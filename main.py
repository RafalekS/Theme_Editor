#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Theme Editor - Multi-Format Theme Editor
Universal theme editor supporting JSON terminal themes, Windows Terminal themes,
QSS themes, and CustomTkinter themes with integrated image converter utility.

Author: Rafal Staska
License: MIT
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QMessageBox, QPushButton, QStatusBar,
    QMenuBar, QMenu, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

# Add modules directory to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.theme_manager import ThemeManager
from modules.theme_data import TerminalTheme, QSSPalette, CustomTkinterTheme
from modules.json_theme_editor import JSONTerminalEditor
from modules.windows_terminal_editor import WindowsTerminalEditor
from modules.qss_theme_editor import QSSThemeEditor
from modules.ctk_theme_editor import CTkThemeEditor
from modules.converter_ui import ConverterUI


class ThemeEditorMainWindow(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Editor - Multi-Format Theme Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize theme manager
        self.theme_manager = ThemeManager()

        # Perform first-run setup
        if self.theme_manager.first_run_setup():
            QMessageBox.information(
                self,
                "First Run Setup",
                "Welcome to Theme Editor!\n\n"
                "60+ terminal themes have been loaded from the template library.\n"
                "You can now create, edit, and convert themes across multiple formats."
            )

        # Set application icon (use dark theme icon by default)
        icon_path = Path(__file__).parent / "assets" / "theme_editor_dark.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Setup UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()

        # Track unsaved changes
        self.unsaved_changes = False
        self.current_file = None

    def _setup_ui(self):
        """Setup main UI with tabbed interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget (5 tabs for different editors)
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # Remove frame around tab widget

        # Remove massive gray space between tab bar and content
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 0;
                top: -1px;
                margin: 0px;
                padding: 0px;
            }
        """)

        layout.addWidget(self.tab_widget, 1)  # Give all stretch to tab widget

        # Tab 1: JSON Terminal Themes Editor (FULLY IMPLEMENTED)
        self.terminal_editor_tab = JSONTerminalEditor(self.theme_manager)
        self.terminal_editor_tab.themeModified.connect(self._on_theme_modified)
        self.tab_widget.addTab(self.terminal_editor_tab, "Terminal Themes")

        # Tab 2: Windows Terminal Integration (FULLY IMPLEMENTED)
        self.windows_terminal_tab = WindowsTerminalEditor(self.theme_manager)
        self.windows_terminal_tab.themeModified.connect(self._on_theme_modified)
        self.tab_widget.addTab(self.windows_terminal_tab, "Windows Terminal")

        # Tab 3: QSS Theme Editor (FULLY IMPLEMENTED)
        self.qss_editor_tab = QSSThemeEditor(self.theme_manager)
        self.qss_editor_tab.themeModified.connect(self._on_theme_modified)
        self.tab_widget.addTab(self.qss_editor_tab, "QSS Themes")

        # Tab 4: CustomTkinter Theme Editor (FULLY IMPLEMENTED)
        self.ctk_editor_tab = CTkThemeEditor(self.theme_manager)
        self.ctk_editor_tab.themeModified.connect(self._on_theme_modified)
        self.tab_widget.addTab(self.ctk_editor_tab, "CustomTkinter")

        # Tab 5: Theme Converter (FULLY IMPLEMENTED)
        self.converter_tab = ConverterUI(self.theme_manager)
        self.converter_tab.conversionComplete.connect(self._on_conversion_complete)
        self.tab_widget.addTab(self.converter_tab, "Converter")

    def _create_placeholder_tab(self, title: str, description: str) -> QWidget:
        """
        Create a placeholder tab with title and description

        Args:
            title: Tab title
            description: Tab description

        Returns:
            QWidget placeholder tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 11pt; color: #666;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Coming soon message
        coming_soon = QLabel("[ Under Development ]")
        coming_soon.setStyleSheet("font-size: 14pt; color: #0078D4; margin-top: 20px;")
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(coming_soon)

        return widget

    def _setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        # New Theme
        new_action = QAction("&New Theme", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_theme)
        file_menu.addAction(new_action)

        # Open Theme File
        open_action = QAction("&Open Theme File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_theme)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # Save
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_theme)
        file_menu.addAction(save_action)

        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_theme_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        # Undo
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)

        # Redo
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)

        # View Menu
        view_menu = menubar.addMenu("&View")

        # Switch to tabs
        view_menu.addAction("Terminal Themes", lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction("Windows Terminal", lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction("QSS Themes", lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction("CustomTkinter", lambda: self.tab_widget.setCurrentIndex(3))
        view_menu.addAction("Theme Converter", lambda: self.tab_widget.setCurrentIndex(4))

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")

        # Convert JSON to QSS
        convert_json_qss = QAction("Convert Terminal � QSS", self)
        convert_json_qss.triggered.connect(self._convert_json_to_qss)
        tools_menu.addAction(convert_json_qss)

        # Convert QSS to JSON
        convert_qss_json = QAction("Convert QSS � Terminal", self)
        convert_qss_json.triggered.connect(self._convert_qss_to_json)
        tools_menu.addAction(convert_qss_json)

        tools_menu.addSeparator()

        # Image Converter
        image_converter = QAction("Image Converter", self)
        image_converter.triggered.connect(self._open_image_converter)
        tools_menu.addAction(image_converter)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        # Documentation
        docs_action = QAction("Documentation", self)
        docs_action.setShortcut("F1")
        docs_action.triggered.connect(self._show_documentation)
        help_menu.addAction(docs_action)

        # About
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    # ==================== Menu Actions ====================

    def _new_theme(self):
        """Create new theme"""
        QMessageBox.information(self, "New Theme", "New theme functionality coming soon!")

    def _open_theme(self):
        """Open theme file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Theme File",
            str(self.theme_manager.themes_dir),
            "Theme Files (*.json *.qss);;All Files (*)"
        )
        if filename:
            self.status_bar.showMessage(f"Opened: {filename}")

    def _save_theme(self):
        """Save current theme"""
        if self.current_file:
            self.status_bar.showMessage(f"Saved: {self.current_file}")
        else:
            self._save_theme_as()

    def _save_theme_as(self):
        """Save theme as new file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Theme As",
            str(self.theme_manager.themes_dir),
            "JSON Files (*.json);;QSS Files (*.qss);;All Files (*)"
        )
        if filename:
            self.current_file = filename
            self.status_bar.showMessage(f"Saved as: {filename}")

    def _undo(self):
        """Undo last action"""
        pass  # TODO: Implement undo system

    def _redo(self):
        """Redo last undone action"""
        pass  # TODO: Implement redo system

    def _convert_json_to_qss(self):
        """Convert Terminal JSON theme to QSS"""
        self.tab_widget.setCurrentIndex(4)  # Switch to Converter tab
        QMessageBox.information(self, "Converter", "Theme conversion functionality coming soon!")

    def _convert_qss_to_json(self):
        """Convert QSS theme to Terminal JSON"""
        self.tab_widget.setCurrentIndex(4)  # Switch to Converter tab
        QMessageBox.information(self, "Converter", "Theme conversion functionality coming soon!")

    def _open_image_converter(self):
        """Open Image Converter utility"""
        QMessageBox.information(
            self,
            "Image Converter",
            "Image Converter utility is being refactored to PyQt6.\n"
            "This feature will be available in a future update."
        )

    def _show_documentation(self):
        """Show documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "Theme Editor v1.0\n\n"
            "Multi-format theme editor supporting:\n"
            "* JSON Terminal Themes (20 colors)\n"
            "* Windows Terminal Integration\n"
            "* QSS Themes (PyQt6)\n"
            "* CustomTkinter Themes\n\n"
            "For detailed documentation, see:\n"
            "help/README.md"
        )

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Theme Editor",
            "<h2>Theme Editor v1.0</h2>"
            "<p><b>Universal Multi-Format Theme Editor</b></p>"
            "<p>Create, edit, and convert themes across multiple formats:</p>"
            "<ul>"
            "<li>JSON Terminal Themes</li>"
            "<li>Windows Terminal Settings</li>"
            "<li>Qt Style Sheets (QSS)</li>"
            "<li>CustomTkinter Themes</li>"
            "</ul>"
            "<p><b>Author:</b> Rafal Staska</p>"
            "<p><b>License:</b> MIT</p>"
            "<p><b>Built with:</b> PyQt6</p>"
        )

    def _on_theme_modified(self):
        """Handle theme modification signal"""
        self.unsaved_changes = True
        self.status_bar.showMessage("Theme modified (unsaved)", 3000)

    def _on_conversion_complete(self, target_format: str):
        """Handle theme conversion completion"""
        self.status_bar.showMessage(f"Conversion to {target_format} complete", 5000)

    def closeEvent(self, event):
        """Handle window close event"""
        # Check for unsaved changes in all editors
        has_unsaved = False

        if hasattr(self, 'terminal_editor_tab'):
            has_unsaved = has_unsaved or self.terminal_editor_tab.has_unsaved_changes()

        if hasattr(self, 'qss_editor_tab'):
            has_unsaved = has_unsaved or self.qss_editor_tab.has_unsaved_changes()

        if has_unsaved or self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                # Save terminal themes if modified
                if hasattr(self, 'terminal_editor_tab') and self.terminal_editor_tab.has_unsaved_changes():
                    self.terminal_editor_tab._save_themes()

                # Save QSS theme if modified
                if hasattr(self, 'qss_editor_tab') and self.qss_editor_tab.has_unsaved_changes():
                    self.qss_editor_tab._save_theme()

                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Theme Editor")
    app.setOrganizationName("RafalekS")
    app.setApplicationVersion("1.0.0")

    # Create and show main window
    window = ThemeEditorMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
