# Smart Video Downloader

[![Download Installer](https://img.shields.io/badge/Download-Installer-DC2626?style=for-the-badge&logo=download&logoColor=white)](https://github.com/adnaanaeem/smart-video-downloader/releases/download/v1.0.0/SmartVideoDownloaderSetup.exe)

![Main Application Window](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/download_queue.png)

A modern, feature-rich desktop application for downloading videos and audio from the web. Built with Python and PyQt6, this application provides a sleek user interface and a robust backend powered by `yt-dlp`.

---

### Features

*   **Modern & Intuitive UI:** A clean, dark-themed interface built with PyQt6.
*   **Download Videos & Audio:** Fetch a list of all available video and audio formats.
*   **MP3 Conversion:** Download and convert any video to a high-quality MP3 file.
    *   Includes a smart, automatic downloader for the **FFmpeg** dependency.
*   **Private Video Support:** Download age-restricted or members-only content by providing a `cookies.txt` file.
*   **Auto-Dependency Management:** Automatically detects and offers to download `yt-dlp` and `ffmpeg` if they are missing.
*   **Self-Updating `yt-dlp`:** Includes a menu option to check for and download the latest version of `yt-dlp`.
*   **Persistent Configuration:** Remembers your last-used save location and cookies file between sessions.
*   **Smart Error Handling:** Provides user-friendly dialogs and specific instructions for common issues like private videos or missing dependencies.

### Tech Stack

*   **Language:** Python
*   **GUI Framework:** PyQt6
*   **Backend Downloader:** `yt-dlp`
*   **Audio Conversion:** `ffmpeg`
*   **Packaging:** PyInstaller, Inno Setup

### Installation

1.  Go to the [**Releases Page**](https://github.com/adnaanaeem/smart-video-downloader/releases/latest).
2.  Download the `SmartVideoDownloaderSetup.exe` file.
3.  Run the installer and follow the on-screen instructions.

### Running from Source

1.  Clone the repository: `git clone https://github.com/adnaanaeem/smart-video-downloader.git`
2.  Navigate to the project directory: `cd smart-video-downloader`
3.  Install the required packages: `pip install -r requirements.txt`
4.  Run the application: `python main.py`

---

### Screenshots

#### Download Queue
![Main Window](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/main_window.png)

![Download Queue](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/download_queue.png)

#### Private Video Help
![Private Video Help Dialog](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/private_video_help.png)