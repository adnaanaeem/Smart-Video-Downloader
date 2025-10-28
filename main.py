# main.py

import sys
import os
import re
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QScrollArea, QFileDialog, QGraphicsDropShadowEffect, QMenu
)
from PyQt6.QtGui import QColor, QAction, QPixmap, QIcon
from PyQt6.QtCore import QThread, Qt

# --- Local Imports ---
from styles import STYLESHEET
from workers import (
    Spinner, ModalDialog, DeveloperDialog, DownloadItem,
    VersionCheckWorker, YTDlpWorker, FFmpegDownloadWorker, FetchWorker, ThumbnailWorker, DownloadWorker, Mp3DownloadWorker
)

# --- App Configuration ---
APP_TITLE = "Smart Video Downloader"
CONFIG_FILE = "config.json"

# --- HELPER FUNCTION TO FIND BUNDLED FILES ---
def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Main Application Window ---
class SmartVideoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE); self.setWindowIcon(QIcon(resource_path("icon.ico"))); self.setMinimumSize(850, 700)
        self.fetched_data = None; self.download_items = {}; self.downloads_completed = 0; self.downloads_total = 0
        self.ytdlp_dialog = None; self.save_path = ""; self.cookies_path = None; self.ffmpeg_found = False
        self._check_ffmpeg(); self._setup_ui(); self._load_config(); self._check_yt_dlp_on_startup()

    def _setup_ui(self):
        self.central_widget = QWidget(); self.central_widget.setObjectName("centralWidget"); self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self.background_frame = QFrame(self.central_widget); self.background_frame.setObjectName("backgroundFrame")
        self.content_layout = QVBoxLayout(self.background_frame); self.content_layout.setContentsMargins(30, 20, 30, 20); self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_scroll_area = QScrollArea(); main_scroll_area.setObjectName("mainScrollArea"); main_scroll_area.setWidgetResizable(True)
        self.content_panel = QFrame(); self.content_panel.setObjectName("contentPanel")
        self.panel_layout = QVBoxLayout(self.content_panel); self.panel_layout.setContentsMargins(25, 25, 25, 25); self.panel_layout.setSpacing(20); self.panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._create_header(); self._create_url_section(); self._create_error_section(); self._create_video_info_section()
        self._create_save_path_section(); self._create_cookies_section()
        self._create_formats_section(); self._create_downloads_queue(); self.panel_layout.addStretch()
        main_scroll_area.setWidget(self.content_panel); self.content_layout.addWidget(main_scroll_area); self.main_layout.addWidget(self.background_frame)
        self.error_panel.hide(); self.video_info_panel.hide(); self.save_path_panel.hide(); self.cookies_panel.hide(); self.formats_panel.hide(); self.downloads_queue_panel.hide()

    def _create_header(self):
        header = QWidget(); header_layout = QHBoxLayout(header); header_layout.setContentsMargins(0, 0, 0, 15); header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label = QLabel(); icon_png_path = resource_path("icon.png")
        if os.path.exists(icon_png_path): icon_label.setPixmap(QPixmap(icon_png_path))
        icon_label.setFixedSize(36, 36); icon_label.setScaledContents(True)
        shadow = QGraphicsDropShadowEffect(self); shadow.setColor(QColor("#DC2626")); shadow.setBlurRadius(20); shadow.setOffset(0, 0); icon_label.setGraphicsEffect(shadow)
        title_label = QLabel(APP_TITLE); title_label.setObjectName("headerTitle")
        self.menu_button = QPushButton("☰ Menu"); self.menu_button.setObjectName("menuButton"); self.menu_button.setFixedSize(100, 36)
        main_menu = QMenu(self); cookies_action = QAction("Add Cookies for Private Videos", self); cookies_action.triggered.connect(self._on_add_cookies_clicked)
        update_action = QAction("Update yt-dlp", self); update_action.triggered.connect(self._on_update_clicked); help_action = QAction("Help", self); help_action.triggered.connect(self._show_help_dialog)
        about_action = QAction("About This App", self); about_action.triggered.connect(self._show_about_dialog); dev_action = QAction("Developer Info", self); dev_action.triggered.connect(self._show_dev_dialog)
        main_menu.addAction(cookies_action); main_menu.addSeparator(); main_menu.addAction(update_action); main_menu.addAction(help_action); main_menu.addAction(about_action); main_menu.addAction(dev_action); self.menu_button.setMenu(main_menu)
        header_layout.addWidget(icon_label); header_layout.addSpacing(15); header_layout.addWidget(title_label); header_layout.addStretch(); header_layout.addWidget(self.menu_button)
        self.panel_layout.addWidget(header)
    
    def _create_url_section(self):
        url_label = QLabel("Paste a video link to fetch available formats and download."); url_label.setObjectName("urlLabel")
        url_input_container = QFrame(); url_input_container.setObjectName("urlInputContainer"); url_input_layout = QHBoxLayout(url_input_container); url_input_layout.setContentsMargins(10, 2, 2, 2); url_input_layout.setSpacing(10)
        link_icon = QLabel("🔗"); link_icon.setObjectName("linkIcon"); self.url_input = QLineEdit(); self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=..."); self.url_input.setFixedHeight(40)
        self.fetch_button = QPushButton("Fetch"); self.fetch_button.setObjectName("fetchButton"); self.fetch_button.setFixedSize(100, 40); self.fetch_button.clicked.connect(self._on_fetch_clicked); self.spinner = Spinner(); self.spinner.hide()
        url_input_layout.addWidget(link_icon); url_input_layout.addWidget(self.url_input); url_input_layout.addWidget(self.spinner); url_input_layout.addWidget(self.fetch_button)
        self.panel_layout.addWidget(url_label); self.panel_layout.addWidget(url_input_container)

    def _create_error_section(self):
        self.error_panel = QFrame(); self.error_panel.setObjectName("errorPanel"); error_layout = QHBoxLayout(self.error_panel)
        error_icon = QLabel("❌"); error_icon.setObjectName("errorIcon"); self.error_message = QLabel("Error message."); self.error_message.setObjectName("errorMessage")
        error_layout.addWidget(error_icon); error_layout.addWidget(self.error_message, 1); self.panel_layout.addWidget(self.error_panel)

    def _create_video_info_section(self):
        self.video_info_panel = QWidget(); info_layout = QHBoxLayout(self.video_info_panel); info_layout.setContentsMargins(0, 0, 0, 0); info_layout.setSpacing(20)
        self.thumbnail_label = QLabel(); self.thumbnail_label.setObjectName("thumbnail"); self.thumbnail_label.setFixedSize(256, 144); self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_widget = QWidget(); text_layout = QVBoxLayout(text_widget); text_layout.setContentsMargins(0, 0, 0, 0); text_layout.setSpacing(5); text_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.video_title = QLabel("Title"); self.video_title.setObjectName("videoTitle"); self.video_title.setWordWrap(True)
        desc_layout = QHBoxLayout(); desc_layout.setContentsMargins(0,0,0,0); desc_layout.setSpacing(10)
        self.video_description = QLabel("Desc."); self.video_description.setObjectName("videoDescription"); self.video_description.setWordWrap(True); self.video_description.setMaximumHeight(100)
        self.show_more_btn = QPushButton("Show More..."); self.show_more_btn.setObjectName("showMoreButton"); self.show_more_btn.clicked.connect(self._show_full_description)
        desc_layout.addWidget(self.video_description, 1); desc_layout.addWidget(self.show_more_btn, 0, Qt.AlignmentFlag.AlignBottom)
        text_layout.addWidget(self.video_title); text_layout.addLayout(desc_layout); info_layout.addWidget(self.thumbnail_label); info_layout.addWidget(text_widget, 1); self.panel_layout.addWidget(self.video_info_panel)

    def _create_save_path_section(self):
        self.save_path_panel = QWidget(); layout = QVBoxLayout(self.save_path_panel); layout.setContentsMargins(0,0,0,0); layout.setSpacing(5)
        label = QLabel("Save Location"); label.setObjectName("savePathLabel")
        container = QFrame(); container.setObjectName("urlInputContainer"); h_layout = QHBoxLayout(container); h_layout.setContentsMargins(10, 2, 2, 2); h_layout.setSpacing(10)
        self.save_path_input = QLineEdit(); self.save_path_input.setReadOnly(True)
        browse_btn = QPushButton("Browse"); browse_btn.setObjectName("browseButton"); browse_btn.setFixedSize(100, 36); browse_btn.clicked.connect(self._browse_save_path)
        h_layout.addWidget(self.save_path_input); h_layout.addWidget(browse_btn); layout.addWidget(label); layout.addWidget(container); self.panel_layout.addWidget(self.save_path_panel)
    
    def _create_cookies_section(self):
        self.cookies_panel = QWidget(); layout = QVBoxLayout(self.cookies_panel); layout.setContentsMargins(0,0,0,0); layout.setSpacing(5)
        label = QLabel("Active Cookies File"); label.setObjectName("cookiesLabel")
        container = QFrame(); container.setObjectName("urlInputContainer"); h_layout = QHBoxLayout(container); h_layout.setContentsMargins(10, 2, 2, 2); h_layout.setSpacing(10)
        self.cookies_path_input = QLineEdit(); self.cookies_path_input.setReadOnly(True)
        clear_btn = QPushButton("Clear"); clear_btn.setObjectName("clearCookiesButton"); clear_btn.setFixedSize(100, 36); clear_btn.clicked.connect(self._clear_cookies)
        h_layout.addWidget(self.cookies_path_input); h_layout.addWidget(clear_btn); layout.addWidget(label); layout.addWidget(container); self.panel_layout.addWidget(self.cookies_panel)

    def _create_formats_section(self):
        self.formats_panel = QWidget(); formats_layout = QVBoxLayout(self.formats_panel); formats_layout.setContentsMargins(0, 0, 0, 0); formats_layout.setSpacing(15)
        filter_bar = QWidget(); filter_layout = QHBoxLayout(filter_bar); filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_label = QLabel("📊 Filter Formats"); filter_label.setObjectName("filterLabel"); quality_label = QLabel("Quality:"); quality_label.setObjectName("filterDropdownLabel")
        self.quality_filter = QComboBox(); self.quality_filter.currentIndexChanged.connect(self._filter_table); format_label = QLabel("Format:"); format_label.setObjectName("filterDropdownLabel")
        self.format_filter = QComboBox(); self.format_filter.currentIndexChanged.connect(self._filter_table)
        filter_layout.addWidget(filter_label); filter_layout.addStretch(); filter_layout.addWidget(quality_label); filter_layout.addWidget(self.quality_filter); filter_layout.addSpacing(10)
        filter_layout.addWidget(format_label); filter_layout.addWidget(self.format_filter)
        self.formats_table = QTableWidget(); self.formats_table.setColumnCount(5); self.formats_table.setHorizontalHeaderLabels(["Quality", "Format", "Size", "Note", "Action"]); header = self.formats_table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.formats_table.verticalHeader().hide(); self.formats_table.setAlternatingRowColors(True); self.formats_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection); self.formats_table.setFocusPolicy(Qt.FocusPolicy.NoFocus); self.formats_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.empty_filter_label = QLabel("No formats match selection."); self.empty_filter_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.empty_filter_label.setObjectName("emptyFilterLabel"); self.empty_filter_label.hide()
        formats_layout.addWidget(filter_bar); formats_layout.addWidget(self.formats_table); formats_layout.addWidget(self.empty_filter_label); self.panel_layout.addWidget(self.formats_panel)

    def _create_downloads_queue(self):
        self.downloads_queue_panel = QFrame(); self.downloads_queue_panel.setObjectName("downloadsQueuePanel")
        queue_layout = QVBoxLayout(self.downloads_queue_panel); queue_layout.setContentsMargins(0, 0, 0, 0)
        queue_header = QWidget(); header_layout = QHBoxLayout(queue_header); header_layout.setContentsMargins(0, 0, 0, 10)
        queue_title = QLabel("Downloads Queue"); queue_title.setObjectName("queueTitle"); self.progress_counter = QLabel("0 / 0 completed"); self.progress_counter.setObjectName("queueCounter")
        header_layout.addWidget(queue_title); header_layout.addStretch(); header_layout.addWidget(self.progress_counter)
        self.queue_list_layout = QVBoxLayout(); self.queue_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop); self.queue_list_layout.setSpacing(5)
        queue_layout.addWidget(queue_header); queue_layout.addLayout(self.queue_list_layout); self.panel_layout.addWidget(self.downloads_queue_panel)
        
    def _check_ffmpeg(self): self.ffmpeg_found = os.path.exists(resource_path("ffmpeg.exe"))
    def _check_yt_dlp_on_startup(self):
        if not os.path.exists("yt-dlp.exe"):
            dialog = ModalDialog("yt-dlp Not Found","yt-dlp.exe is required.\n\nWould you like to download it automatically?", {"Download": "download", "Exit": "exit"}, self)
            if dialog.exec() and dialog.result == "download": self._start_ytdlp_download()
            else: QApplication.instance().quit()

    def _start_ytdlp_download(self):
        self.ytdlp_dialog = ModalDialog("Downloading yt-dlp", "Please wait...", {}, self); self.ytdlp_dialog.setModal(False); self.ytdlp_dialog.show(); self.setEnabled(False)
        self.ytdlp_thread = QThread(); self.ytdlp_worker = YTDlpWorker(); self.ytdlp_worker.moveToThread(self.ytdlp_thread)
        self.ytdlp_thread.started.connect(self.ytdlp_worker.run); self.ytdlp_worker.signals.ytdlp_progress.connect(self._update_ytdlp_progress)
        self.ytdlp_worker.signals.ytdlp_finished.connect(self._on_dependency_download_finished); self.ytdlp_worker.signals.ytdlp_finished.connect(self.ytdlp_thread.quit)
        self.ytdlp_worker.signals.ytdlp_finished.connect(self.ytdlp_worker.deleteLater); self.ytdlp_thread.finished.connect(self.ytdlp_thread.deleteLater); self.ytdlp_thread.start()

    def _start_ffmpeg_download(self):
        self.ytdlp_dialog = ModalDialog("Downloading FFmpeg", "Please wait...", {}, self); self.ytdlp_dialog.setModal(False); self.ytdlp_dialog.show(); self.setEnabled(False)
        self.ffmpeg_thread = QThread(); self.ffmpeg_worker = FFmpegDownloadWorker(); self.ffmpeg_worker.moveToThread(self.ffmpeg_thread)
        self.ffmpeg_thread.started.connect(self.ffmpeg_worker.run); self.ffmpeg_worker.signals.ytdlp_progress.connect(self._update_ytdlp_progress)
        self.ffmpeg_worker.signals.ytdlp_finished.connect(self._on_dependency_download_finished); self.ffmpeg_worker.signals.ytdlp_finished.connect(self.ffmpeg_thread.quit)
        self.ffmpeg_worker.signals.ytdlp_finished.connect(self.ffmpeg_worker.deleteLater); self.ffmpeg_thread.finished.connect(self.ffmpeg_thread.deleteLater); self.ffmpeg_thread.start()

    def _on_update_clicked(self):
        self.update_dialog = ModalDialog("Checking for updates", "Please wait...", {}, self); self.update_dialog.setModal(False); self.update_dialog.show()
        self.version_thread = QThread(); self.version_worker = VersionCheckWorker(); self.version_worker.moveToThread(self.version_thread)
        self.version_thread.started.connect(self.version_worker.run); self.version_worker.signals.version_checked.connect(self._on_version_checked)
        self.version_worker.signals.version_checked.connect(self.version_thread.quit); self.version_worker.signals.version_checked.connect(self.version_worker.deleteLater)
        self.version_thread.finished.connect(self.version_thread.deleteLater); self.version_thread.start()

    def _on_version_checked(self, local_version, latest_version):
        self.update_dialog.close()
        if local_version == "N/A" or latest_version == "N/A": ModalDialog("Update Check Failed", "Could not verify yt-dlp version.\nPlease check your internet connection.", {"OK": "ok"}, self).exec()
        elif local_version == latest_version: ModalDialog("Up-to-Date", f"You have the latest version of yt-dlp!\n\nVersion: {local_version}", {"OK": "ok"}, self).exec()
        else:
            dialog = ModalDialog("Update Available", f"A new version of yt-dlp is available.\n\nCurrent: {local_version}\nLatest: {latest_version}\n\nWould you like to download it?", {"Download": "download", "Cancel": "cancel"}, self)
            if dialog.exec() and dialog.result == "download": self._start_ytdlp_download()
    
    def _on_add_cookies_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cookies File", "", "Text Files (*.txt);;All Files (*)")
        if file_path: self.cookies_path = file_path; self._save_config(); self._update_cookies_ui()

    def _clear_cookies(self): self.cookies_path = None; self._save_config(); self._update_cookies_ui()
    def _update_cookies_ui(self):
        if self.cookies_path and os.path.exists(self.cookies_path): self.cookies_path_input.setText(os.path.basename(self.cookies_path)); self.cookies_panel.show()
        else: self.cookies_path_input.clear(); self.cookies_panel.hide()

    def _load_config(self):
        default_path = str(Path.home() / "Downloads"); self.save_path = default_path; self.cookies_path = None
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: config = json.load(f); self.save_path = config.get("save_path", default_path); self.cookies_path = config.get("cookies_path", None)
            except (json.JSONDecodeError, IOError): pass
        self.save_path_input.setText(self.save_path); self._update_cookies_ui()

    def _save_config(self):
        with open(CONFIG_FILE, 'w') as f: json.dump({"save_path": self.save_path, "cookies_path": self.cookies_path}, f, indent=4)

    def _browse_save_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder", self.save_path)
        if directory: self.save_path = directory; self.save_path_input.setText(self.save_path); self._save_config()

    def _update_ytdlp_progress(self, message):
        if self.ytdlp_dialog: self.ytdlp_dialog.findChild(QLabel, "modalContentLabel").setText(message)

    def _on_dependency_download_finished(self, success, message):
        if self.ytdlp_dialog: self.ytdlp_dialog.close(); self.setEnabled(True)
        if success: ModalDialog("Success", f"{message}\n\nPlease restart the application for the changes to take effect.", {"OK": "ok"}, self).exec()
        else: ModalDialog("Download Failed", message, {"OK": "ok"}, self).exec(); self.close()

    def _on_fetch_clicked(self):
        url = self.url_input.text().strip();
        if not url: self._show_error("URL field cannot be empty."); return
        self.fetch_button.hide(); self.spinner.show(); self.url_input.setDisabled(True)
        self.error_panel.hide(); self.video_info_panel.hide(); self.formats_panel.hide(); self.save_path_panel.hide(); self.downloads_queue_panel.hide(); self.cookies_panel.hide()
        self.fetch_thread = QThread(); self.fetch_worker = FetchWorker(url, self.cookies_path); self.fetch_worker.moveToThread(self.fetch_thread); self.fetch_thread.started.connect(self.fetch_worker.run)
        self.fetch_worker.signals.finished.connect(self._process_fetch_result); self.fetch_worker.signals.finished.connect(self.fetch_thread.quit); self.fetch_worker.signals.finished.connect(self.fetch_worker.deleteLater)
        self.fetch_thread.finished.connect(self.fetch_thread.deleteLater); self.fetch_thread.start()

    def _process_fetch_result(self, success, data_or_error):
        self.spinner.hide(); self.fetch_button.show(); self.url_input.setDisabled(False)
        if not success: self.handle_fetch_error(data_or_error)
        else:
            self.fetched_data = data_or_error; self._populate_video_data(); self._populate_formats_table()
            self.video_info_panel.show(); self.save_path_panel.show(); self._update_cookies_ui(); self.formats_panel.show()
    
    def handle_fetch_error(self, message):
        msg_lower = str(message).lower()
        if any(keyword in msg_lower for keyword in ["private", "login required", "members only", "subscribers only", "sign in"]):
            self._show_private_video_help(); self._show_error("Could not fetch video info (it may be private).")
        else: self._show_error(message)

    def _populate_video_data(self):
        self.video_title.setText(self.fetched_data.get("title", "N/A")); self.video_description.setText(self.fetched_data.get("description", "No description."))
        thumb_url = self.fetched_data.get('thumbnail')
        if thumb_url:
            self.thumb_thread = QThread(); self.thumb_worker = ThumbnailWorker(thumb_url); self.thumb_worker.moveToThread(self.thumb_thread)
            self.thumb_thread.started.connect(self.thumb_worker.run); self.thumb_worker.signals.thumbnail_loaded.connect(self._set_thumbnail); self.thumb_worker.signals.thumbnail_loaded.connect(self.thumb_thread.quit)
            self.thumb_worker.signals.thumbnail_loaded.connect(self.thumb_worker.deleteLater); self.thumb_thread.finished.connect(self.thumb_thread.deleteLater); self.thumb_thread.start()

    def _set_thumbnail(self, pixmap):
        self.thumbnail_label.setPixmap(pixmap.scaled(self.thumbnail_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _populate_formats_table(self):
        formats = self.fetched_data.get("formats", []); self.formats_table.setRowCount(0); qualities = set(); fmts = set()
        video_formats = []; audio_formats = []
        def sort_key(f): return f.get('height', 0) if f.get('height') is not None else 0
        for fmt in sorted(formats, key=sort_key, reverse=True):
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none': video_formats.append(fmt)
            elif fmt.get('vcodec') == 'none': audio_formats.append(fmt)

        for fmt in video_formats:
            row = self.formats_table.rowCount(); self.formats_table.insertRow(row); quality = f"{fmt.get('height', 'Video')}p"
            size_str = f"{fmt['filesize_approx'] / (1024*1024):.2f} MB" if fmt.get('filesize_approx') else "N/A"
            qualities.add(quality); fmts.add(fmt.get('ext', 'N/A'))
            self.formats_table.setItem(row, 0, QTableWidgetItem(quality)); self.formats_table.setItem(row, 1, QTableWidgetItem(fmt.get('ext', 'N/A'))); self.formats_table.setItem(row, 2, QTableWidgetItem(size_str)); self.formats_table.setItem(row, 3, QTableWidgetItem(fmt.get('format_note', 'N/A')))
            download_btn = QPushButton("Download"); download_btn.setObjectName("downloadButton"); download_btn.clicked.connect(lambda _, r=row, fid=fmt['format_id']: self._on_download_clicked(r, fid))
            container = QWidget(); layout = QHBoxLayout(container); layout.setContentsMargins(0,0,0,0); layout.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(download_btn)
            self.formats_table.setCellWidget(row, 4, container); self.formats_table.setRowHeight(row, download_btn.sizeHint().height() + 20)

        mp3_row = self.formats_table.rowCount(); self.formats_table.insertRow(mp3_row)
        self.formats_table.setItem(mp3_row, 0, QTableWidgetItem("Audio")); self.formats_table.setItem(mp3_row, 1, QTableWidgetItem("mp3"))
        self.formats_table.setItem(mp3_row, 2, QTableWidgetItem("~")); self.formats_table.setItem(mp3_row, 3, QTableWidgetItem("Best Audio Quality"))
        mp3_widget = QWidget(); mp3_layout = QHBoxLayout(mp3_widget); mp3_layout.setContentsMargins(0,0,0,0); mp3_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mp3_btn = QPushButton("Download"); mp3_btn.setObjectName("downloadButton")
        if self.ffmpeg_found:
            mp3_btn.clicked.connect(lambda _, r=mp3_row: self._on_mp3_row_clicked(r))
        else:
            mp3_btn.setDisabled(True); mp3_btn.setToolTip("FFmpeg not found. Click '?' for help.")
        mp3_layout.addWidget(mp3_btn)
        if not self.ffmpeg_found:
            mp3_help = QPushButton("❓"); mp3_help.setObjectName("mp3HelpButton"); mp3_help.clicked.connect(self._show_ffmpeg_help); mp3_layout.addWidget(mp3_help)
        self.formats_table.setCellWidget(mp3_row, 4, mp3_widget); self.formats_table.setRowHeight(mp3_row, mp3_btn.sizeHint().height() + 20)
        qualities.add("Audio"); fmts.add("mp3")

        for fmt in audio_formats:
            row = self.formats_table.rowCount(); self.formats_table.insertRow(row); quality = "Audio"
            size_str = f"{fmt['filesize_approx'] / (1024*1024):.2f} MB" if fmt.get('filesize_approx') else "N/A"
            qualities.add(quality); fmts.add(fmt.get('ext', 'N/A'))
            self.formats_table.setItem(row, 0, QTableWidgetItem(quality)); self.formats_table.setItem(row, 1, QTableWidgetItem(fmt.get('ext', 'N/A'))); self.formats_table.setItem(row, 2, QTableWidgetItem(size_str)); self.formats_table.setItem(row, 3, QTableWidgetItem(fmt.get('format_note', 'N/A')))
            download_btn = QPushButton("Download"); download_btn.setObjectName("downloadButton"); download_btn.clicked.connect(lambda _, r=row, fid=fmt['format_id']: self._on_download_clicked(r, fid))
            container = QWidget(); layout = QHBoxLayout(container); layout.setContentsMargins(0,0,0,0); layout.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(download_btn)
            self.formats_table.setCellWidget(row, 4, container); self.formats_table.setRowHeight(row, download_btn.sizeHint().height() + 20)
        
        self.quality_filter.clear(); self.format_filter.clear(); self.quality_filter.addItems(["All"] + sorted(list(qualities), key=lambda x: -int(x.replace('p','').replace('Audio','0')))); self.format_filter.addItems(["All"] + sorted(list(fmts)))
        self._filter_table()

    def _filter_table(self):
        quality = self.quality_filter.currentText(); fmt = self.format_filter.currentText(); rows_visible = 0
        for i in range(self.formats_table.rowCount()):
            q_match = (quality == "All" or self.formats_table.item(i, 0).text() == quality); f_match = (fmt == "All" or self.formats_table.item(i, 1).text() == fmt)
            if q_match and f_match: self.formats_table.setRowHidden(i, False); rows_visible += 1
            else: self.formats_table.setRowHidden(i, True)
        self.empty_filter_label.setVisible(rows_visible == 0); self.formats_table.setVisible(rows_visible > 0)

    def _on_download_clicked(self, row, format_id):
        quality = self.formats_table.item(row, 0).text(); safe_title = re.sub(r'[\\/*?:"<>|]', "", self.fetched_data['title'])
        filename = f"{safe_title} - {quality}.mp4"; full_path = os.path.join(self.save_path, filename); proceed = not os.path.exists(full_path)
        if not proceed:
            dialog = ModalDialog("Confirm Overwrite", f"'{filename}' already exists.\nDo you want to overwrite it?", {"Overwrite": "overwrite", "Cancel": "cancel"}, self)
            if dialog.exec() and dialog.result == "overwrite": proceed = True
        if proceed: self._start_download_worker(row, format_id, full_path)

    def _start_download_worker(self, row, format_id, save_path):
        btn = self.formats_table.cellWidget(row, 4).findChild(QPushButton); btn.setText("Queued"); btn.setDisabled(True)
        if not self.downloads_queue_panel.isVisible(): self.downloads_queue_panel.show()
        self.downloads_total += 1; self._update_queue_counter()
        quality = self.formats_table.item(row, 0).text(); fmt = self.formats_table.item(row, 1).text(); unique_id = f"{self.fetched_data['id']}-{format_id}"
        item_widget = DownloadItem(self.fetched_data['title'], f"{quality} ({fmt})"); self.queue_list_layout.addWidget(item_widget); self.download_items[unique_id] = item_widget
        self.dl_thread = QThread(); self.dl_worker = DownloadWorker(self.fetched_data['webpage_url'], format_id, save_path, unique_id, self.cookies_path); self.dl_worker.moveToThread(self.dl_thread); self.dl_thread.started.connect(self.dl_worker.run)
        self.dl_worker.signals.progress.connect(self._update_download_progress); self.dl_worker.signals.download_finished.connect(self._on_download_finished)
        self.dl_worker.signals.download_finished.connect(self.dl_thread.quit); self.dl_worker.signals.download_finished.connect(self.dl_worker.deleteLater)
        self.dl_thread.finished.connect(self.dl_thread.deleteLater); self.dl_thread.start()

    def _on_mp3_row_clicked(self, row):
        safe_title = re.sub(r'[\\/*?:"<>|]', "", self.fetched_data['title']); filename = f"{safe_title}.mp3"; full_path = os.path.join(self.save_path, filename); proceed = not os.path.exists(full_path)
        if not proceed:
            dialog = ModalDialog("Confirm Overwrite", f"'{filename}' already exists.\nDo you want to overwrite it?", {"Overwrite": "overwrite", "Cancel": "cancel"}, self)
            if dialog.exec() and dialog.result == "overwrite": proceed = True
        if proceed:
            btn = self.formats_table.cellWidget(row, 4).findChild(QPushButton); btn.setText("Queued"); btn.setDisabled(True)
            unique_id = f"{self.fetched_data['id']}-mp3"
            if not self.downloads_queue_panel.isVisible(): self.downloads_queue_panel.show()
            self.downloads_total += 1; self._update_queue_counter()
            item_widget = DownloadItem(self.fetched_data['title'], "MP3 (Best Audio)"); self.queue_list_layout.addWidget(item_widget); self.download_items[unique_id] = item_widget
            self.mp3_thread = QThread(); self.mp3_worker = Mp3DownloadWorker(self.fetched_data['webpage_url'], full_path, unique_id, self.cookies_path); self.mp3_worker.moveToThread(self.mp3_thread); self.mp3_thread.started.connect(self.mp3_worker.run)
            self.mp3_worker.signals.progress.connect(self._update_download_progress); self.mp3_worker.signals.download_finished.connect(self._on_download_finished)
            self.mp3_worker.signals.download_finished.connect(self.mp3_thread.quit); self.mp3_worker.signals.download_finished.connect(self.mp3_worker.deleteLater)
            self.mp3_thread.finished.connect(self.mp3_thread.deleteLater); self.mp3_thread.start()

    def _update_download_progress(self, unique_id, percentage):
        if unique_id in self.download_items: item = self.download_items[unique_id]; item.progress_bar.setValue(percentage); item.percentage_label.setText(f"{percentage}%")

    def _on_download_finished(self, unique_id, success, message):
        if unique_id in self.download_items:
            item = self.download_items[unique_id]
            if success: self.downloads_completed += 1; item.percentage_label.setText("Completed"); item.progress_bar.setValue(100); item.progress_bar.setProperty("status", "completed")
            else:
                msg_lower = message.lower()
                if any(keyword in msg_lower for keyword in ["private", "login", "members only", "subscribers", "sign in"]): self._show_private_video_help(); item.title_label.setToolTip("This video is private. A cookies file may be required.")
                else: item.title_label.setToolTip(message)
                item.percentage_label.setText("Failed"); item.progress_bar.setProperty("status", "failed")
            item.progress_bar.style().unpolish(item.progress_bar); item.progress_bar.style().polish(item.progress_bar)
        self._update_queue_counter()
        
    def _update_queue_counter(self): self.progress_counter.setText(f"{self.downloads_completed} / {self.downloads_total} completed")
    def _show_error(self, message): self.error_message.setText(str(message)); self.error_panel.show()
    def _show_full_description(self):
        if self.fetched_data: dialog = ModalDialog("Full Description", self.fetched_data.get("description", "No description available."), {"Close": "close"}, True, self); dialog.exec()
    def _show_about_dialog(self): ModalDialog("About This App", "A modern video downloader GUI built with PyQt6 and yt-dlp.", {"OK": "ok"}, self).exec()
    def _show_help_dialog(self):
        help_text = ("<b>General Usage:</b><br>1. Paste a video link and click 'Fetch'.<br>2. Choose your save location.<br>3. Click 'Download' on the format you want.<br><br><b>Downloading Private Videos:</b><br>1. Use a browser extension (like 'Get cookies.txt LOCALLY') to export a <b>cookies.txt</b> file from the video site after you log in.<br>2. In this app, go to <b>Menu -> Add Cookies...</b> and select that file.<br>3. Now you can fetch and download private/members-only content.")
        ModalDialog("Help", help_text, {"OK": "ok"}, is_scrollable=True, parent=self).exec()
    def _show_private_video_help(self):
        help_text = ("This video appears to be private or for members only.<br><br><b>To download it, you must provide a cookies file.</b><br><br><b>Instructions:</b><br>1. Go to your browser's extension store (Chrome, Firefox, etc).<br>2. Search for and install an extension called <b>'Get cookies.txt LOCALLY'</b>.<br>3. Go to the video website (e.g., YouTube) and log into your account.<br>4. Click the extension's icon and 'Export' to save the `cookies.txt` file.<br>5. In this app, go to <b>Menu -> Add Cookies...</b> and select the file you just saved.")
        ModalDialog("Private Video Detected", help_text, {"OK": "ok"}, is_scrollable=True, parent=self).exec()
    def _show_ffmpeg_help(self):
        help_text = ("<b>MP3 conversion requires FFmpeg.</b><br><br>FFmpeg is a free tool used to convert audio into the MP3 format.<br><br>This application can download it for you automatically. After downloading, you must restart the application for the changes to take effect.")
        dialog = ModalDialog("FFmpeg Not Found", help_text, {"Download FFmpeg": "download", "Cancel": "cancel"}, parent=self)
        if dialog.exec() and dialog.result == "download": self._start_ffmpeg_download()
    def _show_dev_dialog(self): DeveloperDialog(self).exec()
    def closeEvent(self, event): self._save_config(); super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = SmartVideoDownloader()
    window.show()
    sys.exit(app.exec())