# config.py
# Central configuration file for the application.

APP_TITLE = "Smart Video Downloader"
APP_VERSION = "v2.3.5"

# --- Developer Info ---
DEV_NAME = "Adnan Naeem"
DEV_LOCATION = "Lahore"
DEV_EMAIL = "adnaanaeem@gmail.com"
DEV_LINKEDIN = "https://www.linkedin.com/in/adnaanaeem/"
DEV_GITHUB = "https://github.com/adnaanaeem"

# --- URLs ---
# Dependencies (Windows)
YT_DLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

# Dependencies (macOS)
YT_DLP_URL_MAC = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"
FFMPEG_URL_MAC = "https://evermeet.cx/ffmpeg/getrelease/zip"

# Deno (JS runtime yt-dlp needs to solve YouTube's signature/"n" challenge - see
# workers.py DenoDownloadWorker/is_js_runtime_challenge_error). Portable zips, no
# installer, a single root-level binary on both platforms (verified by downloading
# and inspecting both zips directly before relying on this).
DENO_URL_WINDOWS = "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip"
DENO_URL_MAC = "https://github.com/denoland/deno/releases/latest/download/deno-aarch64-apple-darwin.zip"

# App self-updater installer assets (version-agnostic "latest" filenames, same
# ones the README download buttons and release.yml's publish-release job use).
APP_INSTALLER_URL_WINDOWS = "https://github.com/adnaanaeem/smart-video-downloader/releases/latest/download/SmartVideoDownloaderSetup-Windows.exe"
APP_INSTALLER_URL_MAC = "https://github.com/adnaanaeem/smart-video-downloader/releases/latest/download/SmartVideoDownloader-macOS-arm64.dmg"

# APIs
YT_DLP_API_URL = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
APP_API_URL = "https://api.github.com/repos/adnaanaeem/smart-video-downloader/releases/latest"