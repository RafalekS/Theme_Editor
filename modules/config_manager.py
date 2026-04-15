"""
Configuration Manager
Centralized configuration loading and saving with validation and defaults
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manage application configuration with defaults and validation"""

    # Default configuration structure
    DEFAULT_CONFIG = {
        "app": {
            "theme": "Earthsong",
            "icon_light": "assets/theme_editor_light.ico",
            "icon_dark": "assets/theme_editor_dark.ico",
            "icon_mode": "auto"  # auto, light, dark
        },
        "window": {
            "geometry": None,
            "last_tab": 0,
            "splitter_sizes": {}
        },
        "defaults": {
            "terminal_theme": "Gruvbox Dark",
            "qss_theme": "Material Dark",
            "qt_widget_theme": "Earthsong"
        },
        "paths": {
            "themes_dir": "config/themes",
            "qss_themes_dir": "config/qss_themes",
            "qt_widget_themes_dir": "config/qt_widget_themes",
            "backup_dir": "backup",
            "templates_dir": "config/templates"
        },
        "ui": {
            "colors": {
                "accent": "#0078D4",
                "accent_hover": "#1084D8",
                "warning": "#FF9800",
                "success": "#4CAF50",
                "error": "#F44336",
                "background_dark": "#2B2B2B",
                "background_medium": "#3C3C3C",
                "background_light": "#F5F5F5",
                "text_light": "#FFFFFF",
                "text_dark": "#000000",
                "border": "#555555",
                "border_light": "#CCCCCC"
            },
            "fonts": {
                "default_family": "Segoe UI",
                "default_size": 10,
                "code_family": "Consolas",
                "code_size": 10
            },
            "dimensions": {
                "window_width": 1200,
                "window_height": 800,
                "min_editor_width": 400,
                "min_preview_width": 350
            }
        },
        "backup": {
            "enabled": True,
            "keep_count": 5,
            "auto_backup_interval": 300
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigManager

        Args:
            config_path: Path to config.json (defaults to config/config.json)
        """
        if config_path is None:
            self.config_path = Path(__file__).parent.parent / "config" / "config.json"
        else:
            # Expand ~ and environment variables
            config_path = os.path.expanduser(os.path.expandvars(config_path))
            self.config_path = Path(config_path)

        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file with defaults

        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # Merge with defaults (deep merge)
                self.config = self._deep_merge(self.DEFAULT_CONFIG.copy(), loaded_config)

                # Handle legacy config format (app_theme -> app.theme)
                if "app_theme" in loaded_config:
                    self.config["app"]["theme"] = loaded_config["app_theme"]

                return self.config

            except Exception as e:
                print(f"Error loading config from {self.config_path}: {e}")
                print("Using default configuration")
                self.config = self.DEFAULT_CONFIG.copy()
                return self.config
        else:
            # Use defaults
            self.config = self.DEFAULT_CONFIG.copy()
            # Save defaults to create initial config file
            self.save()
            return self.config

    def save(self, config: Optional[Dict[str, Any]] = None):
        """
        Save configuration to file

        Args:
            config: Configuration dictionary (uses self.config if None)
        """
        if config is not None:
            self.config = config

        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error saving config to {self.config_path}: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key_path: Dot-separated path (e.g., "app.theme" or "ui.colors.accent")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation

        Args:
            key_path: Dot-separated path (e.g., "app.theme")
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def get_path(self, key: str, base_dir: Optional[Path] = None) -> Path:
        """
        Get expanded path from configuration

        Args:
            key: Configuration key (e.g., "paths.themes_dir")
            base_dir: Base directory for relative paths (defaults to parent of config)

        Returns:
            Resolved Path object
        """
        if base_dir is None:
            base_dir = self.config_path.parent.parent

        path_str = self.get(key, "")

        # Expand ~ and environment variables
        path_str = os.path.expanduser(os.path.expandvars(path_str))

        path = Path(path_str)

        # Make absolute if relative
        if not path.is_absolute():
            path = base_dir / path

        return path

    def _deep_merge(self, base: Dict, overlay: Dict) -> Dict:
        """
        Deep merge two dictionaries

        Args:
            base: Base dictionary
            overlay: Overlay dictionary (takes precedence)

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_ui_color(self, color_name: str) -> str:
        """
        Get UI color by name

        Args:
            color_name: Color name (e.g., "accent", "warning")

        Returns:
            Hex color string
        """
        return self.get(f"ui.colors.{color_name}", "#000000")

    def get_fallback_stylesheet(self) -> str:
        """
        Generate fallback stylesheet from config colors

        Returns:
            QSS stylesheet string
        """
        colors = self.config.get("ui", {}).get("colors", {})

        return f"""
            QWidget {{
                background-color: {colors.get("background_dark", "#2B2B2B")};
                color: {colors.get("text_light", "#FFFFFF")};
            }}
            QPushButton {{
                background-color: {colors.get("accent", "#0078D4")};
                color: {colors.get("text_light", "#FFFFFF")};
                border: 1px solid {colors.get("border", "#555")};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {colors.get("accent_hover", "#1084D8")};
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {colors.get("background_medium", "#3C3C3C")};
                color: {colors.get("text_light", "#FFFFFF")};
                border: 1px solid {colors.get("border", "#555")};
                border-radius: 3px;
                padding: 4px;
            }}
        """
