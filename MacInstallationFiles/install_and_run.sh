#!/bin/bash

# 1. Check for Python
find_python() {
    if command -v python3.11 &> /dev/null && python3.11 -c "import tkinter" &> /dev/null; then
        echo "python3.11"
    elif command -v python3.10 &> /dev/null && python3.10 -c "import tkinter" &> /dev/null; then
        echo "python3.10"
    elif command -v python3.12 &> /dev/null && python3.12 -c "import tkinter" &> /dev/null; then
        echo "python3.12"
    elif command -v python3 &> /dev/null; then
        echo "python3"
    else
        echo ""
    fi
}

PYTHON_CMD=$(find_python)

if [ -z "$PYTHON_CMD" ]; then
    echo "Python 3 is not installed."
    read -p "Do you want to install Python 3? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        OS=$(uname -s)
        if [ "$OS" == "Darwin" ]; then
            if command -v brew &> /dev/null; then
                echo "Installing Python via Homebrew..."
                brew install python
                brew install python-tk
            else
                echo "Error: Homebrew is not installed. Please install Homebrew first: https://brew.sh/"
                exit 1
            fi
        elif [ "$OS" == "Linux" ]; then
             if command -v apt-get &> /dev/null; then
                echo "Installing Python via apt-get..."
                sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-tk
             else
                echo "Error: apt-get not found. Please install Python 3 manually."
                exit 1
             fi
        else
            echo "Error: Unsupported OS. Please install Python 3 manually."
            exit 1
        fi
        
        # Re-check after install
        PYTHON_CMD=$(find_python)
        if [ -z "$PYTHON_CMD" ]; then
             echo "Error: Python installation failed or could not be found."
             exit 1
        fi
    else
        echo "Aborting. Python 3 is required."
        exit 1
    fi
fi

echo "Using Python: $PYTHON_CMD ($(command -v $PYTHON_CMD))"

# Check for Tkinter (GUI library)
if ! $PYTHON_CMD -c "import tkinter" &> /dev/null; then
    echo "Error: 'tkinter' module is missing in $PYTHON_CMD."
    echo "Debug: $(which $PYTHON_CMD)"
    echo ""
    echo "If you installed python via Homebrew, try:"
    echo "  brew install python-tk"
    echo "  brew link --overwrite python-tk"
    echo ""
    echo "If you are using the system Python, install Python from python.org"
    exit 1
fi

# 2. Setup Virtual Environment
VENV_DIR="venv_app"
# If venv exists but uses a different python or is broken, recreate it
if [ -d "$VENV_DIR" ]; then
    if [ ! -f "$VENV_DIR/pyvenv.cfg" ]; then
        rm -rf "$VENV_DIR"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# 3. Activate Virtual Environment
source "$VENV_DIR/bin/activate"

# 4. Install the Wheel
# Find the wheel file in the current directory
WHEEL_FILE=$(ls *.whl 2>/dev/null | head -n 1)

if [ -z "$WHEEL_FILE" ]; then
    echo "Error: No .whl file found in this folder!"
    echo "Please make sure you sent the .whl file along with this script."
    exit 1
fi

echo "Installing App from $WHEEL_FILE..."
pip install "$WHEEL_FILE"

# 5. Check for FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "FFmpeg found in system PATH."
elif [ -f "./ffmpeg" ]; then
    echo "FFmpeg found in current directory."
    export PATH="$PWD:$PATH"
else
    echo "FFmpeg not found. Detecting system..."
    OS=$(uname -s)
    ARCH=$(uname -m)
    
    if [ "$OS" == "Darwin" ]; then
        if [ "$ARCH" == "arm64" ]; then
            echo "Detected macOS (Apple Silicon). Downloading FFmpeg..."
            URL="https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/snapshot/ffmpeg.zip"
        else
            echo "Detected macOS (Intel). Downloading FFmpeg..."
            URL="https://ffmpeg.martin-riedl.de/redirect/latest/macos/amd64/snapshot/ffmpeg.zip"
        fi
        
        curl -L -o ffmpeg.zip "$URL"
        unzip -o ffmpeg.zip
        chmod +x ffmpeg
        rm ffmpeg.zip
        export PATH="$PWD:$PATH"
        
    elif [ "$OS" == "Linux" ]; then
        echo "Detected Linux. Attempting to install via apt..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y ffmpeg
        else
            echo "Warning: apt-get not found. Please install ffmpeg manually."
        fi
    else
        echo "Warning: Unsupported OS ($OS). Please install ffmpeg manually."
    fi
fi

# 6. Run the App
echo "Starting Audio Transcription App..."
audio-transcriber
