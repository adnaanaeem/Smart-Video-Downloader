# localization.py
# Contains all user-facing strings for easy translation.

STRINGS = {
    # --- Main UI ---
    "APP_TITLE": "Smart Video Downloader",
    "URL_LABEL": "Paste any video link to get started.",
    "URL_PLACEHOLDER": "Paste a link from YouTube, TikTok, Instagram, etc.",
    "FETCH_BUTTON": "Fetch",
    "SUPPORTED_SITES_LABEL": "Supports hundreds of sites, including:",
    "SAVE_LOCATION_LABEL": "Save Location",
    "BROWSE_BUTTON": "Browse",
    "COOKIES_LABEL": "Active Browser Cookies File", # Changed for clarity
    "CLEAR_BUTTON": "Clear",
    "FILTER_LABEL": "📊 Filter Formats",
    "QUALITY_LABEL": "Quality:",
    "FORMAT_LABEL": "Format:",
    "LANGUAGE_LABEL": "Language:",
    "DOWNLOAD_BUTTON": "Download",
    "DOWNLOADS_QUEUE_TITLE": "Downloads Queue",
    "COMPLETED_COUNTER": "{completed} / {total} completed",
    "NO_FORMATS_MATCH": "No formats match selection.",
    "SHOW_MORE_BUTTON": "Show More...",
    "EMBED_SUBS_LABEL": "Embed Subtitles",
    "EMBED_METADATA_LABEL": "Embed Thumbnail && Metadata",
    "CLIPBOARD_HINT_TEXT": "📋 Paste copied link?",
    "CLIP_CHECKBOX_LABEL": "Download Clip Only",
    "CLIP_START_PLACEHOLDER": "Start (mm:ss)",
    "CLIP_END_PLACEHOLDER": "End (mm:ss)",
    "CLIP_DURATION_HINT": "Video length: {duration}",
    "CLIP_ERROR_INVALID_TIME": "Enter valid start/end times (e.g. 1:30), with start before end.",
    "CLIP_NOTE_SUFFIX": " [Clip {start}–{end}]",

    # --- Playlist ---
    "PLAYLIST_PANEL_TITLE": "Playlist Detected",
    "PLAYLIST_ITEM_COUNT": "{count} videos found — select which ones to download.",
    "PLAYLIST_SELECT_ALL": "Select All",
    "PLAYLIST_DESELECT_ALL": "Deselect All",
    "PLAYLIST_QUALITY_LABEL": "Quality:",
    "PLAYLIST_QUALITY_BEST": "Best Quality",
    "PLAYLIST_QUALITY_1080P": "1080p",
    "PLAYLIST_QUALITY_720P": "720p",
    "PLAYLIST_QUALITY_480P": "480p",
    "PLAYLIST_QUALITY_AUDIO": "Audio Only (MP3)",
    "PLAYLIST_DOWNLOAD_SELECTED_BUTTON": "Download Selected",
    "PLAYLIST_ERROR_NONE_SELECTED": "Select at least one video first.",

    # --- Table Content ---
    "TABLE_QUALITY_AUDIO": "Audio",
    "TABLE_FORMAT_MP3": "mp3",
    "TABLE_SIZE_NA": "~",
    "TABLE_NOTE_BEST_AUDIO": "Best Audio Quality",
     "TABLE_NOTE_AUDIO_LANG": "{lang} Audio", # <-- NEW
    "TABLE_NOTE_INCLUDES_AUDIO": "Includes Audio", # <-- NEW
    "MP3_FORMAT_DETAILS": "MP3 (Best Audio)",
    
    # --- Menu ---
    "MENU_BUTTON": "☰ Menu",
    "MENU_CHECK_FOR_UPDATES": "Check for Updates",
    "MENU_ADD_COOKIES": "Set Browser Cookies File", # Changed for clarity
    "MENU_UPDATE_YTDLP": "Update yt-dlp",
    "MENU_HELP": "Help",
    "MENU_ABOUT": "About This App",
    "MENU_DEV_INFO": "Developer Info",
    
    # --- Dialogs: Titles ---
    "DIALOG_TITLE_SETUP": "First-Time Setup",
    "DIALOG_TITLE_DOWNLOADING": "Downloading",
    "DIALOG_TITLE_UPDATE_CHECK": "Checking for Updates",
    "DIALOG_TITLE_SUCCESS": "Success",
    "DIALOG_TITLE_FAILED": "Download Failed",
    "DIALOG_TITLE_UPDATE_AVAILABLE": "Update Available",
    "DIALOG_TITLE_UP_TO_DATE": "Up-to-Date",
    "DIALOG_TITLE_PRIVATE_VIDEO": "Private Video Detected",
    "DIALOG_TITLE_FFMPEG_NOT_FOUND": "FFmpeg Not Found",
    "DIALOG_TITLE_CONFIRM_OVERWRITE": "Confirm Overwrite",
    "DIALOG_TITLE_FULL_DESCRIPTION": "Full Description",
    "DIALOG_TITLE_ERROR_DETAILS": "Error Details",

    # --- Dialogs: Content & Buttons ---
    "SETUP_MISSING_DEPS": "The following essential components are missing:\n\n- {missing_list}\n\nThey must be downloaded to continue.",
    "SETUP_DOWNLOAD_NOW": "Download Now",
    "SETUP_EXIT": "Exit",
    "DEPS_SUCCESS_RESTART": "{component} downloaded successfully!\n\nPlease restart the application for the changes to take effect.",
    "RESTART_BUTTON": "Restart",
    "APP_UPDATE_AVAILABLE": "A new version ({latest_version}) is available!\n\nWould you like to go to the download page?",
    "GO_TO_DOWNLOAD_PAGE": "Go to Download Page",
    "SKIP_THIS_VERSION": "Skip This Version",
    "APP_UP_TO_DATE": "You are running the latest version!\n\nVersion: {app_version}",
    "YTDLP_UPDATE_FAILED": "Could not verify yt-dlp version.",
    "YTDLP_UPDATE_AVAILABLE": "A new version of yt-dlp is available.\n\nCurrent: {local_version}\nLatest: {latest_version}\n\nDownload and restart?",
    "YTDLP_UP_TO_DATE": "You have the latest version of yt-dlp!\nVersion: {local_version}",
    "DOWNLOAD_AND_RESTART_BUTTON": "Download & Restart",
    "YTDLP_CORRUPT_REDOWNLOADING": "The bundled yt-dlp component appears to be corrupted or unreadable.\n\nRe-downloading it now to fix this automatically.",
    "FFMPEG_CORRUPT_REDOWNLOADING": "The bundled FFmpeg component appears to be corrupted or unreadable.\n\nRe-downloading it now to fix this automatically.",
    
    "HELP_CONTENT": (
        "<b>General Usage:</b><br>"
        "1. Paste a video link and click 'Fetch'.<br>"
        "2. Choose your save location.<br>"
        "3. Click 'Download' on the format you want.<br><br>"
        "<b>Downloading Private or Members-Only Videos:</b><br>"
        "This requires a `cookies.txt` file from your browser.<br><br>"
        "<b>Step 1: Install a Browser Extension</b><br>"
        "Go to your browser's extension store (Chrome, Firefox, etc.) and install an extension called <b>'Get cookies.txt LOCALLY'</b>.<br><br>"
        "<b>Step 2: Export a Single Cookies File</b><br>"
        "In your browser, make sure you are logged into any websites you want to download from (like YouTube, Vimeo, etc.). Then, click the extension's icon and 'Export' to save the `cookies.txt` file. This one file will work for all sites you are logged into.<br><br>"
        "<b>Step 3: Load the File in This App</b><br>"
        "Go to <b>Menu -> Set Browser Cookies File</b> and select the `cookies.txt` file you just saved."
    ),

    "PRIVATE_VIDEO_HELP": (
        "This video appears to be private, members-only, or requires a login.<br><br>"
        "<b>To download it, you must provide a `cookies.txt` file from your browser.</b><br><br>"
        "<b>Instructions:</b><br>"
        "1. Go to your browser's extension store (e.g., Chrome Web Store) and install an extension called <b>'Get cookies.txt LOCALLY'</b>.<br>"
        "2. In that browser, make sure you are logged into the website where the video is hosted (e.g., YouTube).<br>"
        "3. Click the extension's icon in your browser toolbar and click 'Export' to save the `cookies.txt` file.<br>"
        "4. In this app, go to <b>Menu -> Set Browser Cookies File</b> and select the file you just saved."
    ),
    
    "FFMPEG_HELP": "<b>MP3 conversion requires FFmpeg.</b><br><br>FFmpeg is a free tool used to convert audio into the MP3 format.<br><br>This application can download it for you automatically. After downloading, you must restart the application.",
    "DOWNLOAD_FFMPEG_BUTTON": "Download FFmpeg",
    "CONFIRM_OVERWRITE_CONTENT": "'{filename}' already exists.\nDo you want to overwrite it?",
    "OVERWRITE_BUTTON": "Overwrite",
    "ABOUT_CONTENT": "A modern video downloader GUI built with PyQt6 and yt-dlp.\n\nVersion: {app_version}",
    "NO_DESCRIPTION": "No description available.",
    "DEV_INFO_NAME": "Name:",
    "DEV_INFO_LOCATION": "Location:",
    "DEV_INFO_SUPPORT": "Support:",
    "DEV_INFO_LINKEDIN": "LinkedIn Profile",
    "DEV_INFO_GITHUB": "GitHub Profile",
    
    # --- Status & Error Messages ---
     "WAITING_STATUS": "Waiting...",
    "QUEUED_STATUS": "Queued",
    "COMPLETED_STATUS": "Completed",
    "FAILED_STATUS": "Failed",
    "CANCELLED_STATUS": "Cancelled",
    "CANCEL_BUTTON": "Cancel",
    "RETRY_BUTTON": "Retry",
    "SHOW_IN_FOLDER_BUTTON": "Show in Folder",
    "ERROR_FETCH_PRIVATE": "Could not fetch video info (it may be private).",
    "ERROR_FETCH_GENERIC": "Could not fetch video info.",
    "ERROR_EMPTY_URL": "URL field cannot be empty.",
    "PRIVATE_VIDEO_TOOLTIP": "This video is private. A cookies file may be required.",
    "ERROR_DETAILS_BUTTON": "Details",
    "ERROR_ADD_COOKIES_BUTTON": "How to Add Cookies", # <-- NEW STRING
    "ERROR_LONG_MESSAGE": "An error occurred. Click 'Details' for the full log.",
    "STATUS_PREPARING_COMPONENTS": "Preparing to download components...",
    "STATUS_DOWNLOADING_YTDLP": "Downloading Core Component (yt-dlp)...",
    "STATUS_DOWNLOADING_YTDLP_PERCENT": "Downloading Core Component (yt-dlp)... {percent}%",
    "STATUS_DOWNLOADING_FFMPEG": "Downloading Audio Component (FFmpeg)...",
    "STATUS_DOWNLOADING_FFMPEG_PERCENT": "Downloading Audio Component (FFmpeg)... {percent}%",
    "STATUS_EXTRACTING_FFMPEG": "Extracting ffmpeg.exe...",
    "SUCCESS_YTDLP_DOWNLOADED": "yt-dlp",
    "SUCCESS_FFMPEG_DOWNLOADED": "FFmpeg",
    "ERROR_YTDLP_DOWNLOAD_FAILED": "Failed to download yt-dlp: {error}",
    "ERROR_FFMPEG_DOWNLOAD_FAILED": "Failed to download FFmpeg: {error}",
    "SUCCESS_DOWNLOAD_COMPLETED": "Download completed!",
    "SUCCESS_MP3_CONVERTED": "MP3 conversion completed!",
    "COMPONENT_YTDLP": "Core downloader (yt-dlp)",
    "COMPONENT_FFMPEG": "Audio converter (FFmpeg)",
}