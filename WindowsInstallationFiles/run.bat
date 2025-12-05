@echo off
echo =====================================================
echo   Audio Transcription Pipeline
echo =====================================================
echo.

REM Try to run the application
audio_transcription_run

REM If command not found, try with py launcher
IF %ERRORLEVEL% EQU 9009 (
    echo.
    echo Command not found in PATH. Trying alternate method...
    py -3.11 -m audio_transcription_pipeline
)

REM Keep window open if there's an error
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo =====================================================
    echo An error occurred. Press any key to exit...
    echo =====================================================
    pause >nul
)