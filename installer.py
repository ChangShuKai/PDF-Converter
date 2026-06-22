import os
import sys
import shutil
import winreg
import ctypes
import zipfile

def create_shortcut(target, shortcut_path, icon=None):
    vbs_path = os.path.join(os.environ["TEMP"], "create_shortcut.vbs")
    vbs_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target}"
oLink.WorkingDirectory = "{os.path.dirname(target)}"
"""
    if icon:
        vbs_content += f'oLink.IconLocation = "{icon}"\n'
    vbs_content += "oLink.Save\n"
    
    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(vbs_content)
        
    os.system(f'cscript //nologo "{vbs_path}"')
    try:
        os.remove(vbs_path)
    except:
        pass

def install():
    try:
        local_app_data = os.environ.get("LOCALAPPDATA")
        app_dir = os.path.join(local_app_data, "Programs", "PDF Converter")
        
        # Kill running instances first
        os.system('taskkill /f /im "PDF Converter.exe" >nul 2>&1')
        
        # Recreate target directory
        if os.path.exists(app_dir):
            try:
                shutil.rmtree(app_dir)
            except Exception as e:
                pass
        
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
            
        exe_dest = os.path.join(app_dir, "PDF Converter.exe")
        icon_dest = os.path.join(app_dir, "icon.ico")
        uninstall_bat_dest = os.path.join(app_dir, "uninstall.bat")
        
        # Extract files from app.zip
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        zip_src = os.path.join(base_path, "app.zip")
        
        if not os.path.exists(zip_src):
            ctypes.windll.user32.MessageBoxW(0, f"無法找到安裝封裝檔案: {zip_src}", "安裝失敗", 0)
            return

        with zipfile.ZipFile(zip_src, 'r') as zip_ref:
            zip_ref.extractall(app_dir)
            
        # Copy icon.ico to app_dir if it's in package root
        icon_src = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_src):
            shutil.copy2(icon_src, icon_dest)
        else:
            icon_dest = exe_dest
            
        # Write uninstall.bat
        uninstall_vbs_shortcut_del = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "PDF Converter.lnk").replace("\\", "\\\\")
        uninstall_sendto_shortcut_del = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "SendTo", "PDF Converter.lnk").replace("\\", "\\\\")
        uninstall_desktop_shortcut_del = os.path.join(os.environ["USERPROFILE"], "Desktop", "PDF Converter.lnk").replace("\\", "\\\\")
        
        uninstall_bat_content = f"""@echo off
chcp 65001 > nul
echo 正在準備解除安裝 PDF Converter...
taskkill /f /im "PDF Converter.exe" >nul 2>&1
timeout /t 1 /nobreak > nul

:: Copy cleanup script to temp and run it to delete this folder
set TEMP_BAT=%TEMP%\\pdf_converter_cleanup.bat
(
echo @echo off
echo timeout /t 1 /nobreak ^> nul
echo rmdir /s /q "{app_dir}"
echo del "{uninstall_vbs_shortcut_del}"
echo del "{uninstall_sendto_shortcut_del}"
echo del "{uninstall_desktop_shortcut_del}"
echo reg delete "HKCU\\Software\\Classes\\SystemFileAssociations\\.pdf\\shell\\PDFConverter" /f ^>nul 2^>^&1
echo reg delete "HKCU\\Software\\Classes\\SystemFileAssociations\\image\\shell\\PDFConverter" /f ^>nul 2^>^&1
echo reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PDFConverter" /f ^>nul 2^>^&1
echo echo PDF Converter 已成功從您的系統中移除。
echo pause
echo del "%%~f0"
) > "%TEMP_BAT%"

start "" "%TEMP_BAT%"
exit
"""
        with open(uninstall_bat_dest, "w", encoding="utf-8") as f:
            f.write(uninstall_bat_content)

        # 1. Start Menu Shortcut
        start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
        shortcut_path = os.path.join(start_menu, "PDF Converter.lnk")
        create_shortcut(exe_dest, shortcut_path, icon_dest)
        
        # 2. Desktop Shortcut
        desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
        desktop_shortcut = os.path.join(desktop, "PDF Converter.lnk")
        create_shortcut(exe_dest, desktop_shortcut, icon_dest)
        
        # 3. SendTo Shortcut
        sendto_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "SendTo")
        sendto_shortcut = os.path.join(sendto_dir, "PDF Converter.lnk")
        create_shortcut(exe_dest, sendto_shortcut, icon_dest)

        # 4. Registry Context Menu
        command = f'"{exe_dest}" "%1"'
        
        # PDF
        try:
            pdf_key_path = r"Software\Classes\SystemFileAssociations\.pdf\shell\PDFConverter"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, pdf_key_path)
            winreg.SetValue(key, "", winreg.REG_SZ, "用 PDF Converter 轉成圖片")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f'"{icon_dest}"')
            winreg.SetValueEx(key, "MultiSelectModel", 0, winreg.REG_SZ, "Player")
            
            command_key = winreg.CreateKey(key, "command")
            winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        except Exception as e:
            pass

        # Image
        try:
            img_key_path = r"Software\Classes\SystemFileAssociations\image\shell\PDFConverter"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, img_key_path)
            winreg.SetValue(key, "", winreg.REG_SZ, "加入 PDF Converter")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f'"{icon_dest}"')
            winreg.SetValueEx(key, "MultiSelectModel", 0, winreg.REG_SZ, "Player")
            
            command_key = winreg.CreateKey(key, "command")
            winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        except Exception as e:
            pass

        # 5. Registry Control Panel Uninstaller (Standard User HKCU)
        try:
            uninst_key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\PDFConverter"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, uninst_key_path)
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "PDF Converter")
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstall_bat_dest}"')
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, f'"{exe_dest}"')
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.1.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "ChangShuKai")
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        except Exception as e:
            pass

        ctypes.windll.user32.MessageBoxW(0, "安裝成功！\n- 已新增至開始功能表與桌面捷徑\n- 已新增至「傳送到」(Send to) 選單 (完美支援大量多選)\n- 已新增至右鍵選單\n- 支援控制台解除安裝", "PDF Converter 安裝程式", 0)
        
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f"安裝發生錯誤：{str(e)}", "安裝失敗", 0)

if __name__ == "__main__":
    install()
