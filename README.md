# Smart Video Downloader

![App Screenshot](https://i.imgur.com/your_screenshot_url.png)

A modern, feature-rich desktop application for downloading videos and audio from the web. Built with Python and PyQt6, this application provides a sleek user interface and a robust backend powered by `yt-dlp`.

---

### Features

*   **Modern & Intuitive UI:** A clean, dark-themed interface built with PyQt6.
*   **Download Videos & Audio:** Fetch a list of all available video and audio formats.
*   **MP3 Conversion:** Download and convert any video to a high-quality MP3 file.
    *   Includes a smart, automatic downloader for the **FFmpeg** dependency.
*   **Private Video Support:** Download age-restricted or members-only content by providing a `cookies.txt` file.
*   **Auto-Dependency Management:** Automatically detects and offers to download `yt-dlp` and `ffmpeg` if they are missing.
*   **Self-Updating:** Includes a menu option to check for and download the latest version of `yt-dlp`.
*   **Persistent Configuration:** Remembers your last-used save location and cookies file between sessions.
*   **Smart Error Handling:** Provides user-friendly dialogs and specific instructions for common issues like private videos or missing dependencies.

### Tech Stack

*   **Language:** Python
*   **GUI Framework:** PyQt6
*   **Backend Downloader:** `yt-dlp`
*   **Audio Conversion:** `ffmpeg`
*   **Packaging:** PyInstaller, Inno Setup

### Installation

1.  Go to the [**Releases Page**](https://github.com/adnaanaeem/your-repo-name/releases).
2.  Download the `SmartVideoDownloaderSetup.exe` file from the latest release.
3.  Run the installer and follow the on-screen instructions.

### Running from Source

1.  Clone the repository: `git clone https://github.com/adnaanaeem/your-repo-name.git`
2.  Navigate to the project directory: `cd your-repo-name`
3.  Install the required packages: `pip install -r requirements.txt`
4.  Run the application: `python main.py`

---

### Screenshots

*(Add more screenshots here to show off different features, like the download queue or the help dialogs)*

![Screenshot 2](https://i.imgur.com/your_screenshot_url_2.png)
![Screenshot 3](https://i.imgur.com/your_screenshot_url_3.png)