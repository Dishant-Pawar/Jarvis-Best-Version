import os
import subprocess
import winreg
from jarvis.utils.logger import logger

def get_registry_value(key_path, value_name):
    """Retrieve installation path of an app from Windows registry."""
    try:
        # Check both Current User and Local Machine
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
                    val, _ = winreg.QueryValueEx(key, value_name)
                    return val
            except FileNotFoundError:
                continue
    except Exception as e:
        logger.debug(f"Registry lookup failed for {key_path}: {e}")
    return None

def find_chrome():
    """Locate Google Chrome executable path."""
    # Method 1: Check Registry
    reg_path = get_registry_value(r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe", "")
    if reg_path and os.path.exists(reg_path):
        return reg_path
        
    # Method 2: Common Paths
    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return "chrome.exe"  # fallback to PATH

def find_vscode():
    """Locate Visual Studio Code executable path."""
    # Method 1: Check Registry
    reg_path = get_registry_value(r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\code.exe", "")
    if reg_path and os.path.exists(reg_path):
        return reg_path

    # Method 2: Common Paths
    common_paths = [
        os.path.expandvars(r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return "code"  # fallback to PATH

class SystemApps:
    @staticmethod
    def open_notepad() -> bool:
        """Launch Notepad."""
        try:
            logger.info("Opening Notepad...")
            subprocess.Popen("notepad.exe")
            return True
        except Exception as e:
            logger.error(f"Failed to open Notepad: {e}")
            return False

    @staticmethod
    def open_calculator() -> bool:
        """Launch Calculator."""
        try:
            logger.info("Opening Calculator...")
            subprocess.Popen("calc.exe")
            return True
        except Exception as e:
            logger.error(f"Failed to open Calculator: {e}")
            return False

    @staticmethod
    def open_command_prompt() -> bool:
        """Launch Command Prompt in a new window."""
        try:
            logger.info("Opening Command Prompt...")
            subprocess.Popen("cmd.exe", creationflags=subprocess.CREATE_NEW_CONSOLE)
            return True
        except Exception as e:
            logger.error(f"Failed to open Command Prompt: {e}")
            return False

    @staticmethod
    def open_file_explorer() -> bool:
        """Launch File Explorer."""
        try:
            logger.info("Opening File Explorer...")
            subprocess.Popen("explorer.exe")
            return True
        except Exception as e:
            logger.error(f"Failed to open File Explorer: {e}")
            return False

    @staticmethod
    def open_control_panel() -> bool:
        """Launch Control Panel."""
        try:
            logger.info("Opening Control Panel...")
            subprocess.Popen("control.exe")
            return True
        except Exception as e:
            logger.error(f"Failed to open Control Panel: {e}")
            return False

    @staticmethod
    def open_settings() -> bool:
        """Launch Windows Settings app."""
        try:
            logger.info("Opening Windows Settings...")
            # ms-settings is a protocol to open settings app directly
            os.system("start ms-settings:")
            return True
        except Exception as e:
            logger.error(f"Failed to open Settings: {e}")
            return False

    @staticmethod
    def open_camera() -> bool:
        """Launch Windows Camera app."""
        try:
            logger.info("Opening Camera...")
            # microsoft.windows.camera is a protocol to open camera app directly
            os.system("start microsoft.windows.camera:")
            return True
        except Exception as e:
            logger.error(f"Failed to open Camera: {e}")
            return False

    @staticmethod
    def open_chrome() -> bool:
        """Launch Google Chrome."""
        try:
            logger.info("Opening Google Chrome...")
            chrome_path = find_chrome()
            subprocess.Popen([chrome_path])
            return True
        except Exception as e:
            logger.error(f"Failed to open Chrome: {e}")
            # Try basic shell launch
            try:
                os.system("start chrome")
                return True
            except Exception:
                return False

    @staticmethod
    def open_vscode() -> bool:
        """Launch Visual Studio Code."""
        try:
            logger.info("Opening VS Code...")
            vscode_path = find_vscode()
            # If path ends with code, run with shell=True because it's a cmd wrapper
            if vscode_path == "code":
                subprocess.Popen("code", shell=True)
            else:
                subprocess.Popen([vscode_path])
            return True
        except Exception as e:
            logger.error(f"Failed to open VS Code: {e}")
            return False
