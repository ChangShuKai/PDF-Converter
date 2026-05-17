from PyQt6.QtWidgets import QListWidget, QAbstractItemView, QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon
import os

class DraggableListWidget(QListWidget):
    orderChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dropEvent(self, event: QDropEvent):
        super().dropEvent(event)
        self.orderChanged.emit()

class FileDropArea(QFrame):
    filesDropped = pyqtSignal(list)
    clicked = pyqtSignal()

    def __init__(self, title="拖入圖片或 PDF", subtitle="或點擊選擇檔案", parent=None):
        super().__init__(parent)
        self.setObjectName("DropArea")
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        from styles import Styles
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(Styles.LABEL_TITLE + "font-size: 18px;")
        layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        layout.addWidget(self.subtitle_label, 0, Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.setProperty("dragging", "true")
            self.style().unpolish(self)
            self.style().polish(self)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setProperty("dragging", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragging", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        
        urls = event.mimeData().urls()
        files = [url.toLocalFile() for url in urls]
        self.filesDropped.emit(files)
        event.acceptProposedAction()

class GlassButton(QPushButton):
    def __init__(self, text, parent=None, primary=True):
        super().__init__(text, parent)
        from styles import Styles
        if primary:
            self.setStyleSheet(Styles.BUTTON_PRIMARY)
        else:
            self.setStyleSheet(Styles.SIDEBAR_BUTTON)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_active(self, active):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
