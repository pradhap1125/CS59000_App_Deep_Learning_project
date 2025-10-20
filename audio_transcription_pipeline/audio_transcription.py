import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import sys
import traceback

from extract_audio import extract_all_audios
from stt_transcriber import transcribe_folder

LAST_TRANSCRIPTS = {}

# ---------- Browse dialogs ----------

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

# ---------- Main process ----------

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
            # 1️⃣ Extract only audio files
            outputs = extract_all_audios(Path(src), Path(dst))
            out_dir = Path(dst) / "audios"

            if len(outputs) == 0:
                root.after(0, lambda: (
                    messagebox.showwarning(
                        "No Videos Found",
                        "No supported video files were found in the source folder.\n\nSupported: .mp4 .mkv .avi .mov .m4v"
                    ),
                    submit_btn.config(state="normal"),
                    status_var.set("⚠️ No videos found.")
                ))
                return

            # 2️⃣ Transcribe and store ONLY in memory (update status per file)
            from faster_whisper import WhisperModel
            model = WhisperModel("tiny", device="auto", compute_type="int8")
            transcripts = {}

            total = len(outputs)
            for idx, p in enumerate(outputs, start=1):
                root.after(0, lambda i=idx, t=total: status_var.set(f"🗣️ Transcribing file {i} of {t}..."))
                segments, _info = model.transcribe(str(p), beam_size=1)
                text = "".join(seg.text for seg in segments).strip()
                transcripts[str(p)] = text

            LAST_TRANSCRIPTS.clear()
            LAST_TRANSCRIPTS.update(transcripts)

            # 3️⃣ Completion message
            def done():
                status_var.set("✅ Completed successfully!")
                messagebox.showinfo(
                    "Completed ✅",
                    f"Extracted {len(outputs)} audio file(s) to:\n{out_dir}\n\n"
                    f"Transcribed {len(transcripts)} file(s).\n\n"
                    "Transcripts stored in variable: LAST_TRANSCRIPTS"
                )
                root.destroy()

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

# ---------- UI Layout (Grid-based for visible Browse buttons) ----------

root = tk.Tk()
root.title("🎬 Video Transcript Generator")
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

root.mainloop()
