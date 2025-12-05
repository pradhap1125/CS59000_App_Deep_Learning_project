@echo off
cd /d "%~dp0"
SETLOCAL EnableDelayedExpansion

echo =====================================================
echo   Audio Transcription Pipeline - Setup
echo =====================================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: This script requires Administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Check for Python 3.11
echo Checking for Python 3.11...
py -3.11 --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python 3.11 not found. Installing...
    
    REM Download Python 3.11.5
    curl -L -o python311.exe https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe
    IF !ERRORLEVEL! NEQ 0 (
        echo ERROR: Download failed. Check your internet connection.
        pause
        exit /b 1
    )
    
    REM Install Python 3.11
    echo Installing Python 3.11.5... Please wait...
    python311.exe /quiet InstallAllUsers=1 PrependPath=1
    timeout /t 30 /nobreak >nul
    
    REM Cleanup
    del /q python311.exe
    
    REM Check installation
    py -3.11 --version >nul 2>&1
    IF !ERRORLEVEL! NEQ 0 (
        echo ERROR: Installation failed. Please install manually from python.org
        pause
        exit /b 1
    )
    echo Python 3.11.5 installed successfully.
) ELSE (
    echo Python 3.11 found.
)
echo.

REM Install wheel file
echo Installing audio transcription pipeline...
set WHEEL_FILE=audio_transcription_app-1.0.0-py3-none-any.whl

IF NOT EXIST "!WHEEL_FILE!" (
    echo ERROR: Wheel file not found in current folder: !WHEEL_FILE!
    pause
    exit /b 1
)

py -3.11 -m pip install "!WHEEL_FILE!" --quiet
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Installation failed.
    pause
    exit /b 1
)

echo.
echo Adding Python Scripts folder to PATH...

REM Get the Scripts folder path
for /f "tokens=*" %%i in ('py -3.11 -c "import sys; print(sys.prefix + '\\Scripts')"') do set SCRIPTS_PATH=%%i

REM Add to system PATH
setx /M PATH "%PATH%;%SCRIPTS_PATH%" >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Scripts folder added to PATH: %SCRIPTS_PATH%
) ELSE (
    echo WARNING: Could not add to PATH automatically.
    echo Please add manually: %SCRIPTS_PATH%
)

echo.
echo =====================================================
echo Installation complete!
echo.
echo IMPORTANT: Close and reopen your command prompt
echo Then run: audio_transcription_run
echo =====================================================
pause
ENDLOCAL