import sys
import os
import json
import urllib.request
import ssl
import shutil
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtNetwork import QLocalSocket, QLocalServer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFileDialog, QStackedWidget,
                             QListWidgetItem, QMessageBox, QFrame, QPushButton,
                             QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QBrush, QColor, QAction

from styles import Styles
from ui_components import DraggableListWidget, FileDropArea, GlassButton
from converter_engine import PDFConverterEngine

__version__ = "1.1.0"

class UpdateCheckerThread(QThread):
    update_available = pyqtSignal(str, str, str) # version, description, download_url
    
    def run(self):
        try:
            # Create unverified context for reliability
            ctx = ssl._create_unverified_context()
            url = "https://api.github.com/repos/ChangShuKai/PDF-Converter/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'PDF-Converter-Updater'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").strip("v")
                current_version = __version__.strip("v")
                
                # Check version mismatch
                if latest_version and latest_version != current_version:
                    download_url = None
                    for asset in data.get("assets", []):
                        if asset.get("name", "").endswith(".exe"):
                            download_url = asset.get("browser_download_url")
                            break
                    if not download_url and data.get("assets"):
                        download_url = data["assets"][0].get("browser_download_url")
                    
                    if download_url:
                        self.update_available.emit(data.get("tag_name"), data.get("body", ""), download_url)
        except Exception as e:
            pass

