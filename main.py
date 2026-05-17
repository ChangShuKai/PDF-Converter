import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFileDialog, QStackedWidget,
                             QListWidgetItem, QMessageBox, QFrame, QPushButton)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QBrush, QColor

from styles import Styles
from ui_components import DraggableListWidget, FileDropArea, GlassButton
from converter_engine import PDFConverterEngine

class ModernPDFConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Premium PDF Converter")
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
        title.setStyleSheet(Styles.LABEL_TITLE + "font-size: 22px;")
        sidebar_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("THE ULTIMATE CONVERTER")
        subtitle.setStyleSheet(Styles.LABEL_SUBTITLE + "font-size: 10px; font-weight: 600; letter-spacing: 1px;")
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
        name_label.setStyleSheet(Styles.LABEL_TITLE + "font-size: 14px; color: #ffffff;")
        dev_header.addWidget(name_label)
        dev_header.addStretch()
        
        info_layout.addLayout(dev_header)
        
        # Action Button
        self.btn_github = GlassButton("🌐 GitHub Repo", primary=False)
        self.btn_github.setFixedHeight(35)
        self.btn_github.setStyleSheet(self.btn_github.styleSheet() + "font-size: 11px; background-color: rgba(255,255,255,0.05);")
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
        base_name = os.path.splitext(os.path.basename(first_img_path))[0]
        default_name = f"{base_name}_SSC.pdf"
            
        save_path, _ = QFileDialog.getSaveFileName(self, "儲存 PDF", default_name, "PDF Files (*.pdf)")
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
        output_dir = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾", os.path.join(parent_dir, default_folder_name))
        if output_dir:
            success, msg = self.engine.pdf_to_images(self.current_pdf_path, output_dir)
            if success:
                QMessageBox.information(self, "成功", "圖片提取完成！")
            else:
                QMessageBox.critical(self, "錯誤", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Modern font - try to use Inter or Segoe UI
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ModernPDFConverter()
    window.show()
    sys.exit(app.exec())
