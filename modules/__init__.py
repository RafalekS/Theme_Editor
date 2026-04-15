"""
Theme Editor - Core Modules
Multi-format theme editor supporting JSON, Windows Terminal, QSS, and CustomTkinter themes
"""

from .config_manager import ConfigManager
from .theme_manager import ThemeManager
from .theme_data import TerminalTheme, QSSPalette, CustomTkinterTheme, QtWidgetTheme

__version__ = "1.0.0"
__author__ = "Rafal Staska"

__all__ = [
    'ConfigManager',
    'ThemeManager',
    'TerminalTheme',
    'QSSPalette',
    'CustomTkinterTheme',
    'QtWidgetTheme'
]
