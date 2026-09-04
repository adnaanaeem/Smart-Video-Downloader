# main.py

import sys
import os
import re
import json
import webbrowser
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QComboBox, QCheckBox, QHeaderView, QScrollArea, QFileDialog, QGraphicsDropShadowEffect, QMenu
)
from PyQt6.QtGui import QColor, QAction, QPixmap, QIcon
from PyQt6.QtCore import QThread, Qt, QStandardPaths, QEvent

# --- Local Imports ---
import config
from theme import THEME
from localization import STRINGS
from styles import generate_stylesheet
from workers import (
    Spinner, ModalDialog, DeveloperDialog, DownloadItem,
    VersionCheckWorker, FFmpegHealthCheckWorker, AppUpdateCheckWorker, YTDlpWorker, FFmpegDownloadWorker,
    FetchWorker, PlaylistProbeWorker, ThumbnailWorker, DownloadWorker, Mp3DownloadWorker,
    YTDLP_PATH, FFMPEG_PATH
)

# --- HELPER FUNCTIONS ---
def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_settings_path():
    app_data_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    os.makedirs(app_data_path, exist_ok=True)
    return os.path.join(app_data_path, "settings.json")

# --- Main Application Window ---
class SmartVideoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config.APP_TITLE} {config.APP_VERSION}"); self.setWindowIcon(QIcon(resource_path("icon.ico"))); self.setMinimumSize(850, 700)
        self.fetched_data = None; self.download_items = {}; self.downloads_completed = 0; self.downloads_total = 0
        self.dependency_dialog = None; self.save_path = ""; self.cookies_path = None
        self.ffmpeg_found = os.path.exists(FFMPEG_PATH); self.ytdlp_found = os.path.exists(YTDLP_PATH)
        self.app_update_thread = None; self.version_thread = None; self.ffmpeg_health_thread = None
        self.download_source_buttons = {}; self.download_requests = {}; self.active_workers = {}; self.active_threads = []
        self.playlist_entries = []; self.playlist_checkboxes = []
        self.last_clipboard_hint_text = None; self._startup_clipboard_checked = False
        self._setup_ui(); 
        self._load_settings();
        self.is_updating_ytdlp = False
        self.check_dependencies()

    def _setup_ui(self):
        self.central_widget = QWidget(); self.central_widget.setObjectName("centralWidget"); self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self.background_frame = QFrame(self.central_widget); self.background_frame.setObjectName("backgroundFrame")
        self.content_layout = QVBoxLayout(self.background_frame); self.content_layout.setContentsMargins(30, 20, 30, 20); self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_scroll_area = QScrollArea(); main_scroll_area.setObjectName("mainScrollArea"); main_scroll_area.setWidgetResizable(True)
        self.content_panel = QFrame(); self.content_panel.setObjectName("contentPanel")
        self.panel_layout = QVBoxLayout(self.content_panel); self.panel_layout.setContentsMargins(25, 25, 25, 25); self.panel_layout.setSpacing(20); self.panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._create_header(); self._create_url_section(); self._create_supported_sites_section(); self._create_error_section(); self._create_video_info_section()
        self._create_playlist_section()
        self._create_save_path_section(); self._create_cookies_section(); self._create_formats_section(); self._create_downloads_queue(); self.panel_layout.addStretch()
        main_scroll_area.setWidget(self.content_panel); self.content_layout.addWidget(main_scroll_area); self.main_layout.addWidget(self.background_frame)
        self.error_panel.hide(); self.video_info_panel.hide(); self.playlist_panel.hide(); self.save_path_panel.hide(); self.cookies_panel.hide(); self.formats_panel.hide(); self.downloads_queue_panel.hide()

    def _create_header(self):
        header = QWidget(); header_layout = QHBoxLayout(header); header_layout.setContentsMargins(0, 0, 0, 15); header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label = QLabel(); icon_png_path = resource_path("icon.png")
        if os.path.exists(icon_png_path): icon_label.setPixmap(QPixmap(icon_png_path))
        icon_label.setFixedSize(36, 36); icon_label.setScaledContents(True)
        shadow = QGraphicsDropShadowEffect(self); shadow.setColor(QColor(THEME["PRIMARY_ACCENT"])); shadow.setBlurRadius(20); shadow.setOffset(0, 0); icon_label.setGraphicsEffect(shadow)
        title_label = QLabel(config.APP_TITLE); title_label.setObjectName("headerTitle")
        self.menu_button = QPushButton(STRINGS["MENU_BUTTON"]); self.menu_button.setObjectName("menuButton"); self.menu_button.setFixedSize(100, 36)
        main_menu = QMenu(self); app_update_action = QAction(STRINGS["MENU_CHECK_FOR_UPDATES"], self); app_update_action.triggered.connect(self._check_for_app_updates)
        cookies_action = QAction(STRINGS["MENU_ADD_COOKIES"], self); cookies_action.triggered.connect(self._on_add_cookies_clicked)
        ytdlp_update_action = QAction(STRINGS["MENU_UPDATE_YTDLP"], self); ytdlp_update_action.triggered.connect(self._on_ytdlp_update_clicked)
        help_action = QAction(STRINGS["MENU_HELP"], self); help_action.triggered.connect(self._show_help_dialog); about_action = QAction(STRINGS["MENU_ABOUT"], self); about_action.triggered.connect(self._show_about_dialog)
        dev_action = QAction(STRINGS["MENU_DEV_INFO"], self); dev_action.triggered.connect(self._show_dev_dialog)
        main_menu.addAction(app_update_action); main_menu.addSeparator(); main_menu.addAction(cookies_action); main_menu.addSeparator(); main_menu.addAction(ytdlp_update_action)
        main_menu.addAction(help_action); main_menu.addAction(about_action); main_menu.addAction(dev_action); self.menu_button.setMenu(main_menu)
        header_layout.addWidget(icon_label); header_layout.addSpacing(15); header_layout.addWidget(title_label); header_layout.addStretch(); header_layout.addWidget(self.menu_button)
        self.panel_layout.addWidget(header)
    
    def _create_url_section(self):
        url_label = QLabel(STRINGS["URL_LABEL"]); url_label.setObjectName("urlLabel")
        url_input_container = QFrame(); url_input_container.setObjectName("urlInputContainer"); url_input_layout = QHBoxLayout(url_input_container); url_input_layout.setContentsMargins(10, 2, 2, 2); url_input_layout.setSpacing(10)
        link_icon = QLabel("🔗"); link_icon.setObjectName("linkIcon"); self.url_input = QLineEdit(); self.url_input.setPlaceholderText(STRINGS["URL_PLACEHOLDER"]); self.url_input.setFixedHeight(40)
        self.url_input.textEdited.connect(self._on_url_input_edited)
        self.fetch_button = QPushButton(STRINGS["FETCH_BUTTON"]); self.fetch_button.setObjectName("fetchButton"); self.fetch_button.setFixedSize(100, 40); self.fetch_button.clicked.connect(self._on_fetch_clicked); self.spinner = Spinner(); self.spinner.hide()
        url_input_layout.addWidget(link_icon); url_input_layout.addWidget(self.url_input); url_input_layout.addWidget(self.spinner); url_input_layout.addWidget(self.fetch_button)
        self.clipboard_hint = QPushButton(STRINGS["CLIPBOARD_HINT_TEXT"]); self.clipboard_hint.setObjectName("clipboardHintButton"); self.clipboard_hint.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clipboard_hint.clicked.connect(self._on_clipboard_hint_clicked); self.clipboard_hint.hide()
        self.panel_layout.addWidget(url_label); self.panel_layout.addWidget(url_input_container); self.panel_layout.addWidget(self.clipboard_hint)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.ActivationChange and self.isActiveWindow():
            self._check_clipboard_for_link()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._startup_clipboard_checked:
            self._startup_clipboard_checked = True
            self._check_clipboard_for_link()

    def _check_clipboard_for_link(self):
        text = QApplication.clipboard().text().strip()
        if not text or not re.match(r'^https?://\S+$', text) or text == self.url_input.text().strip() or text == self.last_clipboard_hint_text:
            self.clipboard_hint.hide(); return
        self._pending_clipboard_link = text
        self.clipboard_hint.show()

    def _on_clipboard_hint_clicked(self):
        self.url_input.setText(self._pending_clipboard_link)
        self.last_clipboard_hint_text = self._pending_clipboard_link
        self.clipboard_hint.hide()

    def _on_url_input_edited(self):
        if self.clipboard_hint.isVisible():
            self.last_clipboard_hint_text = getattr(self, '_pending_clipboard_link', None)
            self.clipboard_hint.hide()

    def _create_supported_sites_section(self):
        sites_label = QLabel(STRINGS["SUPPORTED_SITES_LABEL"]); sites_label.setObjectName("urlLabel"); sites_widget = QWidget(); sites_layout = QHBoxLayout(sites_widget)
        sites_layout.setContentsMargins(0, 5, 0, 0); sites_layout.setAlignment(Qt.AlignmentFlag.AlignCenter); sites_layout.setSpacing(15)
        supported = ["YouTube", "TikTok", "Instagram", "Facebook", "Vimeo", "Dailymotion"]
        for i, site in enumerate(supported):
            label = QLabel(site); label.setStyleSheet(f"color: {THEME['TEXT_SECONDARY']}; font-weight: bold; font-size: 13px;"); sites_layout.addWidget(label)
            if i < len(supported) - 1: separator = QLabel("•"); separator.setStyleSheet(f"color: {THEME['BORDER_TERTIARY']}; font-weight: bold;"); sites_layout.addWidget(separator)
        self.panel_layout.addWidget(sites_label); self.panel_layout.addWidget(sites_widget)

    def _create_error_section(self):
        self.error_panel = QFrame(); self.error_panel.setObjectName("errorPanel"); error_layout = QVBoxLayout(self.error_panel)
        top_layout = QHBoxLayout(); error_icon = QLabel("❌"); error_icon.setObjectName("errorIcon"); self.error_message_label = QLabel()
        self.error_message_label.setObjectName("errorMessage"); top_layout.addWidget(error_icon); top_layout.addWidget(self.error_message_label, 1)
        self.error_button_widget = QWidget(); self.error_button_layout = QHBoxLayout(self.error_button_widget)
        self.error_button_layout.setContentsMargins(0, 5, 0, 0)
        self.error_button_widget.hide()
        error_layout.addLayout(top_layout); error_layout.addWidget(self.error_button_widget)
        self.panel_layout.addWidget(self.error_panel)

    def _create_video_info_section(self):
        self.video_info_panel = QWidget(); info_layout = QHBoxLayout(self.video_info_panel); info_layout.setContentsMargins(0, 0, 0, 0); info_layout.setSpacing(20)
        self.thumbnail_label = QLabel(); self.thumbnail_label.setObjectName("thumbnail"); self.thumbnail_label.setFixedSize(256, 144); self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_widget = QWidget(); text_layout = QVBoxLayout(text_widget); text_layout.setContentsMargins(0, 0, 0, 0); text_layout.setSpacing(5); text_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.video_title = QLabel(); self.video_title.setObjectName("videoTitle"); self.video_title.setWordWrap(True)
        desc_layout = QHBoxLayout(); desc_layout.setContentsMargins(0,0,0,0); desc_layout.setSpacing(10)
        self.video_description = QLabel(); self.video_description.setObjectName("videoDescription"); self.video_description.setWordWrap(True); self.video_description.setMaximumHeight(100)
        self.show_more_btn = QPushButton(STRINGS["SHOW_MORE_BUTTON"]); self.show_more_btn.setObjectName("showMoreButton"); self.show_more_btn.clicked.connect(self._show_full_description)
        desc_layout.addWidget(self.video_description, 1); desc_layout.addWidget(self.show_more_btn, 0, Qt.AlignmentFlag.AlignBottom)
        text_layout.addWidget(self.video_title); text_layout.addLayout(desc_layout); info_layout.addWidget(self.thumbnail_label); info_layout.addWidget(text_widget, 1); self.panel_layout.addWidget(self.video_info_panel)

    def _create_playlist_section(self):
        self.playlist_panel = QWidget(); layout = QVBoxLayout(self.playlist_panel); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(10)
        header_row = QHBoxLayout(); title_label = QLabel(STRINGS["PLAYLIST_PANEL_TITLE"]); title_label.setObjectName("videoTitle")
        self.playlist_count_label = QLabel(""); self.playlist_count_label.setObjectName("savePathLabel")
        header_row.addWidget(title_label); header_row.addStretch(); header_row.addWidget(self.playlist_count_label)

        select_row = QHBoxLayout()
        select_all_btn = QPushButton(STRINGS["PLAYLIST_SELECT_ALL"]); select_all_btn.setObjectName("browseButton"); select_all_btn.clicked.connect(lambda: self._set_all_playlist_checkboxes(True))
        deselect_all_btn = QPushButton(STRINGS["PLAYLIST_DESELECT_ALL"]); deselect_all_btn.setObjectName("browseButton"); deselect_all_btn.clicked.connect(lambda: self._set_all_playlist_checkboxes(False))
        select_row.addWidget(select_all_btn); select_row.addWidget(deselect_all_btn); select_row.addStretch()

        self.playlist_scroll = QScrollArea(); self.playlist_scroll.setWidgetResizable(True); self.playlist_scroll.setMaximumHeight(240)
        self.playlist_list_widget = QWidget(); self.playlist_list_layout = QVBoxLayout(self.playlist_list_widget); self.playlist_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop); self.playlist_list_layout.setSpacing(4)
        self.playlist_scroll.setWidget(self.playlist_list_widget)

        footer_row = QHBoxLayout()
        quality_label = QLabel(STRINGS["PLAYLIST_QUALITY_LABEL"]); quality_label.setObjectName("filterDropdownLabel")
        self.playlist_quality_combo = QComboBox()
        self.playlist_quality_combo.addItems([STRINGS["PLAYLIST_QUALITY_BEST"], STRINGS["PLAYLIST_QUALITY_1080P"], STRINGS["PLAYLIST_QUALITY_720P"], STRINGS["PLAYLIST_QUALITY_480P"], STRINGS["PLAYLIST_QUALITY_AUDIO"]])
        self.playlist_download_btn = QPushButton(STRINGS["PLAYLIST_DOWNLOAD_SELECTED_BUTTON"]); self.playlist_download_btn.setObjectName("fetchButton"); self.playlist_download_btn.clicked.connect(self._on_playlist_download_clicked)
        footer_row.addWidget(quality_label); footer_row.addWidget(self.playlist_quality_combo); footer_row.addStretch(); footer_row.addWidget(self.playlist_download_btn)

        layout.addLayout(header_row); layout.addLayout(select_row); layout.addWidget(self.playlist_scroll); layout.addLayout(footer_row)
        self.panel_layout.addWidget(self.playlist_panel)

    def _populate_playlist_section(self, entries):
        for cb in self.playlist_checkboxes: cb.setParent(None)
        self.playlist_checkboxes = []; self.playlist_entries = entries
        for entry in entries:
            title = entry.get('title') or entry.get('id') or entry.get('url') or ''
            cb = QCheckBox(title); cb.setChecked(True)
            self.playlist_list_layout.addWidget(cb); self.playlist_checkboxes.append(cb)
        self.playlist_count_label.setText(STRINGS["PLAYLIST_ITEM_COUNT"].format(count=len(entries)))

    def _set_all_playlist_checkboxes(self, checked):
        for cb in self.playlist_checkboxes: cb.setChecked(checked)

    def _on_playlist_download_clicked(self):
        selected = [e for e, cb in zip(self.playlist_entries, self.playlist_checkboxes) if cb.isChecked()]
        if not selected: self._show_error(STRINGS["PLAYLIST_ERROR_NONE_SELECTED"]); return

        quality_text = self.playlist_quality_combo.currentText()
        is_mp3 = quality_text == STRINGS["PLAYLIST_QUALITY_AUDIO"]
        height_map = {STRINGS["PLAYLIST_QUALITY_1080P"]: 1080, STRINGS["PLAYLIST_QUALITY_720P"]: 720, STRINGS["PLAYLIST_QUALITY_480P"]: 480}
        max_height = height_map.get(quality_text)
        embed_subs = self.embed_subs_checkbox.isChecked(); embed_metadata = self.embed_metadata_checkbox.isChecked()

        for entry in selected:
            video_url = entry.get('url') or entry.get('webpage_url') or entry.get('id')
            title = entry.get('title') or entry.get('id') or video_url
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
            unique_id = f"playlist-{entry.get('id', video_url)}-{quality_text}"
            if unique_id in self.download_items: continue  # already queued from a previous click

            if is_mp3:
                full_path = os.path.join(self.save_path, f"{safe_title}.mp3")
                request = {'kind': 'mp3', 'url': video_url, 'save_path': full_path, 'embed_subs': embed_subs, 'embed_metadata': embed_metadata}
                self._queue_download(unique_id, title, STRINGS["MP3_FORMAT_DETAILS"], request)
            else:
                format_selection = f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]" if max_height else "bestvideo+bestaudio/best"
                full_path = os.path.join(self.save_path, f"{safe_title}.mp4")
                request = {'kind': 'video', 'url': video_url, 'format_selection': format_selection, 'save_path': full_path, 'embed_subs': embed_subs, 'embed_metadata': embed_metadata}
                self._queue_download(unique_id, title, quality_text, request)

    def _create_save_path_section(self):
        self.save_path_panel = QWidget(); layout = QVBoxLayout(self.save_path_panel); layout.setContentsMargins(0,0,0,0); layout.setSpacing(5)
        label = QLabel(STRINGS["SAVE_LOCATION_LABEL"]); label.setObjectName("savePathLabel")
        container = QFrame(); container.setObjectName("urlInputContainer"); h_layout = QHBoxLayout(container); h_layout.setContentsMargins(10, 2, 2, 2); h_layout.setSpacing(10)
        self.save_path_input = QLineEdit(); self.save_path_input.setReadOnly(True)
        browse_btn = QPushButton(STRINGS["BROWSE_BUTTON"]); browse_btn.setObjectName("browseButton"); browse_btn.setFixedSize(100, 36); browse_btn.clicked.connect(self._browse_save_path)
        h_layout.addWidget(self.save_path_input); h_layout.addWidget(browse_btn); layout.addWidget(label); layout.addWidget(container); self.panel_layout.addWidget(self.save_path_panel)
    
    def _create_cookies_section(self):
        self.cookies_panel = QWidget(); layout = QVBoxLayout(self.cookies_panel); layout.setContentsMargins(0,0,0,0); layout.setSpacing(5)
        label = QLabel(STRINGS["COOKIES_LABEL"]); label.setObjectName("cookiesLabel")
        container = QFrame(); container.setObjectName("urlInputContainer"); h_layout = QHBoxLayout(container); h_layout.setContentsMargins(10, 2, 2, 2); h_layout.setSpacing(10)
        self.cookies_path_input = QLineEdit(); self.cookies_path_input.setReadOnly(True)
        clear_btn = QPushButton(STRINGS["CLEAR_BUTTON"]); clear_btn.setObjectName("clearCookiesButton"); clear_btn.setFixedSize(100, 36); clear_btn.clicked.connect(self._clear_cookies)
        h_layout.addWidget(self.cookies_path_input); h_layout.addWidget(clear_btn); layout.addWidget(label); layout.addWidget(container); self.panel_layout.addWidget(self.cookies_panel)

    def _create_formats_section(self):
        self.formats_panel = QWidget(); formats_layout = QVBoxLayout(self.formats_panel); formats_layout.setContentsMargins(0, 0, 0, 0); formats_layout.setSpacing(15)
        filter_bar = QWidget(); filter_layout = QHBoxLayout(filter_bar); filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_label = QLabel(STRINGS["FILTER_LABEL"]); filter_label.setObjectName("filterLabel"); quality_label = QLabel(STRINGS["QUALITY_LABEL"]); quality_label.setObjectName("filterDropdownLabel")
        self.quality_filter = QComboBox(); self.quality_filter.currentIndexChanged.connect(self._filter_table); format_label = QLabel(STRINGS["FORMAT_LABEL"]); format_label.setObjectName("filterDropdownLabel")
        self.format_filter = QComboBox(); self.format_filter.currentIndexChanged.connect(self._filter_table)
        language_label = QLabel(STRINGS["LANGUAGE_LABEL"]); language_label.setObjectName("filterDropdownLabel")
        self.language_filter = QComboBox(); self.language_filter.currentIndexChanged.connect(self._filter_table)
        filter_layout.addWidget(filter_label); filter_layout.addStretch(); filter_layout.addWidget(quality_label); filter_layout.addWidget(self.quality_filter); filter_layout.addSpacing(10)
        filter_layout.addWidget(format_label); filter_layout.addWidget(self.format_filter); filter_layout.addSpacing(10)
        filter_layout.addWidget(language_label); filter_layout.addWidget(self.language_filter)
        extras_bar = QWidget(); extras_layout = QHBoxLayout(extras_bar); extras_layout.setContentsMargins(0, 0, 0, 0)
        self.embed_subs_checkbox = QCheckBox(STRINGS["EMBED_SUBS_LABEL"]); self.embed_metadata_checkbox = QCheckBox(STRINGS["EMBED_METADATA_LABEL"])
        extras_layout.addWidget(self.embed_subs_checkbox); extras_layout.addSpacing(15); extras_layout.addWidget(self.embed_metadata_checkbox); extras_layout.addStretch()
        self.formats_table = QTableWidget(); self.formats_table.setColumnCount(5); self.formats_table.setHorizontalHeaderLabels(["Quality", "Format", "Size", "Note", "Action"]); header = self.formats_table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.formats_table.verticalHeader().hide(); self.formats_table.setAlternatingRowColors(True); self.formats_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection); self.formats_table.setFocusPolicy(Qt.FocusPolicy.NoFocus); self.formats_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.empty_filter_label = QLabel(STRINGS["NO_FORMATS_MATCH"]); self.empty_filter_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.empty_filter_label.setObjectName("emptyFilterLabel"); self.empty_filter_label.hide()
        formats_layout.addWidget(filter_bar); formats_layout.addWidget(extras_bar); formats_layout.addWidget(self.formats_table); formats_layout.addWidget(self.empty_filter_label); self.panel_layout.addWidget(self.formats_panel)

    def _create_downloads_queue(self):
        self.downloads_queue_panel = QFrame(); self.downloads_queue_panel.setObjectName("downloadsQueuePanel")
        queue_layout = QVBoxLayout(self.downloads_queue_panel); queue_layout.setContentsMargins(0, 0, 0, 0)
        queue_header = QWidget(); header_layout = QHBoxLayout(queue_header); header_layout.setContentsMargins(0, 0, 0, 10)
        queue_title = QLabel(STRINGS["DOWNLOADS_QUEUE_TITLE"]); queue_title.setObjectName("queueTitle"); self.progress_counter = QLabel(STRINGS["COMPLETED_COUNTER"].format(completed=0, total=0)); self.progress_counter.setObjectName("queueCounter")
        header_layout.addWidget(queue_title); header_layout.addStretch(); header_layout.addWidget(self.progress_counter)
        self.queue_list_layout = QVBoxLayout(); self.queue_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop); self.queue_list_layout.setSpacing(5)
        queue_layout.addWidget(queue_header); queue_layout.addLayout(self.queue_list_layout); self.panel_layout.addWidget(self.downloads_queue_panel)
        
    def check_dependencies(self):
        self.ytdlp_found = os.path.exists(YTDLP_PATH)
        self.ffmpeg_found = os.path.exists(FFMPEG_PATH)
        if not self.ytdlp_found or not self.ffmpeg_found:
            missing = []
            if not self.ytdlp_found: missing.append(STRINGS["COMPONENT_YTDLP"])
            if not self.ffmpeg_found: missing.append(STRINGS["COMPONENT_FFMPEG"])
            dialog = ModalDialog(STRINGS["DIALOG_TITLE_SETUP"], STRINGS["SETUP_MISSING_DEPS"].format(missing_list='\n- '.join(missing)), {STRINGS["SETUP_DOWNLOAD_NOW"]: "download", STRINGS["SETUP_EXIT"]: "exit"}, self)
            if dialog.exec() and dialog.result == "download": self._start_dependency_downloads()
            else: QApplication.instance().quit()
        else:
            self._check_for_app_updates(silent=True)
            self._start_ytdlp_version_check(silent=True)
            self._check_ffmpeg_health(silent=True)

    def _start_dependency_downloads(self):
        self.setEnabled(False)
        self.dependency_dialog = ModalDialog(STRINGS["DIALOG_TITLE_SETUP"], STRINGS["STATUS_PREPARING_COMPONENTS"], {}, self); self.dependency_dialog.show()
        if not self.ytdlp_found: self._start_ytdlp_download()
        elif not self.ffmpeg_found: self._start_ffmpeg_download()

    def _start_ytdlp_download(self, for_update=False):
        if not for_update: self.dependency_dialog = ModalDialog(STRINGS["DIALOG_TITLE_DOWNLOADING"], "...", {}, self); self.dependency_dialog.show(); self.setEnabled(False)
        self.ytdlp_thread = QThread(); self.ytdlp_worker = YTDlpWorker(); self.ytdlp_worker.moveToThread(self.ytdlp_thread)
        self.ytdlp_thread.started.connect(self.ytdlp_worker.run); self.ytdlp_worker.signals.ytdlp_progress.connect(self._update_dependency_progress)
        self.ytdlp_worker.signals.ytdlp_finished.connect(self._on_ytdlp_download_finished); self.ytdlp_worker.signals.ytdlp_finished.connect(self.ytdlp_thread.quit)
        self.ytdlp_worker.signals.ytdlp_finished.connect(self.ytdlp_worker.deleteLater); self.ytdlp_thread.finished.connect(self.ytdlp_thread.deleteLater); self.ytdlp_thread.start()

    def _start_ffmpeg_download(self):
        self.ffmpeg_thread = QThread(); self.ffmpeg_worker = FFmpegDownloadWorker(); self.ffmpeg_worker.moveToThread(self.ffmpeg_thread)
        self.ffmpeg_thread.started.connect(self.ffmpeg_worker.run); self.ffmpeg_worker.signals.ytdlp_progress.connect(self._update_dependency_progress)
        self.ffmpeg_worker.signals.ytdlp_finished.connect(self._on_ffmpeg_download_finished); self.ffmpeg_worker.signals.ytdlp_finished.connect(self.ffmpeg_thread.quit)
        self.ffmpeg_worker.signals.ytdlp_finished.connect(self.ffmpeg_worker.deleteLater); self.ffmpeg_thread.finished.connect(self.ffmpeg_thread.deleteLater); self.ffmpeg_thread.start()

   # Replace your old _on_ytdlp_download_finished with this new one (around line 232)
    def _on_ytdlp_download_finished(self, success, message):
        if not success:
            ModalDialog(STRINGS["DIALOG_TITLE_FAILED"], message, {"OK": "ok"}, self).exec()
            self.close()
            return

        self.ytdlp_found = True
    
        # Check if we were in 'update' mode
        if self.is_updating_ytdlp:
            self.is_updating_ytdlp = False # Reset the flag
            # Show a success dialog and offer to restart (just like the ffmpeg handler)
            dialog = ModalDialog(
                STRINGS["DIALOG_TITLE_SUCCESS"],
                STRINGS["DEPS_SUCCESS_RESTART"].format(component="yt-dlp"),
                {STRINGS["RESTART_BUTTON"]: "restart"},
                self
            )
            dialog.exec()
            # The magic line that restarts the application to use the new file
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            # This is the original logic for the first-time setup
            self.check_dependencies()

    def _on_ffmpeg_download_finished(self, success, message):
        if self.dependency_dialog: self.dependency_dialog.close(); self.setEnabled(True)
        if not success: ModalDialog(STRINGS["DIALOG_TITLE_FAILED"], message, {"OK": "ok"}, self).exec(); self.close()
        else:
            self.ffmpeg_found = True
            ModalDialog(STRINGS["DIALOG_TITLE_SUCCESS"], STRINGS["DEPS_SUCCESS_RESTART"].format(component=message), {STRINGS["RESTART_BUTTON"]: "restart"}, self).exec()
            os.execl(sys.executable, sys.executable, *sys.argv)

    def _on_ytdlp_update_clicked(self):
        self._start_ytdlp_version_check(silent=False)

    def _start_ytdlp_version_check(self, silent=False):
        if self.version_thread and self.version_thread.isRunning(): return
        self.update_dialog = None
        if not silent: self.update_dialog = ModalDialog(STRINGS["DIALOG_TITLE_UPDATE_CHECK"], "...", {}, self); self.update_dialog.show()
        self.version_thread = QThread(); self.version_worker = VersionCheckWorker(); self.version_worker.moveToThread(self.version_thread)
        self.version_thread.started.connect(self.version_worker.run)
        self.version_worker.signals.version_checked.connect(lambda lv, ltv: self._on_ytdlp_version_checked(lv, ltv, silent))
        self.version_worker.signals.version_checked.connect(self.version_thread.quit); self.version_worker.signals.version_checked.connect(self.version_worker.deleteLater)
        self.version_thread.finished.connect(self.version_thread.deleteLater); self.version_thread.finished.connect(lambda: setattr(self, 'version_thread', None))
        self.version_thread.start()

    def _on_ytdlp_version_checked(self, local_version, latest_version, silent=False):
        if self.update_dialog: self.update_dialog.close()
        if local_version == "N/A" and self.ytdlp_found:
            # The binary exists but couldn't run (--version failed) - treat as corrupted and self-repair.
            ModalDialog(STRINGS["DIALOG_TITLE_SETUP"], STRINGS["YTDLP_CORRUPT_REDOWNLOADING"], {"OK": "ok"}, self).exec()
            self.is_updating_ytdlp = True; self._start_ytdlp_download(for_update=True)
        elif local_version == "N/A" or latest_version == "N/A":
            if not silent: ModalDialog(STRINGS["DIALOG_TITLE_UPDATE_CHECK"], STRINGS["YTDLP_UPDATE_FAILED"], {"OK": "ok"}, self).exec()
        elif local_version == latest_version:
            if not silent: ModalDialog(STRINGS["DIALOG_TITLE_UP_TO_DATE"], STRINGS["YTDLP_UP_TO_DATE"].format(local_version=local_version), {"OK": "ok"}, self).exec()
        else:
            dialog = ModalDialog(STRINGS["DIALOG_TITLE_UPDATE_AVAILABLE"], STRINGS["YTDLP_UPDATE_AVAILABLE"].format(local_version=local_version, latest_version=latest_version), {STRINGS["DOWNLOAD_AND_RESTART_BUTTON"]: "download", "Cancel": "cancel"}, self)
            if dialog.exec() and dialog.result == "download": self.is_updating_ytdlp = True; self._start_ytdlp_download(for_update=True)

    def _check_ffmpeg_health(self, silent=True):
        if self.ffmpeg_health_thread and self.ffmpeg_health_thread.isRunning(): return
        self.ffmpeg_health_thread = QThread(); self.ffmpeg_health_worker = FFmpegHealthCheckWorker(); self.ffmpeg_health_worker.moveToThread(self.ffmpeg_health_thread)
        self.ffmpeg_health_thread.started.connect(self.ffmpeg_health_worker.run)
        self.ffmpeg_health_worker.signals.ffmpeg_health_checked.connect(self._on_ffmpeg_health_checked)
        self.ffmpeg_health_worker.signals.ffmpeg_health_checked.connect(self.ffmpeg_health_thread.quit); self.ffmpeg_health_worker.signals.ffmpeg_health_checked.connect(self.ffmpeg_health_worker.deleteLater)
        self.ffmpeg_health_thread.finished.connect(self.ffmpeg_health_thread.deleteLater); self.ffmpeg_health_thread.finished.connect(lambda: setattr(self, 'ffmpeg_health_thread', None))
        self.ffmpeg_health_thread.start()

    def _on_ffmpeg_health_checked(self, healthy):
        if healthy or not self.ffmpeg_found: return
        # FFmpeg is present but couldn't run - treat as corrupted and self-repair with a fresh "latest" download.
        ModalDialog(STRINGS["DIALOG_TITLE_SETUP"], STRINGS["FFMPEG_CORRUPT_REDOWNLOADING"], {"OK": "ok"}, self).exec()
        self._start_ffmpeg_download()

    def _check_for_app_updates(self, silent=False):
        if self.app_update_thread and self.app_update_thread.isRunning(): return
        if not silent: self.update_dialog = ModalDialog(STRINGS["DIALOG_TITLE_UPDATE_CHECK"], "...", {}, self); self.update_dialog.show()
        self.app_update_thread = QThread(); self.app_update_worker = AppUpdateCheckWorker(config.APP_VERSION); self.app_update_worker.moveToThread(self.app_update_thread)
        self.app_update_thread.started.connect(self.app_update_worker.run); self.app_update_worker.signals.app_update_checked.connect(lambda latest_version: self._on_app_update_checked(latest_version, silent))
        self.app_update_worker.signals.app_update_checked.connect(self.app_update_thread.quit); self.app_update_worker.signals.app_update_checked.connect(self.app_update_worker.deleteLater)
        self.app_update_thread.finished.connect(self.app_update_thread.deleteLater); self.app_update_thread.finished.connect(lambda: setattr(self, 'app_update_thread', None))
        self.app_update_thread.start()
        
    def _on_app_update_checked(self, latest_version, silent):
        if hasattr(self, 'update_dialog') and self.update_dialog: self.update_dialog.close()
        if latest_version:
            dialog = ModalDialog(STRINGS["DIALOG_TITLE_UPDATE_AVAILABLE"], STRINGS["APP_UPDATE_AVAILABLE"].format(latest_version=latest_version), {STRINGS["GO_TO_DOWNLOAD_PAGE"]: "download", STRINGS["SKIP_THIS_VERSION"]: "cancel"}, self)
            if dialog.exec() and dialog.result == "download": webbrowser.open(f"{config.DEV_GITHUB}/smart-video-downloader/releases/latest")
        elif not silent: ModalDialog(STRINGS["DIALOG_TITLE_UP_TO_DATE"], STRINGS["APP_UP_TO_DATE"].format(app_version=config.APP_VERSION), {"OK": "ok"}, self).exec()
    
    def _on_add_cookies_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cookies File", "", "Text Files (*.txt);;All Files (*)")
        if file_path: self.cookies_path = file_path; self._save_settings(); self._update_cookies_ui()

    def _clear_cookies(self): self.cookies_path = None; self._save_settings(); self._update_cookies_ui()
    def _update_cookies_ui(self):
        if self.cookies_path and os.path.exists(self.cookies_path): self.cookies_path_input.setText(os.path.basename(self.cookies_path)); self.cookies_panel.show()
        else: self.cookies_path_input.clear(); self.cookies_panel.hide()

    def _load_settings(self):
        settings_path = get_settings_path(); default_path = str(Path.home() / "Downloads"); self.save_path = default_path; self.cookies_path = None
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f: settings_data = json.load(f)
                self.save_path = settings_data.get("save_path", default_path); self.cookies_path = settings_data.get("cookies_path", None)
            except (json.JSONDecodeError, IOError): pass
        self.save_path_input.setText(self.save_path); self._update_cookies_ui()

    def _save_settings(self):
        with open(get_settings_path(), 'w') as f: json.dump({"save_path": self.save_path, "cookies_path": self.cookies_path}, f, indent=4)

    def _browse_save_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder", self.save_path)
        if directory: self.save_path = directory; self.save_path_input.setText(self.save_path); self._save_settings()

    def _update_dependency_progress(self, message):
        if self.dependency_dialog: self.dependency_dialog.findChild(QLabel, "modalContentLabel").setText(message)
    
    def _on_fetch_clicked(self):
        url = self.url_input.text().strip();
        if not url: self._show_error(STRINGS["ERROR_EMPTY_URL"]); return
        self.clipboard_hint.hide()
        self.fetch_button.hide(); self.spinner.show(); self.url_input.setDisabled(True)
        self.error_panel.hide(); self.video_info_panel.hide(); self.playlist_panel.hide(); self.formats_panel.hide(); self.save_path_panel.hide(); self.downloads_queue_panel.hide(); self.cookies_panel.hide()
        self.probe_thread = QThread(); self.probe_worker = PlaylistProbeWorker(url, self.cookies_path); self.probe_worker.moveToThread(self.probe_thread)
        self.probe_thread.started.connect(self.probe_worker.run)
        self.probe_worker.signals.finished.connect(lambda success, data: self._on_playlist_probed(success, data, url))
        self.probe_worker.signals.finished.connect(self.probe_thread.quit); self.probe_worker.signals.finished.connect(self.probe_worker.deleteLater)
        self.probe_thread.finished.connect(self.probe_thread.deleteLater); self.probe_thread.start()

    def _on_playlist_probed(self, success, data, url):
        if success and isinstance(data, list) and len(data) > 1:
            self.spinner.hide(); self.fetch_button.show(); self.url_input.setDisabled(False)
            self._populate_playlist_section(data)
            self.playlist_panel.show(); self.save_path_panel.show(); self._update_cookies_ui()
            return
        # Not a playlist (single video, or the probe itself failed) - fall back to the
        # normal single-video fetch, unchanged from before playlist support existed.
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
            self._show_error(STRINGS["ERROR_FETCH_PRIVATE"], is_private=True)
        else: self._show_error(message)

    def _populate_video_data(self):
        self.video_title.setText(self.fetched_data.get("title", "N/A")); self.video_description.setText(self.fetched_data.get("description", STRINGS["NO_DESCRIPTION"]))
        thumb_url = self.fetched_data.get('thumbnail')
        if thumb_url:
            self.thumb_thread = QThread(); self.thumb_worker = ThumbnailWorker(thumb_url); self.thumb_worker.moveToThread(self.thumb_thread)
            self.thumb_thread.started.connect(self.thumb_worker.run); self.thumb_worker.signals.thumbnail_loaded.connect(self._set_thumbnail); self.thumb_worker.signals.thumbnail_loaded.connect(self.thumb_thread.quit)
            self.thumb_worker.signals.thumbnail_loaded.connect(self.thumb_worker.deleteLater); self.thumb_thread.finished.connect(self.thumb_thread.deleteLater); self.thumb_thread.start()

    def _set_thumbnail(self, pixmap):
        self.thumbnail_label.setPixmap(pixmap.scaled(self.thumbnail_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _populate_formats_table(self):
        self.formats_table.setRowCount(0)
        formats = self.fetched_data.get("formats", []); qualities = set(); fmts = set(); languages = set()
        
        video_formats = []; audio_formats = []; merged_formats = []
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none': merged_formats.append(f)
            elif f.get('vcodec') != 'none': video_formats.append(f)
            elif f.get('acodec') != 'none': audio_formats.append(f)

        def sort_key(f): return f.get('height', 0) if f.get('height') is not None else 0
        video_formats.sort(key=sort_key, reverse=True)
        merged_formats.sort(key=sort_key, reverse=True)

        # 1. Add combined video + audio entries
        if video_formats and audio_formats:
            unique_langs = sorted(list(set(a.get('language') for a in audio_formats if a.get('language'))))
            best_audio = max(audio_formats, key=lambda a: a.get('abr') or 0)
            for v_fmt in video_formats:
                for lang in unique_langs:
                    best_lang_audio = next((a for a in sorted(audio_formats, key=lambda x: x.get('abr') or 0, reverse=True) if a.get('language') == lang), None)
                    if best_lang_audio: self._add_format_row(v_fmt, audio_format=best_lang_audio)
                if not unique_langs: self._add_format_row(v_fmt, audio_format=best_audio, is_best_audio=True)
        
        # 2. Add pre-merged formats
        for fmt in merged_formats: self._add_format_row(fmt)
        
        # 3. Add MP3 option
        self._add_mp3_row()
        qualities.add(STRINGS["TABLE_QUALITY_AUDIO"]); fmts.add(STRINGS["TABLE_FORMAT_MP3"])
        
        # 4. Add other audio-only formats
        for fmt in audio_formats: self._add_format_row(fmt)

        for row in range(self.formats_table.rowCount()):
            qualities.add(self.formats_table.item(row, 0).text())
            fmts.add(self.formats_table.item(row, 1).text())
            row_lang = self.formats_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if row_lang: languages.add(row_lang)

        self.quality_filter.clear(); self.format_filter.clear(); self.language_filter.clear()
        self.quality_filter.addItems(["All"] + sorted(list(qualities), key=lambda x: -int(re.sub(r'[^0-9]', '', x) or 0)))
        self.format_filter.addItems(["All"] + sorted(list(fmts)))
        self.language_filter.addItems(["All"] + sorted(list(languages)))
        self._filter_table()

    def _filter_table(self):
        quality = self.quality_filter.currentText(); fmt = self.format_filter.currentText(); language = self.language_filter.currentText(); rows_visible = 0
        for i in range(self.formats_table.rowCount()):
            q_match = (quality == "All" or self.formats_table.item(i, 0).text() == quality); f_match = (fmt == "All" or self.formats_table.item(i, 1).text() == fmt)
            row_lang = self.formats_table.item(i, 0).data(Qt.ItemDataRole.UserRole)
            l_match = (language == "All" or not row_lang or row_lang == language)
            if q_match and f_match and l_match: self.formats_table.setRowHidden(i, False); rows_visible += 1
            else: self.formats_table.setRowHidden(i, True)
        self.empty_filter_label.setVisible(rows_visible == 0); self.formats_table.setVisible(rows_visible > 0)

    def _add_format_row(self, video_format, audio_format=None, is_best_audio=False):
        row = self.formats_table.rowCount(); self.formats_table.insertRow(row)
        is_video = video_format.get('vcodec') != 'none'
        language = None

        if is_video:
            quality = f"{video_format.get('height')}p"; ext = video_format.get('ext', 'mp4'); note = STRINGS["TABLE_NOTE_INCLUDES_AUDIO"]
            v_id = video_format['format_id']; a_id = None
            if audio_format:
                a_id = audio_format['format_id']
                language = audio_format.get('language_name') or audio_format.get('language')
                if is_best_audio: note = STRINGS["TABLE_NOTE_BEST_AUDIO"]
                else: note = STRINGS["TABLE_NOTE_AUDIO_LANG"].format(lang=language or '')
        else:
            quality = STRINGS["TABLE_QUALITY_AUDIO"]; ext = video_format.get('ext'); v_id = video_format['format_id']; a_id = None
            language = video_format.get('language_name') or video_format.get('language')
            note = STRINGS["TABLE_NOTE_AUDIO_LANG"].format(lang=language) if language else video_format.get('format_note', '')

        size_str = f"{(video_format.get('filesize_approx', 0) + (audio_format.get('filesize_approx', 0) if audio_format else 0)) / (1024*1024):.2f} MB" if video_format.get('filesize_approx') else "N/A"

        quality_item = QTableWidgetItem(quality); quality_item.setData(Qt.ItemDataRole.UserRole, language)
        self.formats_table.setItem(row, 0, quality_item); self.formats_table.setItem(row, 1, QTableWidgetItem(ext)); self.formats_table.setItem(row, 2, QTableWidgetItem(size_str)); self.formats_table.setItem(row, 3, QTableWidgetItem(note))
        download_btn = QPushButton(STRINGS["DOWNLOAD_BUTTON"]); download_btn.setObjectName("downloadButton"); download_btn.clicked.connect(lambda _, r=row, vid=v_id, aid=a_id: self._on_download_clicked(r, vid, aid))
        container = QWidget(); layout = QHBoxLayout(container); layout.setContentsMargins(0,0,0,0); layout.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(download_btn)
        self.formats_table.setCellWidget(row, 4, container); self.formats_table.setRowHeight(row, download_btn.sizeHint().height() + 20)

    def _add_mp3_row(self):
        mp3_row_index = self.formats_table.rowCount(); self.formats_table.insertRow(mp3_row_index)
        self.formats_table.setItem(mp3_row_index, 0, QTableWidgetItem(STRINGS["TABLE_QUALITY_AUDIO"])); self.formats_table.setItem(mp3_row_index, 1, QTableWidgetItem(STRINGS["TABLE_FORMAT_MP3"]))
        self.formats_table.setItem(mp3_row_index, 2, QTableWidgetItem(STRINGS["TABLE_SIZE_NA"])); self.formats_table.setItem(mp3_row_index, 3, QTableWidgetItem(STRINGS["TABLE_NOTE_BEST_AUDIO"]))
        mp3_widget = QWidget(); mp3_layout = QHBoxLayout(mp3_widget); mp3_layout.setContentsMargins(0,0,0,0); mp3_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mp3_btn = QPushButton(STRINGS["DOWNLOAD_BUTTON"]); mp3_btn.setObjectName("downloadButton")
        if self.ffmpeg_found: mp3_btn.clicked.connect(lambda _, r=mp3_row_index: self._on_mp3_row_clicked(r))
        else: mp3_btn.setDisabled(True); mp3_btn.setToolTip("FFmpeg not found. Click '?' for help.")
        mp3_layout.addWidget(mp3_btn)
        if not self.ffmpeg_found:
            mp3_help = QPushButton("❓"); mp3_help.setObjectName("mp3HelpButton"); mp3_help.clicked.connect(self._show_ffmpeg_help); mp3_layout.addWidget(mp3_help)
        self.formats_table.setCellWidget(mp3_row_index, 4, mp3_widget); self.formats_table.setRowHeight(mp3_row_index, mp3_btn.sizeHint().height() + 20)

    def _on_download_clicked(self, row, video_id, audio_id=None):
        quality = self.formats_table.item(row, 0).text(); ext = self.formats_table.item(row, 1).text(); safe_title = re.sub(r'[\\/*?:"<>|]', "", self.fetched_data['title'])
        filename = f"{safe_title} - {quality}.{ext}"
        if audio_id: filename = f"{safe_title} - {quality}.mp4"
        full_path = os.path.join(self.save_path, filename); proceed = not os.path.exists(full_path)
        if not proceed:
            dialog = ModalDialog(STRINGS["DIALOG_TITLE_CONFIRM_OVERWRITE"], STRINGS["CONFIRM_OVERWRITE_CONTENT"].format(filename=filename), {STRINGS["OVERWRITE_BUTTON"]: "overwrite", "Cancel": "cancel"}, self)
            if dialog.exec() and dialog.result == "overwrite": proceed = True
        if proceed: self._start_download_worker(row, video_id, audio_id, full_path)

    def _start_download_worker(self, row, video_id, audio_id, save_path):
        btn = self.formats_table.cellWidget(row, 4).findChild(QPushButton); btn.setText(STRINGS["QUEUED_STATUS"]); btn.setDisabled(True)

        quality = self.formats_table.item(row, 0).text(); note = self.formats_table.item(row, 3).text()
        format_details = f"{quality} ({note})"
        unique_id = f"{self.fetched_data['id']}-{video_id}-{audio_id or ''}"
        format_selection = f"{video_id}+{audio_id}" if audio_id else video_id

        request = {
            'kind': 'video', 'url': self.fetched_data['webpage_url'], 'format_selection': format_selection,
            'save_path': save_path, 'embed_subs': self.embed_subs_checkbox.isChecked(), 'embed_metadata': self.embed_metadata_checkbox.isChecked(),
        }
        self._queue_download(unique_id, self.fetched_data['title'], format_details, request, source_button=btn)

    def _on_mp3_row_clicked(self, row):
        safe_title = re.sub(r'[\\/*?:"<>|]', "", self.fetched_data['title']); filename = f"{safe_title}.mp3"; full_path = os.path.join(self.save_path, filename); proceed = not os.path.exists(full_path)
        if not proceed:
            dialog = ModalDialog(STRINGS["DIALOG_TITLE_CONFIRM_OVERWRITE"], STRINGS["CONFIRM_OVERWRITE_CONTENT"].format(filename=filename), {STRINGS["OVERWRITE_BUTTON"]: "overwrite", "Cancel": "cancel"}, self)
            if dialog.exec() and dialog.result == "overwrite": proceed = True
        if proceed:
            btn = self.formats_table.cellWidget(row, 4).findChild(QPushButton); btn.setText(STRINGS["QUEUED_STATUS"]); btn.setDisabled(True)
            unique_id = f"{self.fetched_data['id']}-mp3"
            request = {
                'kind': 'mp3', 'url': self.fetched_data['webpage_url'], 'save_path': full_path,
                'embed_subs': self.embed_subs_checkbox.isChecked(), 'embed_metadata': self.embed_metadata_checkbox.isChecked(),
            }
            self._queue_download(unique_id, self.fetched_data['title'], STRINGS["MP3_FORMAT_DETAILS"], request, source_button=btn)

    def _queue_download(self, unique_id, title, format_details, request, source_button=None):
        """Creates the queue-list entry for a new download and launches it. Shared by single-video, MP3, and playlist downloads."""
        if not self.downloads_queue_panel.isVisible(): self.downloads_queue_panel.show()
        self.downloads_total += 1; self._update_queue_counter()
        item_widget = DownloadItem(title, format_details); self.queue_list_layout.addWidget(item_widget); self.download_items[unique_id] = item_widget
        item_widget.action_btn.clicked.connect(lambda _, uid=unique_id: self._on_queue_item_action_clicked(uid))
        self.download_requests[unique_id] = request
        if source_button: self.download_source_buttons[unique_id] = source_button
        self._launch_download(unique_id, request)

    def _launch_download(self, unique_id, request):
        """Starts (or resumes, via yt-dlp's default --continue behavior) the worker for a queued request."""
        thread = QThread()
        if request['kind'] == 'mp3':
            worker = Mp3DownloadWorker(request['url'], request['save_path'], unique_id, self.cookies_path, request.get('embed_subs', False), request.get('embed_metadata', False))
        else:
            worker = DownloadWorker(request['url'], request['format_selection'], request['save_path'], unique_id, self.cookies_path, request.get('embed_subs', False), request.get('embed_metadata', False))
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.signals.progress.connect(self._update_download_progress); worker.signals.download_finished.connect(self._on_download_finished)
        worker.signals.download_finished.connect(thread.quit); worker.signals.download_finished.connect(worker.deleteLater)
        # The thread must be kept alive via a persistent reference for as long as it runs - a
        # local-only QThread can be garbage-collected by Python while the underlying C++ thread is
        # still executing, crashing the process. Retrying under the same unique_id must NOT drop the
        # previous thread's reference before ITS OWN 'finished' has fired (that happens on a later
        # event-loop pass than _on_download_finished, so a same-key dict would race) - a list that
        # only removes a thread once its own finished signal confirms it's done avoids that entirely.
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda t=thread: self.active_threads.remove(t) if t in self.active_threads else None)
        self.active_threads.append(thread); self.active_workers[unique_id] = worker; thread.start()

    def _on_queue_item_action_clicked(self, unique_id):
        item = self.download_items.get(unique_id)
        if not item: return
        if item.state == "running":
            worker = self.active_workers.get(unique_id)
            if worker: worker.cancel()
        else:
            request = self.download_requests.get(unique_id)
            if not request: return
            item.state = "running"; item.percentage_label.setText(STRINGS["WAITING_STATUS"]); item.progress_bar.setValue(0)
            item.progress_bar.setProperty("status", ""); item.progress_bar.style().unpolish(item.progress_bar); item.progress_bar.style().polish(item.progress_bar)
            item.action_btn.setText(STRINGS["CANCEL_BUTTON"])
            self._launch_download(unique_id, request)

    def _update_download_progress(self, unique_id, percentage):
        if unique_id in self.download_items: item = self.download_items[unique_id]; item.progress_bar.setValue(percentage); item.percentage_label.setText(f"{percentage}%")

    def _on_download_finished(self, unique_id, success, message):
        self.active_workers.pop(unique_id, None)
        if unique_id in self.download_items:
            item = self.download_items[unique_id]
            if success:
                item.state = "completed"
                self.downloads_completed += 1; item.percentage_label.setText(STRINGS["COMPLETED_STATUS"]); item.progress_bar.setValue(100); item.progress_bar.setProperty("status", "completed")
                item.action_btn.hide()
            else:
                cancelled = (message == STRINGS["CANCELLED_STATUS"])
                item.state = "cancelled" if cancelled else "failed"
                if cancelled:
                    item.percentage_label.setText(STRINGS["CANCELLED_STATUS"]); item.progress_bar.setProperty("status", "failed")
                else:
                    msg_lower = message.lower()
                    if any(keyword in msg_lower for keyword in ["private", "login", "members only", "subscribers", "sign in"]):
                        self._show_error(STRINGS["ERROR_FETCH_PRIVATE"], is_private=True)
                        item.title_label.setToolTip(STRINGS["PRIVATE_VIDEO_TOOLTIP"])
                    else:
                        self._show_error(message)
                        item.title_label.setToolTip(message)
                    item.percentage_label.setText(STRINGS["FAILED_STATUS"]); item.progress_bar.setProperty("status", "failed")
                item.action_btn.setText(STRINGS["RETRY_BUTTON"]); item.action_btn.setEnabled(True)
                btn = self.download_source_buttons.get(unique_id)
                if btn:
                    try: btn.setText(STRINGS["DOWNLOAD_BUTTON"]); btn.setDisabled(False)
                    except RuntimeError: pass
            item.progress_bar.style().unpolish(item.progress_bar); item.progress_bar.style().polish(item.progress_bar)
        self._update_queue_counter()
        
    def _update_queue_counter(self): self.progress_counter.setText(STRINGS["COMPLETED_COUNTER"].format(completed=self.downloads_completed, total=self.downloads_total))
    
    def _show_error(self, message, is_private=False):
        for i in reversed(range(self.error_button_layout.count())): 
            item = self.error_button_layout.itemAt(i)
            if item.widget(): item.widget().setParent(None)
            else: self.error_button_layout.removeItem(item)

        if len(str(message)) > 120:
            self.error_message_label.setText(STRINGS["ERROR_LONG_MESSAGE"])
            details_btn = QPushButton(STRINGS["ERROR_DETAILS_BUTTON"]); details_btn.setObjectName("modalButton")
            def show_details_dialog():
                buttons = {"OK": "ok"}
                if is_private: buttons[STRINGS["ERROR_ADD_COOKIES_BUTTON"]] = "cookie_help"
                dialog = ModalDialog(STRINGS["DIALOG_TITLE_ERROR_DETAILS"], str(message), buttons, is_scrollable=True, parent=self)
                if dialog.exec() and dialog.result == "cookie_help": self._show_private_video_help()
            details_btn.clicked.connect(show_details_dialog)
            self.error_button_layout.addWidget(details_btn)
            self.error_button_widget.show()
        else:
            self.error_message_label.setText(str(message))
            self.error_button_widget.hide()

        if is_private and len(str(message)) <= 120:
            help_btn = QPushButton(STRINGS["ERROR_ADD_COOKIES_BUTTON"]); help_btn.setObjectName("modalButton")
            help_btn.clicked.connect(self._show_private_video_help)
            self.error_button_layout.addWidget(help_btn)
            self.error_button_widget.show()
        
        self.error_button_layout.addStretch()
        self.error_panel.show()

    def _show_full_description(self):
        if self.fetched_data: dialog = ModalDialog(STRINGS["DIALOG_TITLE_FULL_DESCRIPTION"], self.fetched_data.get("description", STRINGS["NO_DESCRIPTION"]), {"Close": "close"}, is_scrollable=True, parent=self); dialog.exec()
    def _show_about_dialog(self): ModalDialog(STRINGS["MENU_ABOUT"], STRINGS["ABOUT_CONTENT"].format(app_version=config.APP_VERSION), {"OK": "ok"}, parent=self).exec()
    def _show_help_dialog(self): ModalDialog(STRINGS["MENU_HELP"], STRINGS["HELP_CONTENT"], {"OK": "ok"}, is_scrollable=True, parent=self).exec()
    def _show_private_video_help(self):
        ModalDialog(STRINGS["DIALOG_TITLE_PRIVATE_VIDEO"], STRINGS["PRIVATE_VIDEO_HELP"], {"OK": "ok"}, is_scrollable=True, parent=self).exec()
    def _show_ffmpeg_help(self):
        dialog = ModalDialog(STRINGS["DIALOG_TITLE_FFMPEG_NOT_FOUND"], STRINGS["FFMPEG_HELP"], {STRINGS["DOWNLOAD_FFMPEG_BUTTON"]: "download", "Cancel": "cancel"}, parent=self)
        if dialog.exec() and dialog.result == "download": self._start_ffmpeg_download()
    def _show_dev_dialog(self): DeveloperDialog(self).exec()
    def closeEvent(self, event): self._save_settings(); super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(generate_stylesheet())
    window = SmartVideoDownloader()
    window.show()
    sys.exit(app.exec())





    # Command for building app with PyInstaller:
    # pyinstaller --name "Smart Video Downloader" --onefile --windowed --icon="icon.ico" --add-data "icon.ico;." --add-data "icon.png;." main.py