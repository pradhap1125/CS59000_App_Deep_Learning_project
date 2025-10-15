import subprocess
from pathlib import Path
from typing import List, Optional
import shutil
import sys

VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".m4v"}

def _check_ffmpeg() -> None:
    """Raise if ffmpeg is not available on PATH."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found. Please install it and ensure it's on your PATH.\n"
            "macOS: brew install ffmpeg\nWindows: choco install ffmpeg (or download binaries)\nLinux: apt-get install ffmpeg"
        )

def list_videos(src_dir: Path) -> List[Path]:
    return [p for p in src_dir.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]

def extract_audio_to_wav(
    video_path: Path,
    out_dir: Path,
    sample_rate: int = 16000,
    channels: int = 1,
    overwrite: bool = True,
) -> Path:
    """
    Extracts audio as mono PCM WAV at 16 kHz (good default for STT).
    Returns the output .wav path.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{video_path.stem}.wav"
    if out_path.exists() and not overwrite:
        return out_path

 
    cmd = [
        "ffmpeg",
        "-y" if overwrite else "-n",
        "-i", str(video_path),
        "-vn",
        "-ac", str(channels),
        "-ar", str(sample_rate),
        "-acodec", "pcm_s16le",
        str(out_path),
    ]

    # Run ffmpeg; capture minimal stderr for error context
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {video_path.name}:\n{proc.stderr}")
    return out_path

def extract_all_audios(
    src_dir: Path,
    dst_base: Path,
    audios_subdir: str = "audios",
    sample_rate: int = 16000,
    channels: int = 1,
    overwrite: bool = True,
) -> List[Path]:
    """
    Extract audio for all videos in src_dir into dst_base/audios_subdir.
    Returns list of output .wav paths.
    """
    _check_ffmpeg()
    videos = list_videos(src_dir)
    out_dir = dst_base / audios_subdir
    outputs = []
    for i, v in enumerate(videos, start=1):
        print(f"[{i}/{len(videos)}] Extracting audio: {v.name}")
        out = extract_audio_to_wav(
            v, out_dir, sample_rate=sample_rate, channels=channels, overwrite=overwrite
        )
        outputs.append(out)
    print(f"Done. Extracted {len(outputs)} audio file(s) to: {out_dir}")
    return outputs


def extract_audio_as_bytes(
    video_path: Path,
    sample_rate: int = 16000,
    channels: int = 1,
) -> bytes:
    """
    Returns WAV bytes (mono, 16 kHz). Use only for short videos to avoid high memory usage.
    """
    _check_ffmpeg()
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",
        "-ac", str(channels),
        "-ar", str(sample_rate),
        "-acodec", "pcm_s16le",
        "-f", "wav",
        "pipe:1",  
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg (bytes) failed for {video_path.name}:\n{proc.stderr.decode(errors='ignore')}")
    return proc.stdout


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python step2_extract_audio.py <SRC_DIR> <DST_DIR>")
        sys.exit(2)

    src = Path(sys.argv[1]).expanduser().resolve()
    dst = Path(sys.argv[2]).expanduser().resolve()

    if not src.exists() or not src.is_dir():
        raise SystemExit(f"Source not found or not a directory: {src}")

    dst.mkdir(parents=True, exist_ok=True)
    extract_all_audios(src, dst)
