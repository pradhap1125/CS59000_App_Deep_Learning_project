# stt_transcriber.py
from pathlib import Path
from typing import Dict

AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".wma", ".aac", ".opus"}

def _transcribe_with_faster_whisper(audio_path: str, model_size: str) -> str:
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, _info = model.transcribe(audio_path, beam_size=5, vad_filter=True)
    return "".join(seg.text for seg in segments).strip()

def _transcribe_with_openai_whisper(audio_path: str, model_size: str) -> str:
    import whisper  # openai/whisper (local)
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, verbose=False)
    return (result.get("text") or "").strip()

def transcribe_folder(audio_folder: str, model_size: str = "small") -> Dict[str, str]:
    folder = Path(audio_folder)
    if not folder.exists():
        raise FileNotFoundError(f"Audio folder not found: {audio_folder}")

    audio_files = [
        p for p in sorted(folder.glob("*"))
        if p.is_file() and p.suffix.lower() in AUDIO_EXTS
    ]
    if not audio_files:
        return {}

    transcripts: Dict[str, str] = {}

    fw_ok = True
    ow_ok = True
    try:
        import faster_whisper  # noqa: F401
    except Exception:
        fw_ok = False
    try:
        import whisper  # noqa: F401
    except Exception:
        ow_ok = False

    if not fw_ok and not ow_ok:
        raise RuntimeError(
            "No transcription backend available. Install one of:\n"
            "  pip install faster-whisper\n"
            "  OR\n"
            "  pip install -U openai-whisper"
        )

    for p in audio_files:
        apath = str(p.resolve())
        text = ""
        last_err = None

        if fw_ok:
            try:
                text = _transcribe_with_faster_whisper(apath, model_size)
            except Exception as e:
                last_err = e
                text = ""

        if not text and ow_ok:
            try:
                text = _transcribe_with_openai_whisper(apath, model_size)
            except Exception as e:
                last_err = e
                text = ""

        if not text:
            raise RuntimeError(f"Failed to transcribe {apath}: {last_err or 'unknown error'}")

        transcripts[apath] = text

    return transcripts
