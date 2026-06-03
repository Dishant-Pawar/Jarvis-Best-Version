import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from jarvis.utils.logger import logger

# --- Common User Folders ---
HOME        = Path.home()
DESKTOP     = HOME / "Desktop"
DOWNLOADS   = HOME / "Downloads"
DOCUMENTS   = HOME / "Documents"
PICTURES    = HOME / "Pictures"
VIDEOS      = HOME / "Videos"
MUSIC       = HOME / "Music"

COMMON_FOLDERS = [DESKTOP, DOWNLOADS, DOCUMENTS, PICTURES, VIDEOS, MUSIC]

# Mapping of common spoken/typed folder aliases to absolute paths
FOLDER_ALIASES = {
    "desktop":   DESKTOP,
    "downloads": DOWNLOADS,
    "documents": DOCUMENTS,
    "pictures":  PICTURES,
    "videos":    VIDEOS,
    "music":     MUSIC,
    "home":      HOME,
    "my desktop":   DESKTOP,
    "my downloads": DOWNLOADS,
    "my documents": DOCUMENTS,
    "my pictures":  PICTURES,
}


class FileManager:
    """
    Full-featured Windows file & folder manager for JARVIS.

    Supported operations:
    - Open file / folder / downloads / recent files
    - Create file / folder
    - Rename file / folder
    - Delete file / folder
    - Move file / folder
    - Copy + Paste file / folder
    - Search files by name across common locations
    - Search documents by keyword (content)
    - Organize folder by file type
    - List folder contents
    """

    # In-memory clipboard buffer for copy/cut → paste
    _clipboard_path: Optional[str] = None
    _clipboard_is_cut: bool = False

    # ──────────────────────────────────────────────
    # PATH RESOLUTION HELPERS
    # ──────────────────────────────────────────────

    @staticmethod
    def get_downloads_path() -> str:
        return str(DOWNLOADS) if DOWNLOADS.exists() else str(HOME)

    @staticmethod
    def resolve_path(raw: str, must_exist: bool = True) -> Optional[str]:
        """
        Resolve a user-provided path string to an absolute path.
        Checks folder aliases first, then expands ~ and env vars,
        then searches common folders.
        Returns the resolved path string, or None if not found and must_exist=True.
        """
        if not raw:
            return None

        # Check alias map (desktop, downloads, etc.)
        alias = FOLDER_ALIASES.get(raw.strip().lower())
        if alias:
            return str(alias)

        # Expand ~ and environment variables
        expanded = os.path.abspath(os.path.expandvars(os.path.expanduser(raw)))
        if os.path.exists(expanded):
            return expanded

        # Try searching common folders for just the filename/folder name
        name = os.path.basename(raw) or raw.strip()
        found = FileManager.find_in_common_folders(name)
        if found:
            return found[0]  # Return first match

        return None if must_exist else expanded

    @staticmethod
    def find_in_common_folders(name: str) -> List[str]:
        """
        Search Desktop, Downloads, Documents, Pictures, Videos, Music for a
        file or folder whose basename matches `name` (case-insensitive).
        Returns a list of absolute path strings found.
        """
        name_l = name.strip().lower()
        results = []
        for folder in COMMON_FOLDERS:
            if not folder.exists():
                continue
            try:
                for entry in folder.iterdir():
                    if entry.name.lower() == name_l:
                        results.append(str(entry))
            except PermissionError:
                continue
        return results

    # ──────────────────────────────────────────────
    # OPEN OPERATIONS
    # ──────────────────────────────────────────────

    @classmethod
    def open_downloads_folder(cls) -> bool:
        """Open the Downloads folder in File Explorer."""
        try:
            path = cls.get_downloads_path()
            logger.info(f"Opening Downloads folder: {path}")
            os.startfile(path)
            return True
        except Exception as e:
            logger.error(f"Failed to open Downloads: {e}")
            return False

    @staticmethod
    def open_folder(path: str) -> Tuple[bool, str]:
        """
        Open a directory in File Explorer.
        Returns (success, message).
        """
        resolved = FileManager.resolve_path(path)
        if resolved and os.path.isdir(resolved):
            try:
                logger.info(f"Opening folder: {resolved}")
                os.startfile(resolved)
                return True, resolved
            except Exception as e:
                logger.error(f"Failed to open folder '{resolved}': {e}")
                return False, str(e)

        # Search common folders
        matches = FileManager.find_in_common_folders(os.path.basename(path) or path)
        dirs = [m for m in matches if os.path.isdir(m)]
        if dirs:
            try:
                os.startfile(dirs[0])
                return True, dirs[0]
            except Exception as e:
                return False, str(e)

        return False, f"Folder not found: {path}"

    @staticmethod
    def open_specific_file(path: str) -> Tuple[bool, str]:
        """
        Open a specific file with its default application.
        Returns (success, resolved_path_or_error).
        """
        resolved = FileManager.resolve_path(path)
        if resolved and os.path.isfile(resolved):
            try:
                logger.info(f"Opening file: {resolved}")
                os.startfile(resolved)
                return True, resolved
            except Exception as e:
                return False, str(e)

        # Search common folders for file
        name = os.path.basename(path) or path
        matches = FileManager.find_in_common_folders(name)
        files = [m for m in matches if os.path.isfile(m)]
        if files:
            try:
                os.startfile(files[0])
                return True, files[0]
            except Exception as e:
                return False, str(e)

        return False, f"File not found: {path}"

    # ──────────────────────────────────────────────
    # CREATE OPERATIONS
    # ──────────────────────────────────────────────

    @staticmethod
    def create_file(path: str, content: str = "") -> Tuple[bool, str]:
        """
        Create a file with optional content.
        If no directory is specified, creates on the Desktop.
        Returns (success, full_path_or_error).
        """
        try:
            # If path has no directory component, default to Desktop
            if not os.path.dirname(path) or not os.path.isabs(path):
                path = str(DESKTOP / os.path.basename(path))

            path = os.path.abspath(os.path.expanduser(path))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            logger.info(f"Creating file: {path}")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, path
        except Exception as e:
            logger.error(f"Failed to create file '{path}': {e}")
            return False, str(e)

    @staticmethod
    def create_folder(path: str) -> Tuple[bool, str]:
        """
        Create a new folder.
        If no directory is specified, creates on the Desktop.
        Returns (success, full_path_or_error).
        """
        try:
            if not os.path.dirname(path) or not os.path.isabs(path):
                path = str(DESKTOP / os.path.basename(path))

            path = os.path.abspath(os.path.expanduser(path))
            logger.info(f"Creating folder: {path}")
            os.makedirs(path, exist_ok=True)
            return True, path
        except Exception as e:
            logger.error(f"Failed to create folder '{path}': {e}")
            return False, str(e)

    # ──────────────────────────────────────────────
    # DELETE OPERATIONS
    # ──────────────────────────────────────────────

    @staticmethod
    def delete_file(path: str) -> Tuple[bool, str]:
        """Delete a file. Searches common folders if not found directly."""
        resolved = FileManager.resolve_path(path)
        if not resolved:
            matches = FileManager.find_in_common_folders(os.path.basename(path) or path)
            files = [m for m in matches if os.path.isfile(m)]
            if files:
                resolved = files[0]

        if resolved and os.path.isfile(resolved):
            try:
                logger.info(f"Deleting file: {resolved}")
                os.remove(resolved)
                return True, resolved
            except Exception as e:
                logger.error(f"Failed to delete '{resolved}': {e}")
                return False, str(e)
        return False, f"File not found: {path}"

    @staticmethod
    def delete_folder(path: str) -> Tuple[bool, str]:
        """Delete an entire folder. Searches common folders if not found directly."""
        resolved = FileManager.resolve_path(path)
        if not resolved:
            matches = FileManager.find_in_common_folders(os.path.basename(path) or path)
            dirs = [m for m in matches if os.path.isdir(m)]
            if dirs:
                resolved = dirs[0]

        if resolved and os.path.isdir(resolved):
            try:
                logger.info(f"Deleting folder: {resolved}")
                shutil.rmtree(resolved)
                return True, resolved
            except Exception as e:
                logger.error(f"Failed to delete folder '{resolved}': {e}")
                return False, str(e)
        return False, f"Folder not found: {path}"

    # ──────────────────────────────────────────────
    # RENAME OPERATIONS
    # ──────────────────────────────────────────────

    @staticmethod
    def rename_file_or_folder(old_name: str, new_name: str) -> Tuple[bool, str]:
        """
        Rename a file or folder.
        Searches common folders if old_name is just a filename (no directory).
        new_name can be just the new name (will keep same parent directory).
        """
        # Resolve old path
        old_path = FileManager.resolve_path(old_name)
        if not old_path:
            matches = FileManager.find_in_common_folders(os.path.basename(old_name) or old_name)
            if matches:
                old_path = matches[0]

        if not old_path or not os.path.exists(old_path):
            return False, f"Not found: {old_name}"

        # Build new path: same directory, new name
        parent_dir = os.path.dirname(old_path)
        new_basename = os.path.basename(new_name) or new_name
        new_path = os.path.join(parent_dir, new_basename)

        try:
            logger.info(f"Renaming '{old_path}' → '{new_path}'")
            os.rename(old_path, new_path)
            return True, new_path
        except Exception as e:
            logger.error(f"Failed to rename: {e}")
            return False, str(e)

    # ──────────────────────────────────────────────
    # MOVE OPERATIONS
    # ──────────────────────────────────────────────

    @staticmethod
    def move_file_or_folder(src: str, dest: str) -> Tuple[bool, str]:
        """
        Move a file or folder to a destination directory.
        Searches common folders if src is just a name.
        dest can be a folder name like 'Desktop', 'Downloads', 'Documents'.
        Returns (success, final_path_or_error).
        """
        # Resolve destination shorthand
        dest_aliases = {
            "desktop": str(DESKTOP),
            "downloads": str(DOWNLOADS),
            "documents": str(DOCUMENTS),
            "pictures": str(PICTURES),
            "videos": str(VIDEOS),
            "music": str(MUSIC),
            "home": str(HOME),
        }
        dest_resolved = dest_aliases.get(dest.strip().lower(), None)
        if not dest_resolved:
            dest_resolved = FileManager.resolve_path(dest, must_exist=False)
            if dest_resolved and not os.path.exists(dest_resolved):
                # Check if it's a common folder alias
                dest_resolved = None

        if not dest_resolved:
            return False, f"Destination not found: {dest}"

        # Resolve source
        src_resolved = FileManager.resolve_path(src)
        if not src_resolved:
            matches = FileManager.find_in_common_folders(os.path.basename(src) or src)
            if matches:
                src_resolved = matches[0]

        if not src_resolved or not os.path.exists(src_resolved):
            return False, f"Source not found: {src}"

        try:
            filename = os.path.basename(src_resolved)
            final_path = os.path.join(dest_resolved, filename)
            shutil.move(src_resolved, final_path)
            logger.info(f"Moving '{src_resolved}' -> '{final_path}'")
            return True, final_path
        except Exception as e:
            logger.error(f"Failed to move: {e}")
            return False, str(e)

    # ──────────────────────────────────────────────
    # COPY + PASTE OPERATIONS
    # ──────────────────────────────────────────────

    @classmethod
    def copy_file(cls, path: str) -> Tuple[bool, str]:
        """Copy a file/folder path to the internal clipboard buffer."""
        resolved = FileManager.resolve_path(path)
        if not resolved:
            matches = FileManager.find_in_common_folders(os.path.basename(path) or path)
            if matches:
                resolved = matches[0]

        if resolved and os.path.exists(resolved):
            cls._clipboard_path = resolved
            cls._clipboard_is_cut = False
            logger.info(f"Copied to clipboard: {resolved}")
            return True, resolved
        return False, f"Not found: {path}"

    @classmethod
    def cut_file(cls, path: str) -> Tuple[bool, str]:
        """Cut (mark for move) a file/folder to the internal clipboard buffer."""
        resolved = FileManager.resolve_path(path)
        if not resolved:
            matches = FileManager.find_in_common_folders(os.path.basename(path) or path)
            if matches:
                resolved = matches[0]

        if resolved and os.path.exists(resolved):
            cls._clipboard_path = resolved
            cls._clipboard_is_cut = True
            logger.info(f"Cut to clipboard: {resolved}")
            return True, resolved
        return False, f"Not found: {path}"

    @classmethod
    def paste_file(cls, dest_dir: str) -> Tuple[bool, str]:
        """Paste the clipboard item into dest_dir."""
        if not cls._clipboard_path:
            return False, "No file in clipboard. Please copy or cut a file first."

        dest_aliases = {
            "desktop": str(DESKTOP),
            "downloads": str(DOWNLOADS),
            "documents": str(DOCUMENTS),
            "pictures": str(PICTURES),
            "videos": str(VIDEOS),
            "music": str(MUSIC),
        }
        dest = dest_aliases.get(dest_dir.strip().lower(), os.path.abspath(os.path.expanduser(dest_dir)))

        if not os.path.isdir(dest):
            return False, f"Destination folder not found: {dest_dir}"
        if not os.path.exists(cls._clipboard_path):
            cls._clipboard_path = None
            return False, "Clipboard source no longer exists."

        try:
            filename = os.path.basename(cls._clipboard_path)
            dest_path = os.path.join(dest, filename)

            if cls._clipboard_is_cut:
                logger.info(f"Moving '{cls._clipboard_path}' → '{dest_path}'")
                shutil.move(cls._clipboard_path, dest_path)
                cls._clipboard_path = None
            else:
                logger.info(f"Copying '{cls._clipboard_path}' → '{dest_path}'")
                if os.path.isdir(cls._clipboard_path):
                    shutil.copytree(cls._clipboard_path, dest_path)
                else:
                    shutil.copy2(cls._clipboard_path, dest_path)
            return True, dest_path
        except Exception as e:
            logger.error(f"Paste failed: {e}")
            return False, str(e)

    # ──────────────────────────────────────────────
    # SEARCH OPERATIONS
    # ──────────────────────────────────────────────

    @staticmethod
    def search_files(keyword: str, search_dirs: Optional[List[str]] = None) -> List[str]:
        """
        Search for files/folders by name keyword across common user folders.
        Returns list of matching absolute paths (max 20 results).
        """
        if not search_dirs:
            search_dirs = [str(f) for f in COMMON_FOLDERS if f.exists()]

        keyword_l = keyword.strip().lower()
        results = []
        logger.info(f"Searching for '{keyword}' in: {search_dirs}")

        for search_dir in search_dirs:
            try:
                for root, dirs, files in os.walk(search_dir):
                    # Prune hidden and system dirs
                    dirs[:] = [d for d in dirs if not d.startswith('.') and
                                d.lower() not in ('appdata', '$recycle.bin', 'system volume information')]
                    for name in files + dirs:
                        if keyword_l in name.lower():
                            results.append(os.path.join(root, name))
                            if len(results) >= 20:
                                return results
            except (PermissionError, OSError):
                continue
        return results

    @staticmethod
    def search_documents_by_content(keyword: str) -> List[str]:
        """
        Search text/document files (.txt, .md, .csv, .log) by content.
        Returns list of matching file paths (max 10 results).
        """
        search_dirs = [str(DOCUMENTS), str(DESKTOP), str(DOWNLOADS)]
        text_extensions = {'.txt', '.md', '.csv', '.log', '.py', '.json', '.xml', '.html'}
        keyword_l = keyword.strip().lower()
        results = []

        for search_dir in search_dirs:
            try:
                for root, dirs, files in os.walk(search_dir):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for fname in files:
                        ext = os.path.splitext(fname)[1].lower()
                        if ext not in text_extensions:
                            continue
                        fpath = os.path.join(root, fname)
                        try:
                            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                                if keyword_l in f.read().lower():
                                    results.append(fpath)
                                    if len(results) >= 10:
                                        return results
                        except Exception:
                            continue
            except (PermissionError, OSError):
                continue
        return results

    # ──────────────────────────────────────────────
    # RECENT FILES
    # ──────────────────────────────────────────────

    @staticmethod
    def get_recent_files(limit: int = 5) -> List[str]:
        """List recently modified files across common folders."""
        recent = []
        for folder in COMMON_FOLDERS:
            if not folder.exists():
                continue
            try:
                for entry in folder.iterdir():
                    if entry.is_file():
                        recent.append((entry.stat().st_mtime, str(entry)))
            except (PermissionError, OSError):
                continue
        recent.sort(reverse=True)
        return [p for _, p in recent[:limit]]

    # ──────────────────────────────────────────────
    # LIST FOLDER CONTENTS
    # ──────────────────────────────────────────────

    @staticmethod
    def list_folder_contents(path: str) -> Tuple[bool, List[str]]:
        """
        List the contents of a folder.
        Returns (success, list_of_names).
        """
        resolved = FileManager.resolve_path(path)
        if not resolved or not os.path.isdir(resolved):
            matches = FileManager.find_in_common_folders(os.path.basename(path) or path)
            dirs = [m for m in matches if os.path.isdir(m)]
            resolved = dirs[0] if dirs else None

        if not resolved:
            return False, []

        try:
            entries = sorted(os.listdir(resolved))
            return True, entries
        except Exception as e:
            logger.error(f"Failed to list '{resolved}': {e}")
            return False, []

    # ──────────────────────────────────────────────
    # ORGANIZE FILES
    # ──────────────────────────────────────────────

    @staticmethod
    def organize_files_automatically(folder_path: str) -> Tuple[bool, str]:
        """Organize files in a folder into subfolders by extension type."""
        resolved = FileManager.resolve_path(folder_path)
        if not resolved or not os.path.isdir(resolved):
            resolved = FileManager.resolve_path(
                folder_path, must_exist=False
            )

        if not resolved or not os.path.isdir(resolved):
            return False, f"Folder not found: {folder_path}"

        logger.info(f"Organizing files in: {resolved}")

        extensions_map = {
            "Images":      ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico', '.svg'],
            "Documents":   ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv', '.rtf', '.odt', '.md'],
            "Audio":       ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma'],
            "Video":       ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm'],
            "Archives":    ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            "Executables": ['.exe', '.msi', '.bat', '.cmd', '.sh', '.ps1'],
            "Code":        ['.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.java', '.cpp', '.c'],
        }

        moved = 0
        try:
            for filename in os.listdir(resolved):
                file_abs = os.path.join(resolved, filename)
                if os.path.isdir(file_abs):
                    continue

                _, ext = os.path.splitext(filename)
                ext = ext.lower()

                dest_folder_name = "Others"
                for folder_name, exts in extensions_map.items():
                    if ext in exts:
                        dest_folder_name = folder_name
                        break

                dest_dir = os.path.join(resolved, dest_folder_name)
                os.makedirs(dest_dir, exist_ok=True)

                dest_path = os.path.join(dest_dir, filename)
                counter = 1
                base, extension = os.path.splitext(filename)
                while os.path.exists(dest_path):
                    dest_path = os.path.join(dest_dir, f"{base}_{counter}{extension}")
                    counter += 1

                shutil.move(file_abs, dest_path)
                moved += 1

            return True, f"Organized {moved} file(s) in {os.path.basename(resolved)}."
        except Exception as e:
            logger.error(f"Error organizing files: {e}")
            return False, str(e)