class DownloaderThread(QThread):
    download_finished = pyqtSignal(str)
    download_failed = pyqtSignal(str)
    
    def __init__(self, url, dest):
        super().__init__()
        self.url = url
        self.dest = dest
        
    def run(self):
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(self.url, headers={'User-Agent': 'PDF-Converter-Updater'})
            with urllib.request.urlopen(req, context=ctx, timeout=60) as response, open(self.dest, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            self.download_finished.emit(self.dest)
        except Exception as e:
            self.download_failed.emit(str(e))

class ModernPDFConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Premium PDF Converter v{__version__}")
        self.resize(1000, 750)
        self.engine = PDFConverterEngine()
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Load Background Image
        self.bg_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "background.png"))
        
        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Override paintEvent for background drawing
        self.central_widget.paintEvent = self.paint_background
        
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Sidebar
        self.init_sidebar(main_layout)
        
        # Content Area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 4)
        
        self.init_img_to_pdf_page()
        self.init_pdf_to_img_page()
        
        self.show_img_to_pdf() # Default page
        
        self.really_close = False
        self.init_tray_icon()

        # Start background update check
        self.checker = UpdateCheckerThread(self)
        self.checker.update_available.connect(self.prompt_update)
        self.checker.start()

    def prompt_update(self, version, body, download_url):
        reply = QMessageBox.question(
            self,
            "發現新版本",
            f"發現新版本 {version}！是否要下載並安裝更新？\n\n更新內容：\n{body}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.download_and_install_update(download_url)

    def download_and_install_update(self, download_url):
        import tempfile
        temp_dir = tempfile.gettempdir()
        dest = os.path.join(temp_dir, "PDF_Converter_Setup.exe")
        
        # Disable window while downloading
        self.setEnabled(False)
        self.tray_icon.showMessage(
            "PDF Converter",
            "正在下載更新中...",
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )
        
        self.downloader = DownloaderThread(download_url, dest)
        self.downloader.download_finished.connect(self.on_download_finished)
        self.downloader.download_failed.connect(self.on_download_failed)
        self.downloader.start()

    def on_download_finished(self, dest_path):
        self.setEnabled(True)
        self.tray_icon.showMessage(
            "PDF Converter",
            "下載完成！即將開始安裝並重啟程式...",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
        try:
            # Run the installer
            os.startfile(dest_path)
            # Quit so installer can overwrite the files
            self.quit_app()
        except Exception as e:
            QMessageBox.critical(self, "更新失敗", f"無法啟動安裝程式：{str(e)}")

    def on_download_failed(self, error_msg):
        self.setEnabled(True)
        QMessageBox.warning(self, "下載失敗", f"下載更新時發生錯誤：{error_msg}")

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        
        tray_menu = QMenu(self)
        show_action = QAction("開啟 PDF Converter", self)
        show_action.triggered.connect(self.show_and_activate)
        
        exit_action = QAction("完全結束", self)
        exit_action.triggered.connect(self.quit_app)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        
    def show_and_activate(self):
        self.show()
        self.activateWindow()
        self.raise_()
        
    def on_tray_icon_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_and_activate()
            
    def quit_app(self):
        self.really_close = True
        QApplication.quit()
        
    def closeEvent(self, event):
        if not self.really_close:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "PDF Converter",
                "程式已縮小至系統匣背景執行。",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()

    def paint_background(self, event):
        painter = QPainter(self.central_widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.bg_pixmap.isNull():
            # Scale background to cover the widget
            scaled_bg = self.bg_pixmap.scaled(self.central_widget.size(), 
                                             Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                             Qt.TransformationMode.SmoothTransformation)
            # Center the background
            x = (self.central_widget.width() - scaled_bg.width()) // 2
            y = (self.central_widget.height() - scaled_bg.height()) // 2
            painter.drawPixmap(x, y, scaled_bg)
        else:
            # Fallback to solid color
            painter.fillRect(self.central_widget.rect(), QColor(Styles.BG_COLOR))

    def init_sidebar(self, layout):
        sidebar = QFrame()
        sidebar.setObjectName("GlassPanel")
        sidebar.setStyleSheet(Styles.GLASS_PANEL)
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 30)
        sidebar_layout.setSpacing(10)
        
        title = QLabel("PDF MASTER")
        title.setStyleSheet(f"QLabel {{ color: {Styles.TEXT_COLOR}; font-size: 22px; font-weight: 800; letter-spacing: 0.5px; }}")
        sidebar_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("THE ULTIMATE CONVERTER")
        subtitle.setStyleSheet(f"QLabel {{ color: {Styles.SECONDARY_TEXT}; font-size: 10px; font-weight: 600; letter-spacing: 1px; }}")
        sidebar_layout.addWidget(subtitle, 0, Qt.AlignmentFlag.AlignCenter)
        
        sidebar_layout.addSpacing(40)
        
        self.btn_img_to_pdf = GlassButton("🖼️  圖片 ➔ PDF", primary=False)
        self.btn_img_to_pdf.clicked.connect(self.show_img_to_pdf)
        sidebar_layout.addWidget(self.btn_img_to_pdf)
        
        self.btn_pdf_to_img = GlassButton("📄  PDF ➔ 圖片", primary=False)
        self.btn_pdf_to_img.clicked.connect(self.show_pdf_to_img)
        sidebar_layout.addWidget(self.btn_pdf_to_img)
        
        sidebar_layout.addStretch()
        
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        
        info_panel = QFrame()
        info_panel.setStyleSheet(f"background-color: {Styles.GLASS_BG_LIGHT}; border: 1px solid {Styles.GLASS_BORDER}; border-radius: 15px; padding: 12px;")
        info_layout = QVBoxLayout(info_panel)
        info_layout.setSpacing(10)
        
        # GitHub Icon and Name Layout
        dev_header = QHBoxLayout()
        dev_header.setSpacing(10)
        
        github_icon_label = QLabel()
        github_icon_path = os.path.join(os.path.dirname(__file__), "github_icon.png")
        if os.path.exists(github_icon_path):
            pixmap = QPixmap(github_icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            github_icon_label.setPixmap(pixmap)
        github_icon_label.setFixedSize(24, 24)
        dev_header.addWidget(github_icon_label)
        
        name_label = QLabel("ChangShuKai")
        name_label.setStyleSheet(f"QLabel {{ color: #ffffff; font-size: 14px; font-weight: 800; letter-spacing: 0.5px; }}")
        dev_header.addWidget(name_label)
        dev_header.addStretch()
        
        info_layout.addLayout(dev_header)
        
        # Action Button
        self.btn_github = GlassButton("🌐 GitHub Repo", primary=False)
        self.btn_github.setFixedHeight(35)
        custom_btn_style = Styles.SIDEBAR_BUTTON.replace(
            "font-size: 15px;", "font-size: 11px;"
        ).replace(
            "padding: 12px 15px;", "padding: 6px 15px;"
        ).replace(
            "background-color: transparent;", "background-color: rgba(255, 255, 255, 0.05);"
        )
        self.btn_github.setStyleSheet(custom_btn_style)
        self.btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ChangShuKai/PDF-Converter")))
        info_layout.addWidget(self.btn_github)
        
        sidebar_layout.addWidget(info_panel)
        
        layout.addWidget(sidebar, 1)

    def init_img_to_pdf_page(self):
        page = QFrame()
        page.setObjectName("GlassPanel")
        page.setStyleSheet(Styles.GLASS_PANEL)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        header = QVBoxLayout()
        title_label = QLabel("圖片轉 PDF")
        title_label.setStyleSheet(Styles.LABEL_TITLE)
        header.addWidget(title_label)
        
        desc_label = QLabel("將圖片拖入下方列表，拖動可自由調整順序。")
        desc_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        header.addWidget(desc_label)
        layout.addLayout(header)
        
        self.img_drop_area = FileDropArea("點擊或拖入圖片", "支援多選 | 無損高清轉換")
        self.img_drop_area.setStyleSheet(Styles.DROP_AREA)
        self.img_drop_area.filesDropped.connect(self.add_images)
        self.img_drop_area.clicked.connect(self.open_image_dialog)
        layout.addWidget(self.img_drop_area)
        
        self.img_list = DraggableListWidget()
        self.img_list.setStyleSheet(Styles.LIST_STYLE + Styles.SCROLLBAR)
        layout.addWidget(self.img_list)
        
        btn_layout = QHBoxLayout()
        self.btn_clear_imgs = GlassButton("🗑️  清空", primary=False)
        self.btn_clear_imgs.clicked.connect(self.img_list.clear)
        self.btn_clear_imgs.setFixedHeight(45)
        btn_layout.addWidget(self.btn_clear_imgs)
        
        btn_layout.addSpacing(10)
        
        self.btn_convert_img = GlassButton("🚀  開始轉換為 PDF")
        self.btn_convert_img.clicked.connect(self.convert_images_to_pdf)
        self.btn_convert_img.setFixedHeight(45)
        btn_layout.addWidget(self.btn_convert_img, 2)
        
        layout.addLayout(btn_layout)
        self.content_stack.addWidget(page)

    def init_pdf_to_img_page(self):
        page = QFrame()
        page.setObjectName("GlassPanel")
        page.setStyleSheet(Styles.GLASS_PANEL)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        header = QVBoxLayout()
        title_label = QLabel("PDF 轉圖片")
        title_label.setStyleSheet(Styles.LABEL_TITLE)
        header.addWidget(title_label)
        
        desc_label = QLabel("高效提取 PDF 頁面為高品質圖片。")
        desc_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        header.addWidget(desc_label)
        layout.addLayout(header)
        
        self.pdf_drop_area = FileDropArea("點擊或拖入 PDF", "解析速度極快 | 保持原圖解析度")
        self.pdf_drop_area.setStyleSheet(Styles.DROP_AREA)
        self.pdf_drop_area.filesDropped.connect(self.handle_pdf_drop)
        self.pdf_drop_area.clicked.connect(self.open_pdf_dialog)
        layout.addWidget(self.pdf_drop_area)
        
        info_card = QFrame()
        info_card.setStyleSheet(f"background-color: {Styles.GLASS_BG}; border: 1px solid {Styles.GLASS_BORDER}; border-radius: 12px;")
        info_card_layout = QVBoxLayout(info_card)
        self.selected_pdf_label = QLabel("尚未選擇檔案")
        self.selected_pdf_label.setStyleSheet(Styles.LABEL_SUBTITLE + f"color: {Styles.ACCENT_COLOR}; font-weight: 600;")
        self.selected_pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_card_layout.addWidget(self.selected_pdf_label)
        layout.addWidget(info_card)
        
        layout.addStretch()
        
        self.btn_convert_pdf = GlassButton("🚀  開始提取圖片")
        self.btn_convert_pdf.clicked.connect(self.convert_pdf_to_images)
        self.btn_convert_pdf.setEnabled(False)
        self.btn_convert_pdf.setFixedHeight(50)
        layout.addWidget(self.btn_convert_pdf)
        
        self.content_stack.addWidget(page)
        self.current_pdf_path = None

    def handle_cli_args(self, args):
        if not args: return
        first_file = args[0]
        if first_file.lower().endswith('.pdf'):
            self.show_pdf_to_img()
            self.handle_pdf_drop([first_file])
        else:
            self.show_img_to_pdf()
            self.add_images(args)
        
        self.activateWindow()
        self.raise_()

    def show_img_to_pdf(self):
        self.content_stack.setCurrentIndex(0)
        self.btn_img_to_pdf.set_active(True)
        self.btn_pdf_to_img.set_active(False)

    def show_pdf_to_img(self):
        self.content_stack.setCurrentIndex(1)
        self.btn_img_to_pdf.set_active(False)
        self.btn_pdf_to_img.set_active(True)

    def open_image_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "選擇圖片", "", "Image Files (*.png *.jpg *.jpeg *.webp *.bmp *.tiff)")
        if files:
            self.add_images(files)

    def open_pdf_dialog(self):
        file, _ = QFileDialog.getOpenFileName(self, "選擇 PDF", "", "PDF Files (*.pdf)")
        if file:
            self.handle_pdf_drop([file])

    def add_images(self, files):
        valid_exts = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')
        for f in files:
            if f.lower().endswith(valid_exts):
                item = QListWidgetItem(os.path.basename(f))
                item.setData(Qt.ItemDataRole.UserRole, f)
                self.img_list.addItem(item)

    def handle_pdf_drop(self, files):
        if not files: return
        pdf_file = files[0]
        if pdf_file.lower().endswith('.pdf'):
            self.current_pdf_path = pdf_file
            self.selected_pdf_label.setText(f"已選取: {os.path.basename(pdf_file)}")
            self.btn_convert_pdf.setEnabled(True)

    def convert_images_to_pdf(self):
        count = self.img_list.count()
        if count == 0:
            QMessageBox.warning(self, "提示", "請先加入圖片！")
            return
            
        image_paths = []
        for i in range(count):
            item = self.img_list.item(i)
            image_paths.append(item.data(Qt.ItemDataRole.UserRole))
            
        first_img_path = image_paths[0]
        parent_dir = os.path.dirname(first_img_path)
        base_name = os.path.splitext(os.path.basename(first_img_path))[0]
        default_path = os.path.join(parent_dir, f"{base_name}_SSC.pdf")
            
        save_path, _ = QFileDialog.getSaveFileName(self, "儲存 PDF", default_path, "PDF Files (*.pdf)")
        if save_path:
            success, msg = self.engine.images_to_pdf(image_paths, save_path)
            if success:
                QMessageBox.information(self, "成功", "PDF 轉換完成！")
            else:
                QMessageBox.critical(self, "錯誤", msg)

    def convert_pdf_to_images(self):
        base_name = os.path.splitext(os.path.basename(self.current_pdf_path))[0]
        default_folder_name = f"{base_name}_SSC"
        
        parent_dir = os.path.dirname(self.current_pdf_path)
        output_dir = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾", parent_dir)
        if output_dir:
            if os.path.normpath(output_dir) == os.path.normpath(parent_dir):
                output_dir = os.path.join(output_dir, default_folder_name)
                
            success, msg = self.engine.pdf_to_images(self.current_pdf_path, output_dir)
            if success:
                QMessageBox.information(self, "成功", "圖片提取完成！")
            else:
                QMessageBox.critical(self, "錯誤", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Check if another instance is running
    socket = QLocalSocket()
    socket.connectToServer("PDFConverterSingleInstance")
    if socket.waitForConnected(500):
        if len(sys.argv) > 1:
            args_data = json.dumps(sys.argv[1:]).encode('utf-8')
            socket.write(args_data)
            socket.waitForBytesWritten(500)
        sys.exit(0)
        
    server = QLocalServer()
    server.removeServer("PDFConverterSingleInstance")
    server.listen("PDFConverterSingleInstance")
    
    # Modern font - try to use Inter or Segoe UI
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ModernPDFConverter()
    
    def handle_new_connection():
        client = server.nextPendingConnection()
        if client.waitForReadyRead(500):
            data = client.readAll().data().decode('utf-8')
            try:
                args = json.loads(data)
                window.handle_cli_args(args)
            except Exception as e:
                pass
        client.disconnectFromServer()
        
    server.newConnection.connect(handle_new_connection)
    
    if len(sys.argv) > 1:
        window.handle_cli_args(sys.argv[1:])
        
    window.show()
    window.activateWindow()
    window.raise_()
    sys.exit(app.exec())
