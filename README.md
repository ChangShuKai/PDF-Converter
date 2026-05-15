# 🚀 Premium PDF Converter | 極致無損 PDF 助手

這是一款基於 **PyQt6** 開發的現代化桌面應用程式，專為追求效率與畫質的用戶打造。它提供直觀的「磨砂玻璃」視覺介面，支援圖片與 PDF 之間的高清無損雙向轉換。

## ✨ 核心功能

* **🖼️ 圖片轉 PDF (無損)**
* 支援多格式批量導入（JPG, PNG, WEBP, BMP, TIFF）。
* **自由排序**：透過拖拽輕鬆調整圖片在 PDF 中的先後順序。
* **無損封裝**：保持原始圖片解析度，不進行強制壓縮。


* **📄 PDF 轉圖片 (高清)**
* 高速解析技術，將 PDF 頁面提取為高品質圖像。
* 自動建立專屬資料夾，保持檔案井然有序。


* **🎨 現代化 UI 設計**
* **Glassmorphism**：流暢的磨砂玻璃質感介面。
* **拖放支援**：直接將檔案拖入視窗即可開始操作。
* **響應式佈局**：適應不同螢幕尺寸。



## 🛠️ 技術棧

* **GUI 框架**: PyQt6
* **轉換引擎**: PDFConverterEngine (自定義核心)
* **樣式控制**: QSS (Qt Style Sheets)
* **字體**: Segoe UI / 微軟正黑體

## 📦 安裝說明

1. **複製專案**
```bash
git clone https://github.com/your-username/pdf-converter.git
cd pdf-converter

```


2. **安裝依賴**
請確保已安裝 Python 3.8+，然後執行：
```bash
pip install PyQt6
# 根據你的 engine 需求可能還需要安裝：
# pip install Pillow PyMuPDF

```


3. **執行程式**
```bash
python main.py

```



## 🖥️ 檔案結構說明

* `main.py`: 程式進入點，負責主視窗邏輯與導航。
* `styles.py`: 存放 `Styles` 類別，管理全局 QSS 樣式。
* `ui_components.py`: 自定義 UI 元件（如可拖拽列表、拖放區域、玻璃按鈕）。
* `converter_engine.py`: 處理 PDF 轉換的核心邏輯。

## 📝 備註

本工具由 **Six Star Culture (SSC)** 開發維護，旨在提供最純淨、無廣告、無浮水印的 PDF 工具體驗。
