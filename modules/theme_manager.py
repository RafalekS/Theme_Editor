"""
Theme Manager
Central theme management for loading/saving different theme formats
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .theme_data import TerminalTheme, QSSPalette, CustomTkinterTheme, QtWidgetTheme


class ThemeManager:
    """Central theme management for all supported formats"""

    def __init__(self, base_dir: str = None):
        """
        Initialize ThemeManager

        Args:
            base_dir: Base directory for the application (defaults to script directory)
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        else:
            base_dir = Path(base_dir)

        self.base_dir = base_dir
        self.config_dir = base_dir / "config"
        self.themes_dir = self.config_dir / "themes"
        self.qss_themes_dir = self.config_dir / "qss_themes"
        self.qt_widget_themes_dir = self.config_dir / "qt_widget_themes"
        self.templates_dir = self.config_dir / "templates"
        self.backup_dir = base_dir / "backup"

        # Ensure directories exist
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        self.qss_themes_dir.mkdir(parents=True, exist_ok=True)
        self.qt_widget_themes_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # ==================== JSON Terminal Themes ====================

    def load_json_themes(self, filepath: str = None) -> Dict[str, TerminalTheme]:
        """
        Load themes from JSON file

        Args:
            filepath: Path to JSON file (defaults to config/themes/themes.json)

        Returns:
            Dictionary of theme_name -> TerminalTheme
        """
        if filepath is None:
            filepath = self.themes_dir / "themes.json"
        else:
            filepath = Path(filepath)

        if not filepath.exists():
            return {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            themes = {}
            for theme_name, theme_data in data.items():
                try:
                    themes[theme_name] = TerminalTheme.from_dict(theme_data)
                except Exception as e:
                    print(f"Error loading theme '{theme_name}': {e}")

            return themes

        except Exception as e:
            print(f"Error loading themes from {filepath}: {e}")
            return {}

    def save_json_themes(self, themes: Dict[str, TerminalTheme], filepath: str = None, backup: bool = True):
        """
        Save themes to JSON file

        Args:
            themes: Dictionary of theme_name -> TerminalTheme
            filepath: Path to JSON file (defaults to config/themes/themes.json)
            backup: Whether to create backup before saving
        """
        if filepath is None:
            filepath = self.themes_dir / "themes.json"
        else:
            filepath = Path(filepath)

        # Create backup if file exists
        if backup and filepath.exists():
            self._create_backup(filepath)

        # Convert themes to dict
        themes_dict = {name: theme.to_dict() for name, theme in themes.items()}

        # Save to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(themes_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving themes to {filepath}: {e}")
            # Attempt to restore from backup
            if backup:
                self._restore_backup(filepath)
            raise

    # ==================== Windows Terminal Settings ====================

    def load_windows_terminal_settings(self, filepath: str = None) -> Dict:
        """
        Load Windows Terminal settings.json

        Args:
            filepath: Path to settings.json (auto-detects if None)

        Returns:
            Complete settings dictionary
        """
        if filepath is None:
            # Auto-detect Windows Terminal settings.json
            filepath = self._find_windows_terminal_settings()
            if filepath is None:
                raise FileNotFoundError("Windows Terminal settings.json not found")
        else:
            filepath = Path(filepath)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Remove comments (Windows Terminal JSON allows comments)
                content = f.read()
                content = self._remove_json_comments(content)
                settings = json.loads(content)

            return settings

        except Exception as e:
            print(f"Error loading Windows Terminal settings from {filepath}: {e}")
            return {}

    def save_windows_terminal_settings(self, settings: Dict, filepath: str = None, backup: bool = True):
        """
        Save to Windows Terminal settings.json with backup

        Args:
            settings: Complete settings dictionary
            filepath: Path to settings.json
            backup: Whether to create backup before saving (default: True)
        """
        if filepath is None:
            filepath = self._find_windows_terminal_settings()
            if filepath is None:
                raise FileNotFoundError("Windows Terminal settings.json not found")
        else:
            filepath = Path(filepath)

        # ALWAYS backup settings.json
        if filepath.exists():
            self._create_backup(filepath)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving Windows Terminal settings to {filepath}: {e}")
            # Attempt to restore from backup
            if backup:
                self._restore_backup(filepath)
            raise

    def _find_windows_terminal_settings(self) -> Optional[Path]:
        """
        Auto-detect Windows Terminal settings.json location

        Returns:
            Path to settings.json or None if not found
        """
        # Common locations for Windows Terminal settings.json
        possible_paths = [
            Path.home() / "AppData" / "Local" / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState" / "settings.json",
            Path.home() / "AppData" / "Local" / "Packages" / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe" / "LocalState" / "settings.json",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def _remove_json_comments(self, json_string: str) -> str:
        """Remove // and /* */ comments from JSON string"""
        import re

        # Remove single-line comments
        json_string = re.sub(r'//.*?$', '', json_string, flags=re.MULTILINE)

        # Remove multi-line comments
        json_string = re.sub(r'/\*.*?\*/', '', json_string, flags=re.DOTALL)

        return json_string

    # ==================== QSS Themes ====================

    def load_qss_theme(self, filepath: str) -> Tuple[QSSPalette, str]:
        """
        Load QSS file, return palette and full code

        Args:
            filepath: Path to .qss file

        Returns:
            Tuple of (QSSPalette, qss_code_string)
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"QSS file not found: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                qss_code = f.read()

            # Extract palette from QSS code
            palette = QSSPalette.from_qss(qss_code)

            return palette, qss_code

        except Exception as e:
            print(f"Error loading QSS theme from {filepath}: {e}")
            return QSSPalette(), ""

    def save_qss_theme(self, qss_code: str, filepath: str, backup: bool = True):
        """
        Save QSS code to file

        Args:
            qss_code: QSS stylesheet code
            filepath: Path to .qss file
            backup: Whether to create backup before saving
        """
        filepath = Path(filepath)

        # Create backup if file exists
        if backup and filepath.exists():
            self._create_backup(filepath)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(qss_code)
        except Exception as e:
            print(f"Error saving QSS theme to {filepath}: {e}")
            # Attempt to restore from backup
            if backup:
                self._restore_backup(filepath)
            raise

    # ==================== CustomTkinter Themes ====================

    def load_ctk_theme(self, filepath: str) -> CustomTkinterTheme:
        """
        Load CustomTkinter theme from JSON file

        Args:
            filepath: Path to .json theme file

        Returns:
            CustomTkinterTheme object
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"CustomTkinter theme file not found: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            theme_name = filepath.stem
            return CustomTkinterTheme.from_dict(data, theme_name)

        except Exception as e:
            print(f"Error loading CustomTkinter theme from {filepath}: {e}")
            return CustomTkinterTheme(name=filepath.stem)

    def save_ctk_theme(self, theme: CustomTkinterTheme, filepath: str, backup: bool = True):
        """
        Save CustomTkinter theme to JSON file

        Args:
            theme: CustomTkinterTheme object
            filepath: Path to .json file
            backup: Whether to create backup before saving
        """
        filepath = Path(filepath)

        # Create backup if file exists
        if backup and filepath.exists():
            self._create_backup(filepath)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving CustomTkinter theme to {filepath}: {e}")
            # Attempt to restore from backup
            if backup:
                self._restore_backup(filepath)
            raise

    # ==================== Backup/Restore ====================

    def _create_backup(self, filepath: Path):
        """
        Create timestamped backup of file

        Args:
            filepath: Path to file to backup
        """
        if not filepath.exists():
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_name = f"{filepath.name}.backup.{timestamp}"
        backup_path = self.backup_dir / backup_name

        try:
            shutil.copy2(filepath, backup_path)
            print(f"Backup created: {backup_path}")

            # Keep only last 5 backups
            self._cleanup_old_backups(filepath.name)

        except Exception as e:
            print(f"Error creating backup: {e}")

    def _restore_backup(self, filepath: Path) -> bool:
        """
        Restore file from most recent backup

        Args:
            filepath: Path to file to restore

        Returns:
            True if restored successfully, False otherwise
        """
        # Find most recent backup
        backups = sorted(
            self.backup_dir.glob(f"{filepath.name}.backup.*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not backups:
            print(f"No backup found for {filepath.name}")
            return False

        try:
            shutil.copy2(backups[0], filepath)
            print(f"Restored from backup: {backups[0]}")
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def _cleanup_old_backups(self, filename: str, keep_count: int = 5):
        """
        Keep only the most recent N backups

        Args:
            filename: Original filename to find backups for
            keep_count: Number of backups to keep (default: 5)
        """
        backups = sorted(
            self.backup_dir.glob(f"{filename}.backup.*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Delete old backups
        for backup in backups[keep_count:]:
            try:
                backup.unlink()
                print(f"Deleted old backup: {backup}")
            except Exception as e:
                print(f"Error deleting backup {backup}: {e}")

    # ==================== First-Run Setup ====================

    def first_run_setup(self) -> bool:
        """
        Perform first-run setup: copy template_themes.json to themes.json

        Returns:
            True if setup was performed, False if already set up
        """
        themes_file = self.themes_dir / "themes.json"

        # Check if themes.json already exists
        if themes_file.exists():
            return False

        # Copy template_themes.json to themes.json
        template_file = self.templates_dir / "template_themes.json"

        if not template_file.exists():
            print(f"Template file not found: {template_file}")
            return False

        try:
            shutil.copy2(template_file, themes_file)
            print(f"First-run setup: Copied {template_file} to {themes_file}")
            return True
        except Exception as e:
            print(f"Error during first-run setup: {e}")
            return False

    # ==================== Utility Methods ====================

    def get_theme_list(self, theme_dir: str = None) -> List[str]:
        """
        Get list of theme files in a directory

        Args:
            theme_dir: Directory to search (defaults to themes_dir)

        Returns:
            List of theme filenames
        """
        if theme_dir is None:
            theme_dir = self.themes_dir
        else:
            theme_dir = Path(theme_dir)

        if not theme_dir.exists():
            return []

        return [f.name for f in theme_dir.glob("*.json")]

    def get_qss_theme_list(self) -> List[str]:
        """Get list of QSS theme files"""
        if not self.qss_themes_dir.exists():
            return []

        return [f.name for f in self.qss_themes_dir.glob("*.qss")]

    # ==================== Qt Widget Themes ====================

    def load_qt_widget_themes(self, filepath: str = None) -> Dict[str, QtWidgetTheme]:
        """
        Load Qt Widget themes from JSON file

        Args:
            filepath: Path to JSON file (defaults to config/qt_widget_themes/qt_themes.json)

        Returns:
            Dictionary of theme_name -> QtWidgetTheme
        """
        if filepath is None:
            filepath = self.qt_widget_themes_dir / "qt_themes.json"
        else:
            filepath = Path(filepath)

        if not filepath.exists():
            return {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            themes = {}
            for theme_name, theme_data in data.items():
                try:
                    themes[theme_name] = QtWidgetTheme.from_dict(theme_data)
                except Exception as e:
                    print(f"Error loading Qt widget theme '{theme_name}': {e}")

            return themes

        except Exception as e:
            print(f"Error loading Qt widget themes from {filepath}: {e}")
            return {}

    def save_qt_widget_themes(self, themes: Dict[str, QtWidgetTheme], filepath: str = None, backup: bool = True):
        """
        Save Qt Widget themes to JSON file

        Args:
            themes: Dictionary of theme_name -> QtWidgetTheme
            filepath: Path to JSON file (defaults to config/qt_widget_themes/qt_themes.json)
            backup: Whether to create backup before saving
        """
        if filepath is None:
            filepath = self.qt_widget_themes_dir / "qt_themes.json"
        else:
            filepath = Path(filepath)

        # Create backup if file exists
        if backup and filepath.exists():
            self._create_backup(filepath)

        # Convert themes to dict
        themes_dict = {name: theme.to_dict() for name, theme in themes.items()}

        # Save to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(themes_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving Qt widget themes to {filepath}: {e}")
            # Attempt to restore from backup
            if backup:
                self._restore_backup(filepath)
            raise

    def get_qt_widget_theme_list(self) -> List[str]:
        """Get list of Qt widget theme files"""
        if not self.qt_widget_themes_dir.exists():
            return []

        return [f.name for f in self.qt_widget_themes_dir.glob("*.json")]
