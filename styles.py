class Styles:
    # Modern Color Palette
    BG_COLOR = "#0f172a"  # Deep navy
    ACCENT_COLOR = "#38bdf8"  # Sky blue
    ACCENT_HOVER = "#0ea5e9"
    TEXT_COLOR = "#f8fafc"
    SECONDARY_TEXT = "#94a3b8"
    GLASS_BG = "rgba(30, 41, 59, 0.7)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.1)"
    
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {BG_COLOR};
        }}
    """
    
    GLASS_PANEL = f"""
        QFrame#GlassPanel {{
            background-color: {GLASS_BG};
            border: 1px solid {GLASS_BORDER};
            border-radius: 16px;
        }}
    """
    
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {ACCENT_COLOR};
            color: {BG_COLOR};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: #0284c7;
        }}
        QPushButton:disabled {{
            background-color: #334155;
            color: #64748b;
        }}
    """

    LIST_STYLE = f"""
        QListWidget {{
            background-color: transparent;
            border: none;
            outline: none;
            color: {TEXT_COLOR};
            font-size: 13px;
        }}
        QListWidget::item {{
            background-color: rgba(51, 65, 85, 0.5);
            border-radius: 8px;
            margin-bottom: 8px;
            padding: 10px;
            border: 1px solid transparent;
        }}
        QListWidget::item:selected {{
            background-color: rgba(56, 189, 248, 0.2);
            border: 1px solid {ACCENT_COLOR};
            color: {ACCENT_COLOR};
        }}
        QListWidget::item:hover {{
            background-color: rgba(51, 65, 85, 0.8);
        }}
    """

    SCROLLBAR = f"""
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(148, 163, 184, 0.3);
            min-height: 20px;
            border-radius: 4px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """

    LABEL_TITLE = f"""
        QLabel {{
            color: {TEXT_COLOR};
            font-size: 24px;
            font-weight: bold;
        }}
    """
    
    LABEL_SUBTITLE = f"""
        QLabel {{
            color: {SECONDARY_TEXT};
            font-size: 14px;
        }}
    """

    DROP_AREA = f"""
        QFrame#DropArea {{
            border: 2px dashed {GLASS_BORDER};
            border-radius: 12px;
            background-color: rgba(30, 41, 59, 0.4);
        }}
        QFrame#DropArea[dragging="true"] {{
            border-color: {ACCENT_COLOR};
            background-color: rgba(56, 189, 248, 0.1);
        }}
    """
