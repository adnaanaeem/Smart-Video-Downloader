# Smart Video Downloader

[![Latest Release](https://img.shields.io/github/v/release/adnaanaeem/smart-video-downloader?style=for-the-badge&color=DC2626&label=Latest%20Release)](https://github.com/adnaanaeem/smart-video-downloader/releases/latest)
[![Download for Windows](https://img.shields.io/badge/Download-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/adnaanaeem/smart-video-downloader/releases/latest/download/SmartVideoDownloaderSetup-Windows.exe)
[![Download for macOS](https://img.shields.io/badge/Download-macOS%20(Apple%20Silicon)-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/adnaanaeem/smart-video-downloader/releases/latest/download/SmartVideoDownloader-macOS-arm64.dmg)

![Main Application Window](https://raw.githubusercontent.com/adnaanaeem/smart-video-downloader/main/screenshots/download_queue.png)

A modern, feature-rich desktop application for downloading videos and audio from hundreds of websites. Built with Python and a highly-structured PyQt6 frontend, this application provides a sleek user interface and a robust backend powered by `yt-dlp`.

---

### What's New

*   **v2.2.0 (Current):**
    *   `feat:` **Playlist support** — paste a playlist link to select videos and bulk-download them at a chosen quality.
    *   `feat:` **Cancel & Retry** on downloads — retrying resumes the partial file instead of starting over.
    *   `feat:` Optional **subtitle and thumbnail/metadata embedding** for downloads.
    *   `feat:` A dismissible **clipboard hint** offers to paste a video link you've just copied.
    *   `fix:` A failed download no longer leaves its row stuck on "Queued" — it's re-enabled for a retry.

*   **v2.1.2:**
    *   `feat:` Added a **Language** filter alongside Quality and Format, so videos with multiple audio/dub tracks are easy to narrow down.
    *   `feat:` The app now runs natively on **macOS (Apple Silicon)** as well as Windows, with a proper `.dmg` installer.
    *   `feat:` The app now automatically checks for `yt-dlp` updates on launch and can self-repair a corrupted `yt-dlp`/`ffmpeg` install.
    *   `fix:` Corrected a bug where the bundled `yt-dlp` binary could be shadowed by an unrelated copy elsewhere on the system PATH.
    *   `fix:` Corrected a crash that could occur when a video had audio tracks with no reported bitrate.

*   **v2.1.1:**
    *   `fix:` Corrected a critical bug that caused downloads of high-resolution videos (1080p and above) to have no audio.
    *   `fix:` Resolved several `TypeError` and `AttributeError` crashes related to refactoring.
    *   `fix:` Improved UI consistency and error handling dialogs.

*   **v2.0.0:**
    *   Major architectural overhaul with isolated modules for UI, styling, configuration, and localization.
    *   Added support for hundreds of sites (TikTok, Instagram, etc.).
    *   Implemented an application auto-updater and mandatory dependency downloader for `yt-dlp` and `ffmpeg`.
    *   Added contextual error handling and help buttons.

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
*   **Multi-Language Audio Support:** For videos with multiple audio tracks, you can now choose which language to download.
*   **Quality, Format & Language Filters:** Instantly narrow the formats list down to exactly what you're looking for.
*   **Playlist Support:** Paste a playlist link to select and bulk-download multiple videos at once.
*   **Cancel & Retry:** Cancel an in-progress download or retry a failed one directly from the queue — retrying resumes the partial file rather than starting over.
*   **Subtitle & Metadata Embedding:** Optionally embed subtitles, thumbnail, and metadata into your downloads.
*   **Clipboard Link Detection:** A dismissible hint offers to paste a video link you've just copied.
*   **MP3 Conversion:** Download and convert any video to a high-quality MP3 file.
*   **Private Video Support:** Download age-restricted or members-only content by providing a single, consolidated `cookies.txt` file.
*   **Persistent User Settings:** Remembers your last-used save location and cookies file between sessions.
*   **Cross-Platform:** Runs natively on both Windows and macOS (Apple Silicon).

### Tech Stack

*   **Language:** Python
*   **GUI Framework:** PyQt6
*   **Backend Downloader:** `yt-dlp`
*   **Audio Conversion:** `ffmpeg`
*   **Packaging:** PyInstaller, Inno Setup (Windows), `hdiutil` (macOS)
*   **CI/CD:** GitHub Actions builds and publishes both installers on every release

### Installation

#### Windows

1.  Go to the [**Releases Page**](https://github.com/adnaanaeem/smart-video-downloader/releases/latest) (or use the **Download for Windows** button above).
2.  Download `SmartVideoDownloaderSetup-Windows.exe`.
3.  Run the installer. Windows Defender may show a warning; this is normal for an unsigned installer. Click `More info` -> `Run anyway` to proceed.

#### macOS (Apple Silicon)

1.  Go to the [**Releases Page**](https://github.com/adnaanaeem/smart-video-downloader/releases/latest) (or use the **Download for macOS** button above). Covers any Mac from 2020 onward (M1/M2/M3/M4); Intel support is planned for a future release.
2.  Download `SmartVideoDownloader-macOS-arm64.dmg`, open it, and drag **Smart Video Downloader** into your **Applications** folder.
3.  On first launch, macOS Gatekeeper will likely block the app because it isn't notarized by Apple (that requires a paid Apple Developer account — nothing is wrong with the app itself). If you see a warning like *"Smart Video Downloader" can't be opened* or it's offered to be moved to the Trash, fix it with either method below:
    *   **Option A:** Right-click (or Control-click) the app in Applications → **Open** → click **Open** again in the confirmation dialog. You only need to do this once.
    *   **Option B (newer macOS versions, e.g. Sequoia+):** Open **System Settings → Privacy & Security**, scroll down to the security notice mentioning the app was blocked, and click **Open Anyway**, then confirm once more when prompted.

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