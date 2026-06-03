import os
import shutil
import winshell
from typing import List, Optional
from jarvis.utils.logger import logger

class FileManager:
    # Buffer to hold path of copied item
    _clipboard_path: Optional[str] = None
    _clipboard_is_cut: bool = False

    @staticmethod
    def _init_com():
        import pythoncom
        pythoncom.CoInitialize()

    @staticmethod
    def _uninit_com():
        import pythoncom
        pythoncom.CoUninitialize()

    @staticmethod
    def get_downloads_path() -> str:
        """Get the user's Downloads folder path."""
        # Standard location
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(downloads):
            return downloads
        return os.path.expanduser("~")

    @classmethod
    def open_downloads_folder(cls) -> bool:
        """Open the Downloads folder in File Explorer."""
        try:
            path = cls.get_downloads_path()
            logger.info(f"Opening Downloads folder: {path}")
            os.startfile(path)
            return True
        except Exception as e:
            logger.error(f"Failed to open Downloads folder: {e}")
            return False

    @staticmethod
    def open_folder(path: str) -> bool:
        """Open a directory in File Explorer."""
        try:
            path = os.path.abspath(os.path.expanduser(path))
            if os.path.exists(path) and os.path.isdir(path):
                logger.info(f"Opening folder: {path}")
                os.startfile(path)
                return True
            logger.warning(f"Folder does not exist or is not a directory: {path}")
            return False
        except Exception as e:
            logger.error(f"Failed to open folder '{path}': {e}")
            return False

    @staticmethod
    def open_specific_file(path: str) -> bool:
        """Open a specific file with its default system application."""
        try:
            path = os.path.abspath(os.path.expanduser(path))
            if os.path.exists(path) and os.path.isfile(path):
                logger.info(f"Opening file: {path}")
                os.startfile(path)
                return True
            logger.warning(f"File does not exist or is not a file: {path}")
            return False
        except Exception as e:
            logger.error(f"Failed to open file '{path}': {e}")
            return False

    @staticmethod
    def create_file(path: str, content: str = "") -> bool:
        """Create a file with optional content."""
        try:
            path = os.path.abspath(os.path.expanduser(path))
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            logger.info(f"Creating file: {path}")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to create file '{path}': {e}")
            return False

    @staticmethod
    def delete_file(path: str) -> bool:
        """Delete a file."""
        try:
            path = os.path.abspath(os.path.expanduser(path))
            if os.path.exists(path) and os.path.isfile(path):
                logger.info(f"Deleting file: {path}")
                os.remove(path)
                return True
            logger.warning(f"File '{path}' does not exist.")
            return False
        except Exception as e:
            logger.error(f"Failed to delete file '{path}': {e}")
            return False

    @staticmethod
    def create_folder(path: str) -> bool:
        """Create a new folder."""
        try:
            path = os.path.abspath(os.path.expanduser(path))
            logger.info(f"Creating folder: {path}")
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create folder '{path}': {e}")
            return False

    @staticmethod
    def delete_folder(path: str) -> bool:
        """Delete an entire folder directory."""
        try:
            path = os.path.abspath(os.path.expanduser(path))
            if os.path.exists(path) and os.path.isdir(path):
                logger.info(f"Deleting folder: {path}")
                shutil.rmtree(path)
                return True
            logger.warning(f"Folder '{path}' does not exist.")
            return False
        except Exception as e:
            logger.error(f"Failed to delete folder '{path}': {e}")
            return False

    @staticmethod
    def rename_file_or_folder(old_path: str, new_path: str) -> bool:
        """Rename or move a file/folder to a new name in the same parent directory."""
        try:
            old_path = os.path.abspath(os.path.expanduser(old_path))
            new_path = os.path.abspath(os.path.expanduser(new_path))
            if not os.path.exists(old_path):
                logger.warning(f"Rename source '{old_path}' does not exist.")
                return False
            logger.info(f"Renaming '{old_path}' to '{new_path}'")
            os.rename(old_path, new_path)
            return True
        except Exception as e:
            logger.error(f"Failed to rename '{old_path}' to '{new_path}': {e}")
            return False

    @classmethod
    def copy_file(cls, path: str) -> bool:
        """Save file path to clipboard for copying."""
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.exists(path):
            cls._clipboard_path = path
            cls._clipboard_is_cut = False
            logger.info(f"Copied file to clipboard buffer: {path}")
            return True
        logger.warning(f"Copy source '{path}' does not exist.")
        return False

    @classmethod
    def cut_file(cls, path: str) -> bool:
        """Save file path to clipboard for moving (cutting)."""
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.exists(path):
            cls._clipboard_path = path
            cls._clipboard_is_cut = True
            logger.info(f"Cut file to clipboard buffer: {path}")
            return True
        logger.warning(f"Cut source '{path}' does not exist.")
        return False

    @classmethod
    def paste_file(cls, dest_dir: str) -> bool:
        """Paste file in buffer to destination folder."""
        dest_dir = os.path.abspath(os.path.expanduser(dest_dir))
        if not cls._clipboard_path:
            logger.warning("No file in clipboard buffer to paste.")
            return False
        if not os.path.exists(cls._clipboard_path):
            logger.warning(f"Source file '{cls._clipboard_path}' no longer exists.")
            cls._clipboard_path = None
            return False
        if not os.path.isdir(dest_dir):
            logger.warning(f"Paste destination '{dest_dir}' is not a valid directory.")
            return False

        try:
            filename = os.path.basename(cls._clipboard_path)
            dest_path = os.path.join(dest_dir, filename)
            
            if cls._clipboard_is_cut:
                logger.info(f"Moving '{cls._clipboard_path}' to '{dest_path}'")
                shutil.move(cls._clipboard_path, dest_path)
                cls._clipboard_path = None  # Clear clipboard after cut paste
            else:
                logger.info(f"Copying '{cls._clipboard_path}' to '{dest_path}'")
                if os.path.isdir(cls._clipboard_path):
                    shutil.copytree(cls._clipboard_path, dest_path)
                else:
                    shutil.copy2(cls._clipboard_path, dest_path)
            return True
        except Exception as e:
            logger.error(f"Failed to paste file: {e}")
            return False

    @classmethod
    def get_recent_files(cls, limit: int = 10) -> List[str]:
        """List files recently opened on Windows."""
        cls._init_com()
        recent_list = []
        try:
            # winshell.recent() yields Shortcut objects
            shortcuts = list(winshell.recent())
            # Sort by access/modified time
            shortcuts.sort(key=lambda x: os.path.getmtime(x.lnk_filepath) if os.path.exists(x.lnk_filepath) else 0, reverse=True)
            
            for shortcut in shortcuts:
                try:
                    # Target path
                    target = shortcut.path
                    if target and os.path.exists(target) and os.path.isfile(target):
                        if target not in recent_list:
                            recent_list.append(target)
                            if len(recent_list) >= limit:
                                break
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Failed to get recent files: {e}")
        finally:
            cls._uninit_com()
        return recent_list

    @staticmethod
    def search_files(keyword: str, search_dir: Optional[str] = None) -> List[str]:
        """Search for files containing the keyword in their filename."""
        if not search_dir:
            # Default search in user's Documents folder
            cls = FileManager
            cls._init_com()
            try:
                search_dir = winshell.folder("personal")
            except Exception:
                search_dir = os.path.expanduser("~")
            finally:
                cls._uninit_com()

        logger.info(f"Searching for '{keyword}' in directory: {search_dir}")
        results = []
        count = 0
        max_results = 25  # prevent flooding
        
        try:
            for root, dirs, files in os.walk(search_dir):
                # Prune hidden/system folders
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ('appdata', 'microsoft', 'package')]
                for file in files:
                    if keyword.lower() in file.lower():
                        results.append(os.path.join(root, file))
                        count += 1
                        if count >= max_results:
                            return results
        except Exception as e:
            logger.error(f"Error during file search: {e}")
        return results

    @staticmethod
    def organize_files_automatically(folder_path: str) -> bool:
        """Organizes files inside a folder into subfolders based on extensions."""
        folder_path = os.path.abspath(os.path.expanduser(folder_path))
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            logger.warning(f"Cannot organize: {folder_path} is not a valid directory.")
            return False

        logger.info(f"Organizing files in: {folder_path}")
        
        # Extensions dictionary maps folder name to associated extensions
        extensions_map = {
            "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico'],
            "Documents": ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv', '.rtf', '.odt', '.md'],
            "Audio": ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
            "Video": ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv'],
            "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            "Executables": ['.exe', '.msi', '.bat', '.sh']
        }

        try:
            for filename in os.listdir(folder_path):
                file_abs = os.path.join(folder_path, filename)
                # Skip directories
                if os.path.isdir(file_abs):
                    continue

                _, ext = os.path.splitext(filename)
                ext = ext.lower()
                
                destination_folder = None
                for folder, exts in extensions_map.items():
                    if ext in exts:
                        destination_folder = folder
                        break
                
                # If extension doesn't match predefined categories, put it in 'Others'
                if not destination_folder:
                    destination_folder = "Others"

                dest_dir = os.path.join(folder_path, destination_folder)
                os.makedirs(dest_dir, exist_ok=True)
                
                dest_file_path = os.path.join(dest_dir, filename)
                # Avoid overwriting files, append number if duplicate exists
                base, extension = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_file_path):
                    dest_file_path = os.path.join(dest_dir, f"{base}_{counter}{extension}")
                    counter += 1

                logger.debug(f"Moving '{filename}' to category folder '{destination_folder}'")
                shutil.move(file_abs, dest_file_path)
            return True
        except Exception as e:
            logger.error(f"Error organizing files: {e}")
            return False
