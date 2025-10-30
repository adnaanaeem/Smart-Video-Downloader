# workers.py

import sys
import os
import re
import json
import requests
import subprocess
import zipfile
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QDialog, QProgressBar
)
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject, QThread
from packaging.version import parse as parse_version

# --- Local Imports ---
import config
from localization import STRINGS

# --- Custom Widgets & Dialogs ---
class Spinner(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedSize(24, 24); self.angle = 0; self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate); self.timer.start(20)
    def rotate(self): self.angle = (self.angle + 10) % 360; self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#DC2626"), 2); painter.setPen(pen)
        rect = QRect(2, 2, self.width() - 4, self.height() - 4); painter.drawArc(rect, self.angle * 16, 90 * 16)

class ModalDialog(QDialog):
    def __init__(self, title, content, buttons=None, is_scrollable=False, parent=None):
        super().__init__(parent)
        self.setModal(True); self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog); self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); self.result = None
        bg_frame = QFrame(self); bg_frame.setObjectName("modalDialog"); main_layout = QVBoxLayout(bg_frame); main_layout.setContentsMargins(1, 1, 1, 15); main_layout.setSpacing(10)
        title_bar = QFrame(); title_bar.setFixedHeight(40); title_bar.setObjectName("modalTitleBar"); title_layout = QHBoxLayout(title_bar); title_layout.setContentsMargins(15, 0, 10, 0)
        title_label = QLabel(title); title_label.setObjectName("modalTitleLabel"); close_btn = QPushButton("✕"); close_btn.setObjectName("modalCloseButton"); close_btn.clicked.connect(self.reject)
        title_layout.addWidget(title_label); title_layout.addStretch(); title_layout.addWidget(close_btn); main_layout.addWidget(title_bar)
        
        content_widget = QLabel(content); content_widget.setWordWrap(True); content_widget.setObjectName("modalContentLabel"); content_widget.setContentsMargins(15, 5, 15, 5)
        content_widget.setOpenExternalLinks(True) # Allow links to be clicked

        if is_scrollable:
            scroll_area = QScrollArea(); scroll_area.setObjectName("descriptionScrollArea"); scroll_area.setWidgetResizable(True); scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)
            self.setMinimumSize(500, 400)
        else:
            main_layout.addWidget(content_widget)
            self.setMinimumSize(500, 300)

        if buttons:
            button_widget = QWidget(); button_layout = QHBoxLayout(button_widget); button_layout.setContentsMargins(0, 10, 0, 0); button_layout.addStretch()
            for text, res in buttons.items(): btn = QPushButton(text); btn.setObjectName("modalButton"); btn.clicked.connect(lambda _, r=res: self.set_result(r)); button_layout.addWidget(btn)
            button_layout.addStretch(); main_layout.addWidget(button_widget)
        
        outer_layout = QVBoxLayout(self); outer_layout.addWidget(bg_frame)

    def set_result(self, result):
        self.result = result; self.accept()

class DeveloperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True); self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog); self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        bg_frame = QFrame(self); bg_frame.setObjectName("modalDialog"); main_layout = QVBoxLayout(bg_frame); main_layout.setContentsMargins(1, 1, 1, 15); main_layout.setSpacing(10)
        title_bar = QFrame(); title_bar.setFixedHeight(40); title_bar.setObjectName("modalTitleBar"); title_layout = QHBoxLayout(title_bar); title_layout.setContentsMargins(15, 0, 10, 0)
        title_label = QLabel(STRINGS["MENU_DEV_INFO"]); title_label.setObjectName("modalTitleLabel"); close_btn = QPushButton("✕"); close_btn.setObjectName("modalCloseButton"); close_btn.clicked.connect(self.reject)
        title_layout.addWidget(title_label); title_layout.addStretch(); title_layout.addWidget(close_btn); main_layout.addWidget(title_bar)
        content_widget = QWidget(); content_layout = QHBoxLayout(content_widget); content_layout.setContentsMargins(20, 10, 20, 10); content_layout.setSpacing(20)
        self.profile_pic_label = QLabel(); self.profile_pic_label.setFixedSize(96, 96); self.profile_pic_label.setObjectName("profilePicLabel"); content_layout.addWidget(self.profile_pic_label)
        dev_info = (f"<b>{STRINGS['DEV_INFO_NAME']}</b> {config.DEV_NAME}<br><b>{STRINGS['DEV_INFO_LOCATION']}</b> {config.DEV_LOCATION}<br><b>{STRINGS['DEV_INFO_SUPPORT']}</b> <a href='mailto:{config.DEV_EMAIL}'>{config.DEV_EMAIL}</a><br><br><a href='{config.DEV_LINKEDIN}'>{STRINGS['DEV_INFO_LINKEDIN']}</a><br><a href='{config.DEV_GITHUB}'>{STRINGS['DEV_INFO_GITHUB']}</a>")
        info_label = QLabel(dev_info); info_label.setOpenExternalLinks(True); info_label.setObjectName("modalContentLabel"); content_layout.addWidget(info_label, 1)
        main_layout.addWidget(content_widget)
        button_widget = QWidget(); button_layout = QHBoxLayout(button_widget); button_layout.setContentsMargins(0, 10, 0, 0); button_layout.addStretch()
        close_dialog_btn = QPushButton("Close"); close_dialog_btn.setObjectName("modalButton"); close_dialog_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_dialog_btn); button_layout.addStretch(); main_layout.addWidget(button_widget)
        outer_layout = QVBoxLayout(self); outer_layout.addWidget(bg_frame); self._load_profile_picture()
    def _load_profile_picture(self):
        self.pic_thread = QThread(); self.pic_worker = ProfilePictureWorker(f"https://github.com/{config.DEV_GITHUB.split('/')[-1]}.png"); self.pic_worker.moveToThread(self.pic_thread)
        self.pic_thread.started.connect(self.pic_worker.run); self.pic_worker.signals.thumbnail_loaded.connect(self._set_profile_picture)
        self.pic_worker.signals.thumbnail_loaded.connect(self.pic_thread.quit); self.pic_worker.signals.thumbnail_loaded.connect(self.pic_worker.deleteLater)
        self.pic_thread.finished.connect(self.pic_thread.deleteLater); self.pic_thread.start()
    def _set_profile_picture(self, pixmap): self.profile_pic_label.setPixmap(self.make_circular(pixmap))
    def make_circular(self, pixmap):
        size = 96; target = QPixmap(size, size); target.fill(Qt.GlobalColor.transparent)
        source = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        painter = QPainter(target); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addEllipse(0, 0, size, size); painter.setClipPath(path)
        painter.drawPixmap(0, 0, source); painter.end(); return target

class DownloadItem(QWidget):
    def __init__(self, title, format_details, parent=None):
        super().__init__(parent); self.setFixedHeight(60); main_layout = QVBoxLayout(self); main_layout.setContentsMargins(10, 5, 10, 5); main_layout.setSpacing(5)
        top_layout = QHBoxLayout(); self.title_label = QLabel(f"{title} - {format_details}"); self.title_label.setObjectName("queueItemTitle"); self.percentage_label = QLabel(STRINGS["WAITING_STATUS"]); self.percentage_label.setObjectName("queueItemPercent")
        top_layout.addWidget(self.title_label); top_layout.addStretch(); top_layout.addWidget(self.percentage_label); self.progress_bar = QProgressBar(); self.progress_bar.setTextVisible(False); self.progress_bar.setFixedHeight(8); self.progress_bar.setValue(0)
        main_layout.addLayout(top_layout); main_layout.addWidget(self.progress_bar); self.setLayout(main_layout)

# --- Worker Signals & Classes ---
class WorkerSignals(QObject):
    finished = pyqtSignal(bool, object); progress = pyqtSignal(str, int); download_finished = pyqtSignal(str, bool, str); log = pyqtSignal(str); thumbnail_loaded = pyqtSignal(QPixmap)
    ytdlp_progress = pyqtSignal(str); ytdlp_finished = pyqtSignal(bool, str); version_checked = pyqtSignal(str, str); app_update_checked = pyqtSignal(str)

