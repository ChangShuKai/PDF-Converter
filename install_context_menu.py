import winreg
import os
import sys

def add_context_menu():
    # Paths
    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable
        
    main_py = os.path.abspath("main.py")
    icon_path = os.path.abspath("icon.ico")
    
    command = f'"{python_exe}" "{main_py}" "%1"'
    
    print(f"Using Command: {command}")

    # 1. Add context menu for PDF files
    try:
        pdf_key_path = r"Software\Classes\SystemFileAssociations\.pdf\shell\PDFConverter"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, pdf_key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "用 PDF Converter 轉成圖片")
        if os.path.exists(icon_path):
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f'"{icon_path}"')
        
        command_key = winreg.CreateKey(key, "command")
        winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        print("Successfully added to PDF context menu")
    except Exception as e:
        print(f"Error adding PDF context menu: {e}")

    # 2. Add context menu for Image files
    image_extensions = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]
    
    try:
        # Instead of generic 'image' which might not trigger properly, 
        # let's add it to SystemFileAssociations\image
        img_key_path = r"Software\Classes\SystemFileAssociations\image\shell\PDFConverter"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, img_key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "加入 PDF Converter")
        if os.path.exists(icon_path):
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f'"{icon_path}"')
        
        command_key = winreg.CreateKey(key, "command")
        winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        print("Successfully added to Image context menu")
    except Exception as e:
        print(f"Error adding Image context menu: {e}")
        
    print("\n完成！現在您可以在圖片或 PDF 檔案上點擊右鍵（Windows 11 可能需要點擊「顯示其他選項」），即可看到捷徑。")

if __name__ == "__main__":
    add_context_menu()
