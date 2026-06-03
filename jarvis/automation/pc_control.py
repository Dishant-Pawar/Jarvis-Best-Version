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
        """Take a full-screen screenshot and save it to the project's screenshots directory.
        Returns the file path of the saved screenshot, or an empty string on failure.
        """
        try:
            # Import pyautogui lazily to avoid import errors if the library is missing.
            try:
                import pyautogui
            except ImportError as ie:
                logger.error(f"pyautogui is required for screenshots but is not installed: {ie}")
                return ""

            # Determine the screenshots directory within the project.
            screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "screenshots"))
            os.makedirs(screenshots_dir, exist_ok=True)

            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(screenshots_dir, filename)
            logger.info(f"Capturing screenshot to {filepath}")

            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""
    @staticmethod
    def screenshort() -> str:
        """Alias for take_screenshot."""
        return PCControl.take_screenshot()

    @staticmethod
    def toggle_wifi(enable: bool) -> bool:
        """Enable or disable Wi-Fi using PowerShell (Radio API + netsh fallback)."""
        state = "On" if enable else "Off"
        logger.info(f"Turning Wi-Fi {state}")
        
        # Primary: try the PowerShell script (Radio API + netsh fallback)
        try:
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "toggle_radio.ps1"))
            cmd = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -RadioKind WiFi -State {state}'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            logger.info(f"WiFi toggle stdout: {res.stdout.strip()}")
            if res.returncode == 0:
                return True
            logger.warning(f"WiFi PS1 failed (rc={res.returncode}): {res.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.warning("WiFi PowerShell script timed out.")
        except Exception as e:
            logger.warning(f"WiFi PS1 script error: {e}")

        # Fallback: direct netsh command
        try:
            action = "enabled" if enable else "disabled"
            for iface in ["Wi-Fi", "WiFi", "Wireless Network Connection"]:
                r = subprocess.run(
                    f'netsh interface set interface "{iface}" {action}',
                    shell=True, capture_output=True, text=True, timeout=8
                )
                if r.returncode == 0:
                    logger.info(f"Wi-Fi {action} via netsh interface '{iface}'")
                    return True
            logger.error("All netsh Wi-Fi fallback attempts failed.")
        except Exception as e:
            logger.error(f"WiFi netsh fallback error: {e}")

        return False

    @staticmethod
    def toggle_bluetooth(enable: bool) -> bool:
        """Enable or disable Bluetooth using PowerShell (Radio API + service fallback)."""
        state = "On" if enable else "Off"
        logger.info(f"Turning Bluetooth {state}")

        # Primary: try the PowerShell script
        try:
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "toggle_radio.ps1"))
            cmd = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -RadioKind Bluetooth -State {state}'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            logger.info(f"Bluetooth toggle stdout: {res.stdout.strip()}")
            if res.returncode == 0:
                return True
            logger.warning(f"Bluetooth PS1 failed (rc={res.returncode}): {res.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.warning("Bluetooth PowerShell script timed out.")
        except Exception as e:
            logger.warning(f"Bluetooth PS1 script error: {e}")

        # Fallback: toggle Bluetooth via Windows service (bthserv) and PnP
        try:
            if enable:
                ps_cmd = (
                    'powershell -Command "'
                    'Start-Service bthserv -ErrorAction SilentlyContinue; '
                    '$devs = Get-PnpDevice | Where-Object {$_.FriendlyName -match \'Bluetooth\' -and $_.Status -ne \'OK\'}; '
                    'foreach ($d in $devs) { Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction SilentlyContinue }'
                    '"'
                )
            else:
                ps_cmd = (
                    'powershell -Command "'
                    'Stop-Service bthserv -Force -ErrorAction SilentlyContinue; '
                    '$devs = Get-PnpDevice | Where-Object {$_.FriendlyName -match \'Bluetooth\' -and $_.Status -eq \'OK\'}; '
                    'foreach ($d in $devs) { Disable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction SilentlyContinue }'
                    '"'
                )
            r = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True, timeout=20)
            logger.info(f"Bluetooth service fallback stdout: {r.stdout.strip()}")
            return True  # Best-effort
        except Exception as e:
            logger.error(f"Bluetooth service fallback error: {e}")

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
