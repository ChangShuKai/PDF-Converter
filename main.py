import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFileDialog, QStackedWidget,
                             QListWidgetItem, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap

from styles import Styles
from ui_components import DraggableListWidget, FileDropArea, GlassButton
from converter_engine import PDFConverterEngine

class ModernPDFConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Premium PDF Converter")
        self.resize(900, 700)
        self.engine = PDFConverterEngine()
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set Global Styles
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Sidebar
        self.init_sidebar(main_layout)
        
        # Content Area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 4)
        
        self.init_img_to_pdf_page()
        self.init_pdf_to_img_page()
        
        self.show_img_to_pdf() # Default page

    def init_sidebar(self, layout):
        sidebar = QFrame()
        sidebar.setObjectName("GlassPanel")
        sidebar.setStyleSheet(Styles.GLASS_PANEL)
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(15)
        
        title = QLabel("PDF 助手")
        title.setStyleSheet(Styles.LABEL_TITLE + "font-size: 20px;")
        sidebar_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("極致無損轉換")
        subtitle.setStyleSheet(Styles.LABEL_SUBTITLE)
        sidebar_layout.addWidget(subtitle, 0, Qt.AlignmentFlag.AlignCenter)
        
        sidebar_layout.addSpacing(30)
        
        self.btn_img_to_pdf = GlassButton("🖼️ 圖片 ➔ PDF")
        self.btn_img_to_pdf.clicked.connect(self.show_img_to_pdf)
        sidebar_layout.addWidget(self.btn_img_to_pdf)
        
        self.btn_pdf_to_img = GlassButton("📄 PDF ➔ 圖片")
        self.btn_pdf_to_img.clicked.connect(self.show_pdf_to_img)
        sidebar_layout.addWidget(self.btn_pdf_to_img)
        
        sidebar_layout.addStretch()
        
        info_label = QLabel("v1.1 Stable\nBy Six Star Culture\nPDF Converter")
        info_label.setStyleSheet(Styles.LABEL_SUBTITLE + "font-size: 11px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(info_label)
        
        layout.addWidget(sidebar, 1)

    def init_img_to_pdf_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title_label = QLabel("圖片轉 PDF (無損)")
        title_label.setStyleSheet(Styles.LABEL_TITLE)
        layout.addWidget(title_label)
        
        desc_label = QLabel("將圖片拖入下方列表，拖動可調整順序。")
        desc_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        layout.addWidget(desc_label)
        
        self.img_drop_area = FileDropArea("點擊或拖入圖片", "支援 JPG, PNG, WEBP 等多選")
        self.img_drop_area.setStyleSheet(Styles.DROP_AREA)
        self.img_drop_area.filesDropped.connect(self.add_images)
        self.img_drop_area.clicked.connect(self.open_image_dialog)
        layout.addWidget(self.img_drop_area)
        
        self.img_list = DraggableListWidget()
        self.img_list.setStyleSheet(Styles.LIST_STYLE + Styles.SCROLLBAR)
        layout.addWidget(self.img_list)
        
        btn_layout = QHBoxLayout()
        self.btn_clear_imgs = GlassButton("🗑️ 清空列表")
        self.btn_clear_imgs.clicked.connect(self.img_list.clear)
        btn_layout.addWidget(self.btn_clear_imgs)
        
        self.btn_convert_img = GlassButton("🚀 開始轉換為 PDF")
        self.btn_convert_img.clicked.connect(self.convert_images_to_pdf)
        btn_layout.addWidget(self.btn_convert_img)
        
        layout.addLayout(btn_layout)
        self.content_stack.addWidget(page)

    def init_pdf_to_img_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title_label = QLabel("PDF 轉圖片 (高清)")
        title_label.setStyleSheet(Styles.LABEL_TITLE)
        layout.addWidget(title_label)
        
        desc_label = QLabel("將 PDF 檔案拖入下方或點擊選擇。")
        desc_label.setStyleSheet(Styles.LABEL_SUBTITLE)
        layout.addWidget(desc_label)
        
        self.pdf_drop_area = FileDropArea("點擊或拖入 PDF", "解析速度極快")
        self.pdf_drop_area.setStyleSheet(Styles.DROP_AREA)
        self.pdf_drop_area.filesDropped.connect(self.handle_pdf_drop)
        self.pdf_drop_area.clicked.connect(self.open_pdf_dialog)
        layout.addWidget(self.pdf_drop_area)
        
        self.selected_pdf_label = QLabel("尚未選擇檔案")
        self.selected_pdf_label.setStyleSheet(Styles.LABEL_SUBTITLE + "color: #38bdf8;")
        layout.addWidget(self.selected_pdf_label)
        
        layout.addStretch()
        
        self.btn_convert_pdf = GlassButton("🚀 開始提取圖片")
        self.btn_convert_pdf.clicked.connect(self.convert_pdf_to_images)
        self.btn_convert_pdf.setEnabled(False)
        layout.addWidget(self.btn_convert_pdf)
        
        self.content_stack.addWidget(page)
        self.current_pdf_path = None

    def show_img_to_pdf(self):
        self.content_stack.setCurrentIndex(0)
        self.btn_img_to_pdf.setProperty("active", True)
        self.btn_pdf_to_img.setProperty("active", False)

    def show_pdf_to_img(self):
        self.content_stack.setCurrentIndex(1)
        self.btn_img_to_pdf.setProperty("active", False)
        self.btn_pdf_to_img.setProperty("active", True)

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
            self.selected_pdf_label.setText(f"已選擇: {os.path.basename(pdf_file)}")
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
            
        # Auto-generate default name from the first image
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
        # Auto-generate default folder name from the PDF
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
    
    # Modern font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ModernPDFConverter()
    window.show()
    sys.exit(app.exec())
