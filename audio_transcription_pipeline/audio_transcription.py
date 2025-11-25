import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import sys
import traceback
import datetime
from typing import List, Dict
import os
import platform

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Your modules
from extract_audio import extract_all_audios
# from stt_transcriber import transcribe_folder  # (unused; safe to remove if you want)

# -----------------------------
# Globals
# -----------------------------
# After transcription, this becomes:
# { "<audio_path>": [ {"start": float, "end": float, "text": str}, ... ], ... }
LAST_TRANSCRIPTS: Dict[str, List[dict]] = {}


# -----------------------------
# Helpers for SRT writing
# -----------------------------
def _to_srt_time(seconds: float) -> str:
    """
    Convert seconds (float) to SRT timestamp 'HH:MM:SS,mmm'
    """
    td = datetime.timedelta(seconds=float(seconds))
    s = str(td)
    if "." in s:
        hhmmss, micros = s.split(".")
        millis = str(int(round(int(micros) / 1000.0))).zfill(3)
    else:
        hhmmss, millis = s, "000"
    # Ensure always 'HH:MM:SS' (timedelta may omit hours if 00)
    if len(hhmmss.split(":")) == 2:
        hhmmss = "0:" + hhmmss
    return f"{hhmmss},{millis}"


def save_srt_from_segments(segments: List[dict], srt_path: Path) -> None:
    """
    Write a list of segments [{"start": float, "end": float, "text": str}, ...] to an SRT file.
    """
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    with srt_path.open("w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = _to_srt_time(seg["start"])
            end = _to_srt_time(seg["end"])
            text = (seg.get("text") or "").strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


def save_all_srts_with_timestamps(ts_map: Dict[str, List[dict]], output_dir: Path) -> Dict[str, str]:
    """
    For each audio path in ts_map, write an SRT file in output_dir with the same basename.
    Returns {audio_path_str -> srt_path_str}
    """
    written = {}
    for audio_path_str, segs in ts_map.items():
        audio_path = Path(audio_path_str)
        srt_path = output_dir / audio_path.with_suffix(".srt").name
        save_srt_from_segments(segs, srt_path)
        written[audio_path_str] = str(srt_path)
    return written

def normalizeTranscripts(transcripts: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
    """
    Normalize the text in the transcripts using a pre-trained model.
    """
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    import textwrap

    model_name = "pradhap1125/t5-small-sentence-validator"
    tokenizer = AutoTokenizer.from_pretrained(model_name,use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    normalized_transcripts: Dict[str, List[dict]] = {}
    for audio_path, segments in transcripts.items():
        normalized_segments: List[dict] = []
        for seg in segments:
            raw_text = seg.get("text", "")
            chunks = textwrap.wrap(raw_text, 400)
            normalized_chunks = []
            for ch in chunks:
                input_text = "normalize: " + ch
                inputs = tokenizer(input_text, return_tensors="pt", truncation=True)
                with torch.no_grad():
                    output_ids = model.generate(**inputs, max_length=256, num_beams=5)
                normalized_chunk = tokenizer.decode(output_ids[0], skip_special_tokens=True)
                normalized_chunks.append(normalized_chunk)
            normalized_text = " ".join(normalized_chunks)
            if not normalized_text.strip():
                normalized_text = raw_text
            normalized_seg = {
                "start": seg["start"],
                "end": seg["end"],
                "text": normalized_text
            }
            normalized_segments.append(normalized_seg)
        normalized_transcripts[audio_path] = normalized_segments
    return normalized_transcripts

source_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["HF_HOME"] = os.path.join(source_dir, "hf_cache")
is_windows = platform.system().lower().startswith('win')

def embedTranscriptsToVideo(transcripts) -> None:
    """
    Embed the SRT subtitles into the video using ffmpeg.
    """
    for video_path, srt_path in transcripts.items():
        video_path = Path(video_path)
        srt_path = Path(srt_path)
        output_path = video_path.parent / f"{video_path.stem}_with_subs{video_path.suffix}"
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", f"subtitles={str(srt_path)}",
            "-c:a", "copy",
            str(output_path),
        ]

        # START OF NEW LOGIC
        fixed = []
        for arg in cmd:
            # Convert \ to /
            arg = arg.replace('\\', '/')
            # Handle subtitles filter for proper Windows syntax
            if arg.startswith('subtitles=') and '.srt' in arg:
                path = arg.split('=', 1)[1]
                # Windows only: escape the drive letter colon
                if is_windows and len(path) > 2 and path[1:3] == ':/':
                    path = path[0] + '\\:' + path[2:]
                arg = f"subtitles='{path}'"
            fixed.append(arg)
        proc = subprocess.run(fixed, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # END OF NEW LOGIC

        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg failed to embed subtitles for {video_path.name}:\n{proc.stderr}")



# -----------------------------
# GUI callbacks
# -----------------------------
def browse_source():
    folder = filedialog.askdirectory(title="Select Source Folder (Videos)")
    if folder:
        src_entry.delete(0, tk.END)
        src_entry.insert(0, folder)


def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Folder (Audios)")
    if folder:
        dst_entry.delete(0, tk.END)
        dst_entry.insert(0, folder)


def run_batch_transcription(src: Path, dst: Path, status_callback=None):
    """
    Runs the full audio extraction and transcription pipeline.
    status_callback: function(str) -> None
    """
    def update_status(msg):
        if status_callback:
            status_callback(msg)

    # 1) Extract only audio files
    outputs = extract_all_audios(src, dst)
    out_dir = dst / "transcripts"

    if len(outputs) == 0:
        return {"status": "no_videos", "outputs": []}

    # 2) Transcribe with Faster-Whisper (keep timestamps)
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="auto", compute_type="int8")

    transcripts: Dict[str, List[dict]] = {}
    total = len(outputs)

    for idx, p in enumerate(outputs, start=1):
        update_status(f"🗣️ Transcribing file {i} of {t}..." if 'i' in locals() else f"🗣️ Transcribing file {idx} of {total}...")
        segments, _info = model.transcribe(
            str(p.get("audio")),
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.35,
                min_silence_duration_ms=500,
                speech_pad_ms=400
            )
        )

        seg_list: List[dict] = []
        for seg in segments:
            # seg.start/seg.end are floats; seg.text is a string
            seg_list.append({
                "start": float(seg.start),
                "end": float(seg.end),
                "text": (seg.text or "").strip()
            })
        transcripts[str(p.get("video"))] = seg_list
    normlized_transcripts = normalizeTranscripts(transcripts)
    
    # 3) Write SRT files to transcripts/ in destination
    update_status("📝 Writing .srt files...")
    written_map = save_all_srts_with_timestamps(normlized_transcripts, out_dir)

    update_status("🎬 Embedding subtitles into videos...")
    embedTranscriptsToVideo(written_map)

    return {
        "status": "success",
        "outputs": outputs,
        "transcripts": normlized_transcripts,
        "out_dir": out_dir
    }

def submit():
    src = src_entry.get().strip()
    dst = dst_entry.get().strip()
    if not src or not dst:
        messagebox.showerror("Missing Information", "Please select both source and destination folders.")
        return

    submit_btn.config(state="disabled")
    status_var.set("🔄 Extracting audio files... please wait")

    def run_pipeline():
        try:
            # Define a thread-safe callback
            def on_status(msg):
                root.after(0, lambda: status_var.set(msg))

            result = run_batch_transcription(Path(src), Path(dst), status_callback=on_status)

            if result["status"] == "no_videos":
                root.after(0, lambda: (
                    messagebox.showwarning(
                        "No Videos Found",
                        "No supported video files were found in the source folder.\n\nSupported: .mp4 .mkv .avi .mov .m4v"
                    ),
                    submit_btn.config(state="normal"),
                    status_var.set("⚠️ No videos found.")
                ))
                return

            # Update global
            LAST_TRANSCRIPTS.clear()
            LAST_TRANSCRIPTS.update(result["transcripts"])

            def done():
                status_var.set("✅ Completed successfully!")
                messagebox.showinfo(
                    "Completed",
                    f"Extracted {len(result['outputs'])} audio file(s).\n"
                    f"Transcribed {len(result['transcripts'])} file(s).\n\n"
                    f"SRT files written to:\n{result['out_dir']}\n\n"
                    "Timestamped transcripts stored in variable: LAST_TRANSCRIPTS"
                )
                submit_btn.config(state="normal")
            root.after(0, done)

        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}"
            print(traceback.format_exc(), file=sys.stderr)

            def on_err(msg=err_msg):
                status_var.set("❌ Error encountered. See terminal for details.")
                messagebox.showerror("Error", msg)
                submit_btn.config(state="normal")
            root.after(0, on_err)

    threading.Thread(target=run_pipeline, daemon=True).start()