class ProfilePictureWorker(QObject):
    def __init__(self, url): super().__init__(); self.signals = WorkerSignals(); self.url = url
    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=5)
            if response.status_code == 200: pixmap = QPixmap(); pixmap.loadFromData(response.content); self.signals.thumbnail_loaded.emit(pixmap)
        except Exception: pass

class VersionCheckWorker(QObject):
    def __init__(self): super().__init__(); self.signals = WorkerSignals()
    def run(self):
        local_version = "N/A"; latest_version = "N/A"
        try:
            if os.path.exists("yt-dlp.exe"):
                result = subprocess.run(["yt-dlp.exe", "--version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0: local_version = result.stdout.strip()
        except Exception: pass
        try:
            response = requests.get(config.YT_DLP_API_URL, timeout=5)
            if response.status_code == 200: latest_version = response.json().get("tag_name", "N/A")
        except Exception: pass
        self.signals.version_checked.emit(local_version, latest_version)

class AppUpdateCheckWorker(QObject):
    def __init__(self, current_version):
        super().__init__()
        self.signals = WorkerSignals()
        self.current_version = current_version
    def run(self):
        try:
            response = requests.get(config.APP_API_URL, timeout=5)
            if response.status_code == 200:
                latest_version_str = response.json().get("tag_name", "v0.0.0")
                # Use a robust version comparison
                if parse_version(latest_version_str) > parse_version(self.current_version):
                    self.signals.app_update_checked.emit(latest_version_str)
                else:
                    self.signals.app_update_checked.emit("") # Explicitly signal "no update"
            else:
                self.signals.app_update_checked.emit("") # Signal completion even on network error
        except Exception:
            self.signals.app_update_checked.emit("") # Signal completion on any error

class YTDlpWorker(QObject):
    def __init__(self): super().__init__(); self.signals = WorkerSignals()
    def run(self):
        try:
            self.signals.ytdlp_progress.emit(STRINGS["STATUS_DOWNLOADING_YTDLP"])
            response = requests.get(config.YT_DLP_URL, stream=True, timeout=10); total_size = int(response.headers.get('content-length', 0))
            with open("yt-dlp.exe", "wb") as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk); downloaded_size += len(chunk)
                    if total_size > 0: self.signals.ytdlp_progress.emit(STRINGS["STATUS_DOWNLOADING_YTDLP_PERCENT"].format(percent=int(100 * downloaded_size / total_size)))
            self.signals.ytdlp_finished.emit(True, STRINGS["SUCCESS_YTDLP_DOWNLOADED"])
        except Exception as e: self.signals.ytdlp_finished.emit(False, STRINGS["ERROR_YTDLP_DOWNLOAD_FAILED"].format(error=str(e)))

class FFmpegDownloadWorker(QObject):
    def __init__(self): super().__init__(); self.signals = WorkerSignals()
    def run(self):
        zip_path = "ffmpeg.zip"
        try:
            self.signals.ytdlp_progress.emit(STRINGS["STATUS_DOWNLOADING_FFMPEG"])
            response = requests.get(config.FFMPEG_URL, stream=True, timeout=15); total_size = int(response.headers.get('content-length', 0))
            with open(zip_path, "wb") as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk); downloaded_size += len(chunk)
                    if total_size > 0: self.signals.ytdlp_progress.emit(STRINGS["STATUS_DOWNLOADING_FFMPEG_PERCENT"].format(percent=int(100 * downloaded_size / total_size)))
            
            self.signals.ytdlp_progress.emit(STRINGS["STATUS_EXTRACTING_FFMPEG"])
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if member.endswith('bin/ffmpeg.exe'):
                        source = zip_ref.open(member)
                        with open("ffmpeg.exe", "wb") as target: target.write(source.read())
                        break
            os.remove(zip_path)
            self.signals.ytdlp_finished.emit(True, STRINGS["SUCCESS_FFMPEG_DOWNLOADED"])
        except Exception as e:
            if os.path.exists(zip_path): os.remove(zip_path)
            self.signals.ytdlp_finished.emit(False, STRINGS["ERROR_FFMPEG_DOWNLOAD_FAILED"].format(error=str(e)))

