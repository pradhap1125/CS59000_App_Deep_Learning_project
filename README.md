# CS59000_App_Deep_Learning_project

# 📦 macOS Installer Package for the Application

This repository includes a simple installation package designed specifically for macOS users. The downloadable ZIP file contains all necessary components to install and run the application with minimal setup. Once the ZIP is downloaded and extracted, you will find two files: a Python wheel file (`.whl`) and a shell script (`install_and_run.sh`). The shell script installs all required dependencies and launches the application automatically, eliminating the need for users to manually configure their Python environment.

## 📁 What’s Included in the ZIP?

After unzipping the package, you will see: audio_transcription-0.1.0-py3-none-any.whl and install_and_run.sh
The `.whl` file is the packaged application ready for installation, while the shell script is responsible for installing the wheel, fetching all required Python libraries, and starting the application.

## ⚙️ How to Install & Run (macOS Only)

1. **Download the ZIP file** from the repository or release page.  
2. **Unzip** the file to extract its contents.  
3. **Open Terminal** and navigate to the extracted folder, e.g.:

```bash
cd ~/Downloads/your-folder

bash install_and_run.sh
```

If you get a permission denied error while running the script, run:

```bash
chmod +x install_and_run.sh
bash install_and_run.sh
```


