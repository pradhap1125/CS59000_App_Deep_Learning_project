# CS59000_App_Deep_Learning_project


# 📦 macOS Installer Package for the Application

This repository provides a native macOS .dmg installer for easy, one-click installation of the application without requiring any manual Python setup.

🔗 Download macOS DMG Installer

👉 https://drive.google.com/file/d/1c1qR9CPVbZF_GmTOthmB_vvPsow55hvD/view?usp=sharing


This repository also includes a simple installation package designed specifically for macOS users. The downloadable ZIP file contains all necessary components to install and run the application with minimal setup. Once the ZIP is downloaded and extracted, you will find two files: a Python wheel file (`.whl`) and a shell script (`install_and_run.sh`). The shell script installs all required dependencies and launches the application automatically, eliminating the need for users to manually configure their Python environment.

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
# 📦 Windows Installer Package for the Application

This repository includes a simple installation package designed specifically for **Windows users**. The downloadable ZIP file contains all necessary components to install and run the application with minimal setup. Once the ZIP is downloaded and extracted, you will find two files: a Python wheel file (`.whl`) and two batch scripts (`setup.bat` and `run.bat`). The batch scripts install all required dependencies and launch the application automatically, eliminating the need for users to manually configure their Python environment.

---

## 📁 What's Included in the ZIP?

After unzipping the package, you will see:
- `audio_transcription-0.1.0-py3-none-any.whl` - The packaged application
- `setup.bat` - Installation script
- `run.bat` - Application launcher

The `.whl` file is the packaged application ready for installation, while `setup.bat` is responsible for installing the wheel and fetching all required Python libraries. The `run.bat` script launches the application after setup is complete.

---

## ⚙️ How to Install & Run (Windows Only)

### 1️⃣ Download the ZIP file
Download `WindowsInstallationFiles.zip` from the `WindowsInstallationFiles` folder repository.

### 2️⃣ Unzip the package
Extract the file to a location of your choice (e.g., `Downloads` or `Desktop`).

### 3️⃣ Run Setup (One-Time Only)

> **⚠️ IMPORTANT:** Run as Administrator

1. **Right-click** on `setup.bat`
2. Select **"Run as administrator"**
3. Click **"Yes"** when prompted by User Account Control (UAC)

Wait for the message: **"Press any key to exit."**

### 4️⃣ Launch the Application

> **⚠️ Run as Administrator**

1. **Right-click** on `run.bat`
2. Select **"Run as administrator"**

The application GUI will launch automatically. 🚀

---


