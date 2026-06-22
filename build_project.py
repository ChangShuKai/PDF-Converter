import os
import shutil
import zipfile
import subprocess

def clean_dirs():
    print("Cleaning build and dist directories...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"Warning: Could not remove {folder}: {e}")

def build_app():
    print("Building main application (onedir mode)...")
    # Command to build the main app in onedir mode
    cmd = [
        "pyinstaller",
        "--onedir",
        "--noconsole",
        "--name", "PDF Converter",
        "--icon", "icon.ico",
        "--add-data", "icon.ico;.",
        "--add-data", "icon.png;.",
        "--add-data", "background.png;.",
        "--add-data", "github_icon.png;.",
        "main.py",
        "-y"
    ]
    subprocess.run(cmd, check=True)

def zip_app():
    print("Creating app.zip...")
    zip_path = "app.zip"
    src_dir = os.path.join("dist", "PDF Converter")
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # We want the zip file structure to start from the contents of the 'PDF Converter' folder
                arcname = os.path.relpath(file_path, src_dir)
                zip_file.write(file_path, arcname)
    print(f"app.zip created at {os.path.abspath(zip_path)}")

def build_installer():
    print("Building installer (onefile mode)...")
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", "PDF Converter Setup",
        "--icon", "icon.ico",
        "--add-data", "app.zip;.",
        "--add-data", "icon.ico;.",
        "installer.py",
        "-y"
    ]
    subprocess.run(cmd, check=True)

def main():
    try:
        clean_dirs()
        build_app()
        zip_app()
        build_installer()
        
        # Cleanup app.zip
        if os.path.exists("app.zip"):
            os.remove("app.zip")
            print("Cleaned up temporary app.zip")
            
        print("\nBuild process complete! Your installer is located at dist/PDF Converter Setup.exe")
    except Exception as e:
        print(f"Error during build process: {e}")

if __name__ == "__main__":
    main()
