class Styles:
    # Modern Color Palette - Refined
    BG_COLOR = "#0f172a"  # Deep navy
    ACCENT_COLOR = "#38bdf8"  # Sky blue
    ACCENT_HOVER = "#0ea5e9"
    TEXT_COLOR = "#f8fafc"
    SECONDARY_TEXT = "#94a3b8"
    
    # Advanced Glassmorphism
    GLASS_BG = "rgba(15, 23, 42, 0.45)"
    GLASS_BG_LIGHT = "rgba(255, 255, 255, 0.05)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.12)"
    GLASS_BORDER_BRIGHT = "rgba(255, 255, 255, 0.25)"
    
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {BG_COLOR};
        }}
    """
    
    GLASS_PANEL = f"""
        QFrame#GlassPanel {{
            background-color: {GLASS_BG};
            border: 1px solid {GLASS_BORDER};
            border-radius: 20px;
        }}
    """
    
    SIDEBAR_BUTTON = f"""
        QPushButton {{
            background-color: transparent;
            color: {SECONDARY_TEXT};
            border: 1px solid transparent;
            border-radius: 12px;
            padding: 12px 15px;
            font-size: 15px;
            font-weight: 500;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: {GLASS_BG_LIGHT};
            color: {TEXT_COLOR};
            border: 1px solid {GLASS_BORDER};
        }}
        QPushButton[active="true"] {{
            background-color: rgba(56, 189, 248, 0.15);
            color: {ACCENT_COLOR};
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-weight: bold;
        }}
    """
    
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {ACCENT_COLOR};
            color: #000000;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 15px;
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
        }}
        QListWidget::item {{
            background-color: {GLASS_BG};
            border-radius: 12px;
            margin-bottom: 10px;
            padding: 12px;
            border: 1px solid {GLASS_BORDER};
        }}
        QListWidget::item:selected {{
            background-color: rgba(56, 189, 248, 0.1);
            border: 1px solid {ACCENT_COLOR};
            color: {ACCENT_COLOR};
        }}
        QListWidget::item:hover {{
            background-color: {GLASS_BG_LIGHT};
            border: 1px solid {GLASS_BORDER_BRIGHT};
        }}
    """

    SCROLLBAR = f"""
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 6px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(148, 163, 184, 0.2);
            min-height: 30px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: rgba(148, 163, 184, 0.4);
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """

    LABEL_TITLE = f"""
        QLabel {{
            color: {TEXT_COLOR};
            font-size: 28px;
            font-weight: 800;
            letter-spacing: 0.5px;
        }}
    """
    
    LABEL_SUBTITLE = f"""
        QLabel {{
            color: {SECONDARY_TEXT};
            font-size: 14px;
            font-weight: 400;
        }}
    """

    DROP_AREA = f"""
        QFrame#DropArea {{
            border: 2px dashed {GLASS_BORDER};
            border-radius: 16px;
            background-color: rgba(15, 23, 42, 0.3);
        }}
        QFrame#DropArea:hover {{
            background-color: {GLASS_BG_LIGHT};
            border: 2px dashed {GLASS_BORDER_BRIGHT};
        }}
        QFrame#DropArea[dragging="true"] {{
            border: 2px solid {ACCENT_COLOR};
            background-color: rgba(56, 189, 248, 0.08);
        }}
    """

