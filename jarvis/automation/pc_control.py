import os
import sys
import ctypes
import subprocess
from datetime import datetime
from jarvis.utils.logger import logger

class PCControl:
    @staticmethod
    def _init_com():
        """Initialize COM library. Required for pycaw/winshell in threads."""
        import pythoncom
        pythoncom.CoInitialize()

    @staticmethod
    def _uninit_com():
        """Uninitialize COM library."""
        import pythoncom
        pythoncom.CoUninitialize()

    @classmethod
    def change_volume(cls, amount: int) -> bool:
        """Increase or decrease volume by a relative percent (e.g. +10 or -10)."""
        cls._init_com()
        try:
            from pycaw.pycaw import AudioUtilities

            logger.info(f"Adjusting volume by {amount}%")
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume

            current_vol = volume.GetMasterVolumeLevelScalar()
            new_vol = max(0.0, min(1.0, current_vol + (amount / 100.0)))
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            logger.info(f"Volume set from {int(current_vol*100)}% to {int(new_vol*100)}%")
            return True
        except Exception as e:
            logger.error(f"Failed to change volume: {e}")
            return False
        finally:
            cls._uninit_com()

    @classmethod
    def mute_audio(cls, mute: bool = True) -> bool:
        """Mute or unmute the system speakers."""
        cls._init_com()
        try:
            from pycaw.pycaw import AudioUtilities

            logger.info(f"Setting mute to {mute}")
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume

            volume.SetMute(1 if mute else 0, None)
            logger.info(f"System audio {'muted' if mute else 'unmuted'}")
            return True
        except Exception as e:
            logger.error(f"Failed to toggle mute: {e}")
            return False
        finally:
            cls._uninit_com()

    @staticmethod
    def change_brightness(amount: int) -> bool:
        """Increase or decrease screen brightness by a relative percent (e.g. +15 or -15)."""
        try:
            import screen_brightness_control as sbc
            current = sbc.get_brightness()
            if isinstance(current, list):
                current = current[0]
            
            new_brightness = max(0, min(100, current + amount))
            logger.info(f"Adjusting brightness from {current}% to {new_brightness}%")
            sbc.set_brightness(new_brightness)
            return True
        except Exception as e:
            logger.error(f"Failed to change screen brightness: {e}")
            return False

    @staticmethod
    def take_screenshot() -> str:
        """Take a full-screen screenshot and save it to the user's Desktop."""
        try:
            import pyautogui
            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = f"Screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(desktop_dir, filename)
            
            logger.info(f"Taking screenshot: {filepath}")
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""

    @staticmethod
    def toggle_wifi(enable: bool) -> bool:
        """Enable or disable Wi-Fi adapter using powershell/netsh."""
        try:
            status = "enabled" if enable else "disabled"
            logger.info(f"Turning Wi-Fi {status}")
            # Try netsh (which may require admin depending on OS configuration)
            cmd = f'netsh interface set interface name="Wi-Fi" admin={status}'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                return True
                
            # Try powershell fallback
            ps_status = "Enable" if enable else "Disable"
            ps_cmd = f'powershell -Command "{ps_status}-NetAdapter -Name \'Wi-Fi\' -Confirm:$false"'
            res = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
            return res.returncode == 0
        except Exception as e:
            logger.error(f"Failed to toggle Wi-Fi: {e}")
            return False

    @staticmethod
    def toggle_bluetooth(enable: bool) -> bool:
        """Enable or disable Bluetooth radio using Powershell."""
        try:
            logger.info(f"Turning Bluetooth {'on' if enable else 'off'}")
            # Windows Bluetooth control is exposed via Windows.Devices.Radios API.
            # We can invoke it from Powershell.
            ps_status = "On" if enable else "Off"
            # Command imports Assemblies to toggle Bluetooth radio
            ps_script = (
                "[void][Reference.Assembly]::LoadWithPartialName('System.Runtime.WindowsRuntime'); "
                "$asb = [System.Runtime.InteropServices.WindowsRuntime.WebAuthenticationBroker]; "
                "$radioType = [Windows.Devices.Radios.RadioKind]::Bluetooth; "
                "$radios = [Windows.Devices.Radios.Radio]::GetRadiosAsync().GetResults(); "
                f"$bt = $radios | Where-Object {{ $_.Kind -eq $radioType }}; "
                f"if ($bt) {{ $bt.SetStateAsync([Windows.Devices.Radios.RadioState]::{ps_status}).GetResults(); }}"
            )
            cmd = f'powershell -Command "{ps_script}"'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.returncode == 0
        except Exception as e:
            logger.error(f"Failed to toggle Bluetooth: {e}")
            return False

    @staticmethod
    def lock_pc() -> bool:
        """Lock the Windows workstation."""
        try:
            logger.info("Locking PC...")
            ctypes.windll.user32.LockWorkStation()
            return True
        except Exception as e:
            logger.error(f"Failed to lock PC: {e}")
            return False

    @staticmethod
    def sleep_mode() -> bool:
        """Put Windows to sleep."""
        try:
            logger.info("Putting system to sleep...")
            # SetSuspendState: suspend=True, force=False, disableWake=False
            # Present in powrprof.dll
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to put PC to sleep: {e}")
            # Try powershell backup
            try:
                subprocess.run('powershell -Command "Add-Type -Assembly PresentationCore; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)"', shell=True)
                return True
            except Exception:
                return False

    @staticmethod
    def shutdown_pc() -> bool:
        """Shut down the computer in 10 seconds."""
        try:
            logger.warning("Initiating Shutdown...")
            # /s shutdown, /t 10 delay of 10s
            subprocess.run("shutdown /s /t 10", shell=True)
            return True
        except Exception as e:
            logger.error(f"Failed to initiate shutdown: {e}")
            return False

    @staticmethod
    def restart_pc() -> bool:
        """Restart the computer in 10 seconds."""
        try:
            logger.warning("Initiating Restart...")
            # /r restart, /t 10 delay of 10s
            subprocess.run("shutdown /r /t 10", shell=True)
            return True
        except Exception as e:
            logger.error(f"Failed to initiate restart: {e}")
            return False