# -----------------------------
# GUI setup
# -----------------------------
root = tk.Tk()
root.title("Video Transcript Generator")
root.geometry("680x270")
root.resizable(False, False)

heading = tk.Label(root, text="Video Transcript Generator", font=("Arial", 16, "bold"))
heading.grid(row=0, column=0, columnspan=3, pady=(12, 8))

root.grid_columnconfigure(1, weight=1)

# Row 1 - Source
lbl_src = tk.Label(root, text="Source Folder (Videos):", font=("Arial", 11))
lbl_src.grid(row=1, column=0, sticky="w", padx=(20, 8), pady=(8, 4))
src_entry = tk.Entry(root, width=60)
src_entry.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(8, 4))
tk.Button(root, text="Browse", width=10, command=browse_source).grid(row=1, column=2, sticky="e", padx=(0, 20), pady=(8, 4))

# Row 2 - Destination
lbl_dst = tk.Label(root, text="Destination Folder (Audios):", font=("Arial", 11))
lbl_dst.grid(row=2, column=0, sticky="w", padx=(20, 8), pady=(4, 8))
dst_entry = tk.Entry(root, width=60)
dst_entry.grid(row=2, column=1, sticky="ew", padx=(0, 8), pady=(4, 8))
tk.Button(root, text="Browse", width=10, command=browse_destination).grid(row=2, column=2, sticky="e", padx=(0, 20), pady=(4, 8))

# Row 3 - Start button
submit_btn = tk.Button(root, text="Start Process", width=18, font=("Arial", 12, "bold"), command=submit)
submit_btn.grid(row=3, column=0, columnspan=3, pady=(6, 10))

# Row 4 - Status label
status_var = tk.StringVar(value="Idle...")
status_label = tk.Label(root, textvariable=status_var, font=("Arial", 10, "italic"), fg="gray")
status_label.grid(row=4, column=0, columnspan=3, pady=(4, 10))

if __name__ == "__main__":
    # on Windows also helps multiprocessing
    import multiprocessing as mp
    mp.freeze_support()
    root.mainloop()
