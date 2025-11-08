"""
Windows Terminal Integration
Edit themes in Windows Terminal settings.json with backup and safety features
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QMessageBox, QFileDialog, QListWidget,
    QLineEdit, QSplitter, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import json
import os
from datetime import datetime
from .theme_data import TerminalTheme
from .theme_manager import ThemeManager
from .color_picker import ColorPickerButton
from .preview_widgets import TerminalPreviewWidget


class WindowsTerminalEditor(QWidget):
    """
    Windows Terminal settings.json integration
    - Detect Windows Terminal installation
    - Edit themes in settings.json
    - Backup before modifications
    - Import/Export standalone themes
    """

    themeModified = pyqtSignal()

    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.settings_path = None
        self.settings_data = None
        self.current_theme = None
        self.color_pickers = {}

        self._setup_ui()
        self._detect_settings_path()

    def _setup_ui(self):
        """Setup editor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Top toolbar: Settings path and actions
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Main content: Theme list + Editor + Preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Theme list (20%)
        theme_list = self._create_theme_list()
        splitter.addWidget(theme_list)

        # Middle: Color editor (40%)
        color_editor = self._create_color_editor()
        splitter.addWidget(color_editor)

        # Right: Preview (40%)
        preview_widget = self._create_preview()
        splitter.addWidget(preview_widget)

        # Set splitter proportions
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 4)

        layout.addWidget(splitter, 1)  # Expand to fill space

    def _create_toolbar(self) -> QWidget:
        """Create top toolbar with settings path and actions"""
        toolbar = QWidget()
        toolbar_layout = QVBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(3)

        # Settings path row
        path_row = QWidget()
        path_layout = QHBoxLayout(path_row)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(5)

        path_label = QLabel("Windows Terminal settings.json:")
        path_label.setStyleSheet("font-weight: bold;")
        path_layout.addWidget(path_label)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Not found - click Browse to locate")
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input, 1)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_settings)
        path_layout.addWidget(browse_btn)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._load_settings)
        path_layout.addWidget(load_btn)

        toolbar_layout.addWidget(path_row)

        # Action buttons row
        actions_row = QWidget()
        actions_layout = QHBoxLayout(actions_row)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(5)

        self.add_btn = QPushButton("Add New Theme")
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._add_theme)
        actions_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Theme")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_theme)
        actions_layout.addWidget(self.delete_btn)

        self.import_btn = QPushButton("Import from JSON...")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._import_theme)
        actions_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("Export to JSON...")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._export_theme)
        actions_layout.addWidget(self.export_btn)

        actions_layout.addStretch()

        self.save_btn = QPushButton("Save to settings.json")
        self.save_btn.setStyleSheet("font-weight: bold; padding: 5px 15px;")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_settings)
        actions_layout.addWidget(self.save_btn)

        toolbar_layout.addWidget(actions_row)

        return toolbar

    def _create_theme_list(self) -> QWidget:
        """Create theme list widget"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel("Themes in settings.json:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        self.theme_list = QListWidget()
        self.theme_list.currentItemChanged.connect(self._on_theme_selected)
        layout.addWidget(self.theme_list, 1)

        return container

    def _create_color_editor(self) -> QScrollArea:
        """Create color editor panel (same as JSON editor)"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(2, 2, 2, 2)
        container_layout.setSpacing(2)

        # Theme name input
        name_group = QGroupBox("Theme Name")
        name_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        name_layout = QHBoxLayout(name_group)
        self.theme_name_input = QLineEdit()
        self.theme_name_input.setPlaceholderText("Enter theme name...")
        self.theme_name_input.textChanged.connect(self._on_name_changed)
        name_layout.addWidget(self.theme_name_input)
        container_layout.addWidget(name_group)

        # Basic colors (4 colors)
        basic_group = self._create_color_group(
            "Basic Colors",
            [
                ("background", "Background"),
                ("foreground", "Foreground"),
                ("cursor", "Cursor"),
                ("selection", "Selection"),
            ]
        )
        container_layout.addWidget(basic_group)

        # ANSI colors (8 colors)
        ansi_group = self._create_color_group(
            "ANSI Colors",
            [
                ("black", "Black"),
                ("red", "Red"),
                ("green", "Green"),
                ("yellow", "Yellow"),
                ("blue", "Blue"),
                ("purple", "Purple"),
                ("cyan", "Cyan"),
                ("white", "White"),
            ]
        )
        container_layout.addWidget(ansi_group)

        # Bright ANSI colors (8 colors)
        bright_group = self._create_color_group(
            "Bright ANSI Colors",
            [
                ("brightBlack", "Bright Black"),
                ("brightRed", "Bright Red"),
                ("brightGreen", "Bright Green"),
                ("brightYellow", "Bright Yellow"),
                ("brightBlue", "Bright Blue"),
                ("brightPurple", "Bright Purple"),
                ("brightCyan", "Bright Cyan"),
                ("brightWhite", "Bright White"),
            ]
        )
        container_layout.addWidget(bright_group)

        scroll.setWidget(container)
        return scroll

    def _create_color_group(self, title: str, colors: list) -> QGroupBox:
        """Create a group box with color pickers"""
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; padding-top: 5px; }")
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        layout = QGridLayout(group)
        layout.setSpacing(3)
        layout.setContentsMargins(3, 8, 3, 3)

        for i, (prop_name, label_text) in enumerate(colors):
            row = i // 2
            col = (i % 2) * 2

            label = QLabel(f"{label_text}:")
            layout.addWidget(label, row, col)

            picker = ColorPickerButton("#000000", label_text)
            picker.colorChanged.connect(lambda _, p=prop_name: self._on_color_changed(p))
            self.color_pickers[prop_name] = picker
            layout.addWidget(picker, row, col + 1)

        return group

    def _create_preview(self) -> QWidget:
        """Create preview panel"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.preview = TerminalPreviewWidget()
        layout.addWidget(self.preview, 1)

        return container

    # ==================== Settings Management ====================

    def _detect_settings_path(self):
        """Auto-detect Windows Terminal settings.json path"""
        if os.name != 'nt':  # Not Windows
            return

        # Common Windows Terminal settings paths
        local_appdata = os.environ.get('LOCALAPPDATA', '')
        if not local_appdata:
            return

        possible_paths = [
            Path(local_appdata) / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState" / "settings.json",
            Path(local_appdata) / "Packages" / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe" / "LocalState" / "settings.json",
        ]

        for path in possible_paths:
            if path.exists():
                self.settings_path = path
                self.path_input.setText(str(path))
                self._load_settings()
                return

    def _browse_settings(self):
        """Browse for settings.json file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Windows Terminal settings.json",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*.*)"
        )

        if file_path:
            self.settings_path = Path(file_path)
            self.path_input.setText(str(self.settings_path))
            self._load_settings()

    def _load_settings(self):
        """Load settings.json and populate theme list"""
        if not self.settings_path or not self.settings_path.exists():
            QMessageBox.warning(self, "Error", "Settings file not found. Please browse to locate it.")
            return

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                self.settings_data = json.load(f)

            # Extract schemes
            schemes = self.settings_data.get('schemes', [])
            if not schemes:
                QMessageBox.information(self, "No Themes", "No color schemes found in settings.json")
                return

            # Populate theme list
            self.theme_list.clear()
            for scheme in schemes:
                self.theme_list.addItem(scheme.get('name', 'Unnamed'))

            # Enable buttons
            self.add_btn.setEnabled(True)
            self.import_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

            QMessageBox.information(self, "Success", f"Loaded {len(schemes)} themes from settings.json")

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to parse settings.json:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings.json:\n{e}")

    def _on_theme_selected(self):
        """Handle theme selection from list"""
        current_item = self.theme_list.currentItem()
        if not current_item or not self.settings_data:
            return

        theme_name = current_item.text()
        schemes = self.settings_data.get('schemes', [])

        # Find theme
        for scheme in schemes:
            if scheme.get('name') == theme_name:
                self._load_theme_data(scheme)
                self.delete_btn.setEnabled(True)
                self.export_btn.setEnabled(True)
                break

    def _load_theme_data(self, scheme: dict):
        """Load theme data into editor"""
        self.current_theme = scheme

        # Block signals during load
        self.theme_name_input.blockSignals(True)
        for picker in self.color_pickers.values():
            picker.blockSignals(True)

        # Load name
        self.theme_name_input.setText(scheme.get('name', ''))

        # Load colors
        for prop_name, picker in self.color_pickers.items():
            color = scheme.get(prop_name, '#000000')
            picker.set_color(color)

        # Update preview
        self._update_preview()

        # Re-enable signals
        self.theme_name_input.blockSignals(False)
        for picker in self.color_pickers.values():
            picker.blockSignals(False)

    def _on_name_changed(self):
        """Handle theme name change"""
        if self.current_theme:
            self.current_theme['name'] = self.theme_name_input.text()
            self.themeModified.emit()

    def _on_color_changed(self, prop_name: str):
        """Handle color change"""
        if self.current_theme:
            color = self.color_pickers[prop_name].get_color()
            self.current_theme[prop_name] = color
            self._update_preview()
            self.themeModified.emit()

    def _update_preview(self):
        """Update preview with current theme"""
        if not self.current_theme:
            return

        # Convert to TerminalTheme for preview
        theme = TerminalTheme(
            name=self.current_theme.get('name', 'Preview'),
            background=self.current_theme.get('background', '#000000'),
            foreground=self.current_theme.get('foreground', '#FFFFFF'),
            cursor=self.current_theme.get('cursor', '#FFFFFF'),
            selection=self.current_theme.get('selection', '#FFFFFF'),
            black=self.current_theme.get('black', '#000000'),
            red=self.current_theme.get('red', '#FF0000'),
            green=self.current_theme.get('green', '#00FF00'),
            yellow=self.current_theme.get('yellow', '#FFFF00'),
            blue=self.current_theme.get('blue', '#0000FF'),
            purple=self.current_theme.get('purple', '#FF00FF'),
            cyan=self.current_theme.get('cyan', '#00FFFF'),
            white=self.current_theme.get('white', '#FFFFFF'),
            brightBlack=self.current_theme.get('brightBlack', '#808080'),
            brightRed=self.current_theme.get('brightRed', '#FF0000'),
            brightGreen=self.current_theme.get('brightGreen', '#00FF00'),
            brightYellow=self.current_theme.get('brightYellow', '#FFFF00'),
            brightBlue=self.current_theme.get('brightBlue', '#0000FF'),
            brightPurple=self.current_theme.get('brightPurple', '#FF00FF'),
            brightCyan=self.current_theme.get('brightCyan', '#00FFFF'),
            brightWhite=self.current_theme.get('brightWhite', '#FFFFFF')
        )
        self.preview.set_theme(theme)

    # ==================== Theme Operations ====================

    def _add_theme(self):
        """Add new theme to settings"""
        # Create default theme
        new_theme = {
            "name": "New Theme",
            "background": "#000000",
            "foreground": "#FFFFFF",
            "cursor": "#FFFFFF",
            "selection": "#FFFFFF",
            "black": "#000000",
            "red": "#FF0000",
            "green": "#00FF00",
            "yellow": "#FFFF00",
            "blue": "#0000FF",
            "purple": "#FF00FF",
            "cyan": "#00FFFF",
            "white": "#FFFFFF",
            "brightBlack": "#808080",
            "brightRed": "#FF8080",
            "brightGreen": "#80FF80",
            "brightYellow": "#FFFF80",
            "brightBlue": "#8080FF",
            "brightPurple": "#FF80FF",
            "brightCyan": "#80FFFF",
            "brightWhite": "#FFFFFF"
        }

        # Add to settings
        if 'schemes' not in self.settings_data:
            self.settings_data['schemes'] = []

        self.settings_data['schemes'].append(new_theme)

        # Refresh list
        self.theme_list.addItem("New Theme")
        self.theme_list.setCurrentRow(self.theme_list.count() - 1)

        self.themeModified.emit()

    def _delete_theme(self):
        """Delete selected theme"""
        current_item = self.theme_list.currentItem()
        if not current_item:
            return

        reply = QMessageBox.question(
            self,
            "Delete Theme",
            f"Are you sure you want to delete '{current_item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            theme_name = current_item.text()
            schemes = self.settings_data.get('schemes', [])

            # Remove from settings
            self.settings_data['schemes'] = [s for s in schemes if s.get('name') != theme_name]

            # Remove from list
            row = self.theme_list.currentRow()
            self.theme_list.takeItem(row)

            self.current_theme = None
            self.delete_btn.setEnabled(False)
            self.export_btn.setEnabled(False)

            self.themeModified.emit()

    def _import_theme(self):
        """Import theme from standalone JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Theme from JSON",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )

        if not file_path:
            return

        try:
            themes = self.theme_manager.load_json_themes(file_path)
            if not themes:
                QMessageBox.warning(self, "Error", "No valid themes found in file")
                return

            # Import all themes
            for theme in themes.values():
                scheme = theme.to_dict()
                self.settings_data['schemes'].append(scheme)
                self.theme_list.addItem(theme.name)

            QMessageBox.information(self, "Success", f"Imported {len(themes)} theme(s)")
            self.themeModified.emit()

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import themes:\n{e}")

    def _export_theme(self):
        """Export current theme to standalone JSON file"""
        if not self.current_theme:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Theme to JSON",
            f"{self.current_theme['name']}.json",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            # Convert to TerminalTheme
            theme = TerminalTheme(
                name=self.current_theme['name'],
                **{k: v for k, v in self.current_theme.items() if k != 'name'}
            )

            # Save as single-theme JSON
            themes_dict = {theme.name: theme.to_dict()}
            self.theme_manager.save_json_themes(file_path, themes_dict)

            QMessageBox.information(self, "Success", "Theme exported successfully")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export theme:\n{e}")

    def _save_settings(self):
        """Save settings.json with backup"""
        if not self.settings_path or not self.settings_data:
            return

        # Create backup
        backup_path = self.settings_path.parent / f"settings.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Backup original
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_data)

            # Save new settings
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings_data, f, indent=4)

            QMessageBox.information(
                self,
                "Success",
                f"Settings saved successfully!\n\nBackup created:\n{backup_path.name}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save settings:\n{e}")
