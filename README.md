# Smart Video Downloader v2.0

[![Download Latest Version](https://img.shields.io/badge/Download-Latest%20Version-DC2626?style=for-the-badge&logo=download&logoColor=white)](https://github.com/adnaanaeem/smart-video-downloader/releases/latest/download/SmartVideoDownloaderSetup.exe)

![Main Application Window](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/download_queue.png)

A modern, feature-rich desktop application for downloading videos and audio from hundreds of websites. Built with Python and a highly-structured PyQt6 frontend, this application provides a sleek user interface and a robust backend powered by `yt-dlp`.

---

### What's New in v2.0

Version 2.0 is a complete architectural overhaul, focusing on user experience, expanded functionality, and professional software design patterns.

*   **Expanded Site Support:** Now officially supports hundreds of sites beyond YouTube, including TikTok, Instagram, Facebook, Dailymotion, and more.
*   **Application Auto-Updater:** The app now checks for new versions on startup and provides a simple, non-intrusive prompt to update.
*   **Mandatory Dependency Management:** On first launch, the app now ensures all required components (`yt-dlp`, `ffmpeg`) are present and forces a download if they are missing, guaranteeing a functional state.
*   **Advanced Code Architecture:** The entire codebase has been refactored for maintainability and scalability:
    *   **Separation of Concerns:** UI, workers, styling, configuration, and user-facing text are now isolated in their own modules.
    *   **Centralized Theming:** All colors and fonts are defined in `theme.py` and dynamically injected into the stylesheet.
    *   **Localization-Ready:** All strings are stored in `localization.py`, making future translation simple.
*   **Contextual Error Handling:** Error messages are now more intelligent, providing specific "How-to" buttons for common issues like private videos.

### Core Features

*   **Modern & Intuitive UI:** A clean, dark-themed interface built with PyQt6.
*   **Download Videos & Audio:** Fetch a list of all available video and audio formats.
*   **MP3 Conversion:** Download and convert any video to a high-quality MP3 file.
*   **Private Video Support:** Download age-restricted or members-only content by providing a single, consolidated `cookies.txt` file.
*   **Persistent User Settings:** Remembers your last-used save location and cookies file between sessions.

### Tech Stack

*   **Language:** Python
*   **GUI Framework:** PyQt6
*   **Backend Downloader:** `yt-dlp`
*   **Audio Conversion:** `ffmpeg`
*   **Packaging:** PyInstaller, Inno Setup

### Installation

1.  Go to the [**Releases Page**](https://github.com/adnaanaeem/smart-video-downloader/releases/latest).
2.  Download the `SmartVideoDownloaderSetup-v2.0.0.exe` file.
3.  Run the installer and follow the on-screen instructions.

### Running from Source

1.  Clone the repository: `git clone https://github.com/adnaanaeem/smart-video-downloader.git`
2.  Navigate to the project directory: `cd smart-video-downloader`
3.  Install the required packages: `pip install -r requirements.txt`
4.  Run the application: `python main.py`

---

### Screenshots

#### Main Window
![Mian Window](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/main_window.png)

#### Download Queue
![Download Queue](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/download_queue.png)

#### Private Video Help
![Private Video Help Dialog](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/private_video_help.png)