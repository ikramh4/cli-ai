import PyInstaller.__main__
import os
import time
import shutil

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
dist_path = os.path.join(current_dir, "dist")
exe_path = os.path.join(dist_path, "CLI-Bot.exe")

# Try to remove existing exe if it exists
if os.path.exists(exe_path):
    try:
        os.remove(exe_path)
    except PermissionError:
        print("Waiting for existing exe to be released...")
        time.sleep(2)  # Wait a bit
        try:
            # Try to rename first (Windows trick to force release)
            temp_path = exe_path + '.old'
            if os.path.exists(temp_path):
                os.remove(temp_path)
            os.rename(exe_path, temp_path)
            os.remove(temp_path)
        except:
            print("Could not remove existing exe. Please close CLI-Bot and try again.")
            exit(1)

# Clean build directory
build_dir = os.path.join(current_dir, "build")
if os.path.exists(build_dir):
    shutil.rmtree(build_dir, ignore_errors=True)

# Run PyInstaller
PyInstaller.__main__.run([
    'cli-ai.py',
    '--name=CLI-Bot',
    '--onefile',
    '--noconsole',
    '--add-data=src;src',
    '--add-data=nh.png;.',
    '--icon=nh.png',
    '--clean',
    f'--distpath={dist_path}',
    f'--workpath={build_dir}',
    '--noconfirm',
]) 