class FetchWorker(QObject):
    def __init__(self, url, cookies_path=None):
        super().__init__(); self.signals = WorkerSignals(); self.url = url; self.cookies_path = cookies_path
    def run(self):
        try:
            cmd = ["yt-dlp.exe", self.url, "--dump-json", "--no-playlist"]
            if self.cookies_path: cmd.extend(["--cookies", self.cookies_path])
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0: self.signals.finished.emit(True, json.loads(result.stdout))
            else: self.signals.finished.emit(False, (result.stderr or "") + (result.stdout or "") or STRINGS["ERROR_FETCH_GENERIC"])
        except Exception as e: self.signals.finished.emit(False, str(e))

class ThumbnailWorker(QObject):
    def __init__(self, url): super().__init__(); self.signals = WorkerSignals(); self.url = url
    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            if response.status_code == 200: pixmap = QPixmap(); pixmap.loadFromData(response.content); self.signals.thumbnail_loaded.emit(pixmap)
        except Exception: pass

class DownloadWorker(QObject):
    def __init__(self, url, format_id, save_path, unique_id, cookies_path=None):
        super().__init__(); self.signals = WorkerSignals(); self.url = url; self.format_id = format_id
        self.save_path = save_path; self.unique_id = unique_id; self.cookies_path = cookies_path
    def run(self):
        try:
            cmd = ["yt-dlp.exe", self.url, "-f", self.format_id, "-o", self.save_path, "--progress", "--no-warnings", "--merge-output-format", "mp4"]
            if self.cookies_path: cmd.extend(["--cookies", self.cookies_path])
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            output_lines = []; progress_regex = re.compile(r"\[download\]\s+(?P<percent>[\d\.]+)%")
            for line in iter(process.stdout.readline, ''):
                stripped_line = line.strip(); output_lines.append(stripped_line); self.signals.log.emit(stripped_line)
                match = progress_regex.search(line)
                if match: self.signals.progress.emit(self.unique_id, int(float(match.group("percent"))))
            process.wait()
            if process.returncode == 0: self.signals.download_finished.emit(self.unique_id, True, STRINGS["SUCCESS_DOWNLOAD_COMPLETED"])
            else: self.signals.download_finished.emit(self.unique_id, False, "\n".join(output_lines))
        except Exception as e: self.signals.download_finished.emit(self.unique_id, False, str(e))

class Mp3DownloadWorker(QObject):
    def __init__(self, url, save_path, unique_id, cookies_path=None):
        super().__init__(); self.signals = WorkerSignals(); self.url = url; self.save_path = save_path
        self.unique_id = unique_id; self.cookies_path = cookies_path
    def run(self):
        try:
            cmd = ["yt-dlp.exe", self.url, "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", self.save_path, "--progress", "--no-warnings"]
            if self.cookies_path: cmd.extend(["--cookies", self.cookies_path])
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            output_lines = []; progress_regex = re.compile(r"\[download\]\s+Destination:\s.*\s+\(frag\s\d+/\d+\)\n\[download\]\s+(?P<percent>[\d\.]+)%")
            dest_regex = re.compile(r"\[ExtractAudio\] Destination: (.*)")
            for line in iter(process.stdout.readline, ''):
                stripped_line = line.strip(); output_lines.append(stripped_line); self.signals.log.emit(stripped_line)
                match = progress_regex.search(line) or dest_regex.search(line)
                if match and "percent" in match.groupdict(): self.signals.progress.emit(self.unique_id, int(float(match.group("percent"))))
                elif "Destination:" in line: self.signals.progress.emit(self.unique_id, 100) # Final step
            process.wait()
            if process.returncode == 0: self.signals.download_finished.emit(self.unique_id, True, STRINGS["SUCCESS_MP3_CONVERTED"])
            else: self.signals.download_finished.emit(self.unique_id, False, "\n".join(output_lines))
        except Exception as e: self.signals.download_finished.emit(self.unique_id, False, str(e))