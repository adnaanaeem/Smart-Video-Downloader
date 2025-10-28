# styles.py

STYLESHEET = """
#centralWidget { font-family: Segoe UI, Arial, sans-serif; }
#backgroundFrame { background-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 #111827, stop:1 #000000); }
#contentPanel { background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; }
QLabel { color: #E5E7EB; }
#headerTitle { font-size: 22px; font-weight: bold; padding-bottom: 4px; }
#urlLabel, #savePathLabel, #cookiesLabel { color: #9CA3AF; font-size: 13px; margin-top: 5px; }
#urlInputContainer { background-color: #111827; border: 1px solid #374151; border-radius: 8px; }
#linkIcon { font-size: 18px; }
QLineEdit { background-color: transparent; border: none; color: #F9FAFB; font-size: 15px; }
#fetchButton { background-color: #DC2626; color: white; font-size: 15px; font-weight: bold; border: none; border-radius: 6px; }
#fetchButton:hover { background-color: #EF4444; }
#browseButton { background-color: #374151; color: white; font-size: 14px; border: none; border-radius: 6px; }
#browseButton:hover { background-color: #4B5563; }
#clearCookiesButton { background-color: #4B5563; color: white; font-size: 14px; border: none; border-radius: 6px; }
#clearCookiesButton:hover { background-color: #5A6675; }
#menuButton { color: #D1D5DB; background-color: rgba(255, 255, 255, 0.1); border: none; border-radius: 8px; font-size: 14px; font-weight: bold; }
#menuButton:hover { background-color: rgba(255, 255, 255, 0.15); }
#menuButton::menu-indicator { image: none; }
QMenu { background-color: #1F2937; border: 1px solid rgba(255, 255, 255, 0.1); color: #E5E7EB; }
QMenu::item:selected { background-color: #DC2626; }
#errorPanel { background-color: rgba(220, 38, 38, 0.1); border: 1px solid #DC2626; border-radius: 8px; padding: 10px; }
#errorIcon { font-size: 16px; }
#errorMessage { color: #F87171; }
#thumbnail { background-color: #374151; border-radius: 8px; color: #9CA3AF; font-size: 16px; }
#videoTitle { font-size: 20px; font-weight: bold; color: #F9FAFB; }
#videoDescription { font-size: 13px; color: #9CA3AF; }
#showMoreButton { color: #3B82F6; background-color: transparent; border: none; font-size: 12px; font-weight: bold; padding: 0px; }
#showMoreButton:hover { text-decoration: underline; }
#mainScrollArea { border: none; background-color: transparent; }
#descriptionScrollArea { border: none; background-color: #1F2C37; }
#descriptionScrollArea QWidget { background-color: #1F2C37; }
QScrollBar:vertical { border: none; background: #111827; width: 8px; margin: 0px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #4B5563; min-height: 20px; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
#filterLabel { font-size: 14px; font-weight: bold; }
#filterDropdownLabel { color: #FFFFFF; }
QComboBox { background-color: #1F2937; border: 1px solid #374151; border-radius: 6px; padding: 5px 10px; min-width: 100px; color: #E5E7EB; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #1F2937;
    border: 1px solid #374151;
    selection-background-color: #DC2626;
    color: #E5E7EB;
    selection-color: #FFFFFF;
}
QTableWidget { background-color: transparent; border: 1px solid #374151; border-radius: 8px; gridline-color: #374151; }
QHeaderView::section { background-color: #111827; color: #9CA3AF; padding: 8px; border: none; border-bottom: 1px solid #374151; }
QTableWidget::item { padding: 10px; color: #E5E7EB; }
#emptyFilterLabel { color: #6B7280; font-size: 14px; padding: 20px; }
#downloadButton { background-color: #16A34A; color: white; font-weight: bold; border: none; border-radius: 6px; padding: 8px 16px; margin: 0px; }
#downloadButton:hover { background-color: #22C55E; }
#downloadButton:disabled { background-color: #4B5563; }
#downloadsQueuePanel { background-color: transparent; border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 20px; padding-top: 15px; }
#queueTitle { font-size: 16px; font-weight: bold; }
#queueCounter { color: #9CA3AF; }
#queueItemTitle { font-size: 13px; }
#queueItemPercent { font-size: 13px; color: #9CA3AF; font-weight: bold; }
QProgressBar { border: none; background-color: #111827; border-radius: 4px; }
QProgressBar::chunk { background-color: #3B82F6; }
QProgressBar[status="completed"]::chunk { background-color: #22C55E; }
QProgressBar[status="failed"]::chunk { background-color: #DC2626; }
#mp3HelpButton { color: #9CA3AF; background-color: transparent; border: 1px solid #4B5563; border-radius: 12px; font-size: 14px; font-weight: bold; padding: 0px; width: 24px; height: 24px; }
#mp3HelpButton:hover { background-color: #4B5563; color: white; }
#modalDialog { background-color: #1F2937; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; }
#modalTitleBar { border-bottom: 1px solid #374151; }
#modalTitleLabel { font-size: 16px; font-weight: bold; }
#modalContentLabel { color: #D1D5DB; }
#modalContentLabel a { color: #3B82F6; text-decoration: none; }
#profilePicLabel { background-color: #374151; border-radius: 48px; }
#modalCloseButton { border: none; background-color: transparent; color: #9CA3AF; font-size: 18px; font-weight: bold; }
#modalCloseButton:hover { color: #F9FAFB; }
#modalButton { background-color: #374151; color: #F9FAFB; border: none; border-radius: 6px; padding: 8px 16px; }
#modalButton:hover { background-color: #4B5563; }
"""