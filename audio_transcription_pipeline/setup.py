import sys
sys.setrecursionlimit(10000)
from setuptools import setup

APP = ['audio_transcription.py'] 
APP_NAME = "AudioTranscriber"
DATA_FILES = []         
OPTIONS = {
    'argv_emulation': True,
    'includes': ["whisper",
        "pydub",
        "moviepy",
        "numpy",
        "torch",
        "soundfile",
        "librosa"],
    'packages': ["requests",
        "torch",
        "pydub",
        "moviepy",
        "whisper"],
}

setup(
    app=APP,
    name=APP_NAME,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
