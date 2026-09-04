# styles.py

from theme import THEME, FONT_FAMILY

def generate_stylesheet():
    return f"""
    #centralWidget {{ font-family: {FONT_FAMILY}; }}
    #backgroundFrame {{ background-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 {THEME["BACKGROUND_GRADIENT_START"]}, stop:1 {THEME["BACKGROUND_GRADIENT_END"]}); }}
    #contentPanel {{ background-color: {THEME["CONTENT_PANEL"]}; border: 1px solid {THEME["BORDER_PRIMARY"]}; border-radius: 16px; }}
    QLabel {{ color: {THEME["TEXT_PRIMARY"]}; }}
    #headerTitle {{ font-size: 22px; font-weight: bold; padding-bottom: 4px; }}
    #urlLabel, #savePathLabel, #cookiesLabel {{ color: {THEME["TEXT_SECONDARY"]}; font-size: 13px; margin-top: 5px; }}
    #urlInputContainer {{ background-color: {THEME["INPUT_FIELD"]}; border: 1px solid {THEME["BORDER_SECONDARY"]}; border-radius: 8px; }}
    #linkIcon {{ font-size: 18px; }}
    QLineEdit {{ background-color: transparent; border: none; color: {THEME["TEXT_PRIMARY"]}; font-size: 15px; }}
    #fetchButton {{ background-color: {THEME["PRIMARY_ACCENT"]}; color: white; font-size: 15px; font-weight: bold; border: none; border-radius: 6px; }}
    #fetchButton:hover {{ background-color: {THEME["PRIMARY_ACCENT_HOVER"]}; }}
    #browseButton {{ background-color: {THEME["BUTTON_SECONDARY"]}; color: white; font-size: 14px; border: none; border-radius: 6px; }}
    #browseButton:hover {{ background-color: {THEME["BUTTON_SECONDARY_HOVER"]}; }}
    #clearCookiesButton {{ background-color: {THEME["BUTTON_SECONDARY"]}; color: white; font-size: 14px; border: none; border-radius: 6px; }}
    #clearCookiesButton:hover {{ background-color: {THEME["BUTTON_SECONDARY_HOVER"]}; }}
    #menuButton {{ color: {THEME["TEXT_PRIMARY"]}; background-color: {THEME["BUTTON_TERTIARY"]}; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; }}
    #menuButton:hover {{ background-color: {THEME["BUTTON_TERTIARY_HOVER"]}; }}
    #menuButton::menu-indicator {{ image: none; }}
    QMenu {{ background-color: {THEME["DROPDOWN_MENU"]}; border: 1px solid {THEME["BORDER_PRIMARY"]}; color: {THEME["TEXT_PRIMARY"]}; }}
    QMenu::item:selected {{ background-color: {THEME["PRIMARY_ACCENT"]}; }}
    #errorPanel {{ background-color: {THEME["ERROR_BG"]}; border: 1px solid {THEME["PRIMARY_ACCENT"]}; border-radius: 8px; padding: 10px; }}
    #errorIcon {{ font-size: 16px; }}
    #errorMessage {{ color: {THEME["ERROR_TEXT"]}; }}
    #thumbnail {{ background-color: {THEME["BORDER_SECONDARY"]}; border-radius: 8px; color: {THEME["TEXT_SECONDARY"]}; font-size: 16px; }}
    #videoTitle {{ font-size: 20px; font-weight: bold; color: {THEME["TEXT_PRIMARY"]}; }}
    #videoDescription {{ font-size: 13px; color: {THEME["TEXT_SECONDARY"]}; }}
    #showMoreButton {{ color: {THEME["LINK"]}; background-color: transparent; border: none; font-size: 12px; font-weight: bold; padding: 0px; }}
    #showMoreButton:hover {{ text-decoration: underline; }}
    #mainScrollArea, #descriptionScrollArea {{ border: none; background-color: transparent; }}
    #descriptionScrollArea QWidget {{ background-color: transparent; }}
    QScrollBar:vertical {{ border: none; background: {THEME["INPUT_FIELD"]}; width: 8px; margin: 0px; border-radius: 4px; }}
    QScrollBar::handle:vertical {{ background: {THEME["BORDER_TERTIARY"]}; min-height: 20px; border-radius: 4px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; height: 0px; }}
    #filterLabel {{ font-size: 14px; font-weight: bold; }}
    #filterDropdownLabel {{ color: {THEME["TEXT_WHITE"]}; }}
    QComboBox {{ background-color: {THEME["DROPDOWN_MENU"]}; border: 1px solid {THEME["BORDER_SECONDARY"]}; border-radius: 6px; padding: 5px 10px; min-width: 100px; color: {THEME["TEXT_PRIMARY"]}; }}
    QComboBox::drop-down {{ border: none; }}
    QComboBox QAbstractItemView {{ background-color: {THEME["DROPDOWN_MENU"]}; border: 1px solid {THEME["BORDER_SECONDARY"]}; selection-background-color: {THEME["PRIMARY_ACCENT"]}; color: {THEME["TEXT_PRIMARY"]}; selection-color: {THEME["TEXT_WHITE"]}; }}
    QTableWidget {{ background-color: transparent; border: 1px solid {THEME["BORDER_SECONDARY"]}; border-radius: 8px; gridline-color: {THEME["BORDER_SECONDARY"]}; }}
    QHeaderView::section {{ background-color: {THEME["INPUT_FIELD"]}; color: {THEME["TEXT_SECONDARY"]}; padding: 8px; border: none; border-bottom: 1px solid {THEME["BORDER_SECONDARY"]}; }}
    QTableWidget::item {{ padding: 10px; color: {THEME["TEXT_PRIMARY"]}; }}
    #emptyFilterLabel {{ color: {THEME["BORDER_TERTIARY"]}; font-size: 14px; padding: 20px; }}
    #downloadButton {{ background-color: {THEME["SUCCESS"]}; color: white; font-weight: bold; border: none; border-radius: 6px; padding: 8px 16px; margin: 0px; }}
    #downloadButton:hover {{ background-color: {THEME["SUCCESS_HOVER"]}; }}
    #downloadButton:disabled {{ background-color: {THEME["BUTTON_DISABLED"]}; }}
    #downloadsQueuePanel {{ background-color: transparent; border-top: 1px solid {THEME["BORDER_PRIMARY"]}; margin-top: 20px; padding-top: 15px; }}
    #queueTitle {{ font-size: 16px; font-weight: bold; }}
    #queueCounter {{ color: {THEME["TEXT_SECONDARY"]}; }}
    #queueItemTitle {{ font-size: 13px; }}
    #queueItemPercent {{ font-size: 13px; color: {THEME["TEXT_SECONDARY"]}; font-weight: bold; }}
    #queueItemActionButton {{ background-color: {THEME["BUTTON_SECONDARY"]}; color: {THEME["TEXT_PRIMARY"]}; font-size: 11px; border: none; border-radius: 5px; }}
    #queueItemActionButton:hover {{ background-color: {THEME["PRIMARY_ACCENT"]}; color: white; }}
    #clipboardHintButton {{ background-color: transparent; color: {THEME["LINK"]}; border: none; text-align: left; font-size: 12px; padding: 2px 0px; }}
    #clipboardHintButton:hover {{ text-decoration: underline; }}
    QProgressBar {{ border: none; background-color: {THEME["PROGRESS_BAR_BG"]}; border-radius: 4px; }}
    QProgressBar::chunk {{ background-color: {THEME["PROGRESS_IN_PROGRESS"]}; }}
    QProgressBar[status="completed"]::chunk {{ background-color: {THEME["PROGRESS_COMPLETED"]}; }}
    QProgressBar[status="failed"]::chunk {{ background-color: {THEME["PROGRESS_FAILED"]}; }}
    #mp3HelpButton {{ color: {THEME["TEXT_SECONDARY"]}; background-color: transparent; border: 1px solid {THEME["BORDER_TERTIARY"]}; border-radius: 12px; font-size: 14px; font-weight: bold; padding: 0px; width: 24px; height: 24px; }}
    #mp3HelpButton:hover {{ background-color: {THEME["BORDER_TERTIARY"]}; color: white; }}
    #modalDialog {{ background-color: {THEME["MODAL_DIALOG"]}; border: 1px solid {THEME["BORDER_PRIMARY"]}; border-radius: 12px; }}
    #modalTitleBar {{ border-bottom: 1px solid {THEME["BORDER_SECONDARY"]}; }}
    #modalTitleLabel {{ font-size: 16px; font-weight: bold; }}
    #modalContentLabel {{ color: {THEME["TEXT_PRIMARY"]}; }}
    #modalContentLabel a {{ color: {THEME["LINK"]}; text-decoration: none; }}
    #profilePicLabel {{ background-color: {THEME["BORDER_SECONDARY"]}; border-radius: 48px; }}
    #modalCloseButton {{ border: none; background-color: transparent; color: {THEME["TEXT_SECONDARY"]}; font-size: 18px; font-weight: bold; }}
    #modalCloseButton:hover {{ color: {THEME["TEXT_PRIMARY"]}; }}
    #modalButton {{ background-color: {THEME["BUTTON_SECONDARY"]}; color: {THEME["TEXT_PRIMARY"]}; border: none; border-radius: 6px; padding: 8px 16px; }}
    #modalButton:hover {{ background-color: {THEME["BUTTON_SECONDARY_HOVER"]}; }}
    """