import winreg
import os

def remove_context_menu():
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\SystemFileAssociations\.pdf\shell\PDFConverter\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\SystemFileAssociations\.pdf\shell\PDFConverter")
        print("Successfully removed from PDF context menu")
    except Exception as e:
        print(f"Error removing PDF context menu (or it wasn't installed): {e}")

    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\SystemFileAssociations\image\shell\PDFConverter\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\SystemFileAssociations\image\shell\PDFConverter")
        print("Successfully removed from Image context menu")
    except Exception as e:
        print(f"Error removing Image context menu (or it wasn't installed): {e}")
        
    print("\n已移除右鍵選單捷徑。")

if __name__ == "__main__":
    remove_context_menu()
