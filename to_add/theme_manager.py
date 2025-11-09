"""
Theme manager for loading and applying Qt widget styles to the application.
Loads Qt stylesheets directly from JSON - no color mapping needed.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional


class ThemeManager:
    """Manages application themes and stylesheet generation"""

    def __init__(
        self,
        themes_file: Optional[str] = None,
        config_file: Optional[str] = None,
        auto_load_last_theme: bool = True
    ):
        """
        Initialize theme manager.

        Args:
            themes_file: Path to themes JSON file. If None, uses config/themes/themes.json from project root
            config_file: Path to config JSON file. If None, uses config/config.json from project root
            auto_load_last_theme: Whether to automatically load the last used theme from config

        Raises:
            FileNotFoundError: If themes file doesn't exist
            json.JSONDecodeError: If themes file contains invalid JSON
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Get project root (parent of modules folder)
        project_root = Path(__file__).parent.parent

        # Set themes file path
        if themes_file is None:
            self.themes_file = project_root / "config" / "themes" / "themes.json"
        else:
            self.themes_file = Path(themes_file)

        # Set config file path
        if config_file is None:
            self.config_file = project_root / "config" / "config.json"
        else:
            self.config_file = Path(config_file)

        self.themes: Dict = {}
        self.current_theme: Optional[str] = None
        self.auto_load_last_theme = auto_load_last_theme

        # Load themes (this will raise exception if file missing)
        self._load_themes()

        # Auto-load last theme if enabled
        if self.auto_load_last_theme:
            last_theme = self._get_last_theme()
            if last_theme and last_theme in self.themes:
                self.current_theme = last_theme
                self.logger.info(f"Loaded last used theme: {last_theme}")

    def _load_themes(self):
        """
        Load themes from JSON file.

        Raises:
            FileNotFoundError: If themes file doesn't exist
            json.JSONDecodeError: If themes file contains invalid JSON
        """
        if not self.themes_file.exists():
            self.logger.error(f"Themes file not found: {self.themes_file}")
            raise FileNotFoundError(
                f"Themes file not found: {self.themes_file}\n"
                f"Please ensure themes.json exists in the config/themes/ directory"
            )

        try:
            with open(self.themes_file, 'r', encoding='utf-8') as f:
                self.themes = json.load(f)
            self.logger.info(f"Loaded {len(self.themes)} themes from {self.themes_file}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in themes file: {e}")
            raise

    def _get_last_theme(self) -> Optional[str]:
        """
        Get the last used theme from config file.

        Returns:
            Theme name or None if not found or config doesn't exist
        """
        if not self.config_file.exists():
            self.logger.debug(f"Config file not found: {self.config_file}")
            return None

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            last_theme = config.get('last_theme')
            if last_theme:
                self.logger.debug(f"Last theme from config: {last_theme}")
            return last_theme
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Error reading last theme from config: {e}")
            return None

    def _save_last_theme(self, theme_name: str):
        """
        Save the last used theme to config file.

        Args:
            theme_name: Name of the theme to save
        """
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new one
        config = {}
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                self.logger.warning("Config file contains invalid JSON, creating new config")
                config = {}

        # Update last theme
        config['last_theme'] = theme_name

        # Save config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            self.logger.debug(f"Saved last theme to config: {theme_name}")
        except Exception as e:
            self.logger.error(f"Error saving theme to config: {e}")

    def get_theme_names(self) -> List[str]:
        """
        Get list of available theme names.

        Returns:
            List of theme names sorted alphabetically
        """
        return sorted(self.themes.keys())

    def get_theme(self, theme_name: str) -> Optional[Dict]:
        """
        Get theme data by name.

        Args:
            theme_name: Name of the theme

        Returns:
            Theme data dictionary or None if not found
        """
        return self.themes.get(theme_name)

    def generate_stylesheet(self, theme_name: str) -> str:
        """
        Generate Qt stylesheet from theme.

        Args:
            theme_name: Name of the theme to use

        Returns:
            Qt stylesheet string

        Raises:
            ValueError: If theme not found
        """
        theme = self.get_theme(theme_name)
        if not theme:
            self.logger.error(f"Theme '{theme_name}' not found")
            raise ValueError(
                f"Theme '{theme_name}' not found. "
                f"Available themes: {', '.join(self.get_theme_names())}"
            )

        self.current_theme = theme_name

        # Get styles dictionary from theme
        styles = theme.get('styles', {})

        if not styles:
            self.logger.warning(f"Theme '{theme_name}' has no styles defined")
            return ""

        # Assemble stylesheet from individual widget styles
        stylesheet_parts = []

        for selector, style in styles.items():
            # Format: "Selector { style }"
            stylesheet_parts.append(f"{selector} {{\n    {style}\n}}")

        stylesheet = "\n\n".join(stylesheet_parts)

        self.logger.info(f"Generated stylesheet for theme: {theme_name}")
        return stylesheet

    def apply_theme(self, app, theme_name: str, save_preference: bool = True):
        """
        Apply theme to Qt application.

        Args:
            app: QApplication instance
            theme_name: Name of theme to apply
            save_preference: Whether to save this theme as the last used theme

        Raises:
            ValueError: If theme not found
        """
        stylesheet = self.generate_stylesheet(theme_name)
        app.setStyleSheet(stylesheet)
        self.logger.info(f"Applied theme: {theme_name}")

        if save_preference:
            self._save_last_theme(theme_name)
