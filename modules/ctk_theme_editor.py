"""
CustomTkinter Theme Editor
Editor for CustomTkinter themes with light/dark mode support
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QMessageBox, QFileDialog, QSplitter,
    QTextEdit, QScrollArea, QSizePolicy, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
import json
from .theme_manager import ThemeManager
from .color_picker import ColorPickerButton


class CTkThemeEditor(QWidget):
    """
    CustomTkinter theme editor
    - Edit light/dark mode color pairs
    - Widget-specific styling
    - JSON structure editor
    """

    themeModified = pyqtSignal()

    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.current_file = None
        self.theme_data = None
        self.color_pickers = {}

        self._setup_ui()
        self._load_default_theme()

    def _setup_ui(self):
        """Setup editor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Top toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Main content: Color editor + JSON editor
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Color palette editor (40%)
        color_editor = self._create_color_editor()
        splitter.addWidget(color_editor)

        # Right: JSON editor (60%)
        json_editor = self._create_json_editor()
        splitter.addWidget(json_editor)

        # Set splitter proportions
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

        layout.addWidget(splitter, 1)

    def _create_toolbar(self) -> QWidget:
        """Create top toolbar"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(3)

        # File operations
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self._new_theme)
        toolbar_layout.addWidget(self.new_btn)

        self.open_btn = QPushButton("Open...")
        self.open_btn.clicked.connect(self._open_theme)
        toolbar_layout.addWidget(self.open_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_theme)
        toolbar_layout.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("Save As...")
        self.save_as_btn.clicked.connect(self._save_theme_as)
        toolbar_layout.addWidget(self.save_as_btn)

        toolbar_layout.addSpacing(10)

        # Current file label
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: gray; font-style: italic;")
        toolbar_layout.addWidget(self.file_label, 1)

        return toolbar

    def _create_color_editor(self) -> QScrollArea:
        """Create color palette editor"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(2, 2, 2, 2)
        container_layout.setSpacing(2)

        # Theme name
        name_group = QGroupBox("Theme Name")
        name_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        name_layout = QVBoxLayout(name_group)
        self.theme_name_input = QLineEdit()
        self.theme_name_input.setPlaceholderText("Enter theme name...")
        self.theme_name_input.textChanged.connect(self._on_theme_modified)
        name_layout.addWidget(self.theme_name_input)
        container_layout.addWidget(name_group)

        # CTk base colors (light/dark pairs)
        ctk_group = self._create_ctk_colors_group()
        container_layout.addWidget(ctk_group)

        # Button colors
        button_group = self._create_button_colors_group()
        container_layout.addWidget(button_group)

        # Entry colors
        entry_group = self._create_entry_colors_group()
        container_layout.addWidget(entry_group)

        # Action buttons
        update_btn = QPushButton("Update JSON from Colors")
        update_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        update_btn.clicked.connect(self._update_json_from_colors)
        container_layout.addWidget(update_btn)

        extract_btn = QPushButton("Extract Colors from JSON")
        extract_btn.setStyleSheet("padding: 5px;")
        extract_btn.clicked.connect(self._extract_colors_from_json)
        container_layout.addWidget(extract_btn)

        scroll.setWidget(container)
        return scroll

    def _create_ctk_colors_group(self) -> QGroupBox:
        """Create CTk base colors group"""
        group = QGroupBox("CTk Base Colors")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; padding-top: 5px; }")
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        layout = QGridLayout(group)
        layout.setSpacing(3)
        layout.setContentsMargins(3, 8, 3, 3)

        colors = [
            ("ctk_fg_light", "CTk FG (Light)"),
            ("ctk_fg_dark", "CTk FG (Dark)"),
        ]

        for i, (prop_name, label_text) in enumerate(colors):
            label = QLabel(f"{label_text}:")
            layout.addWidget(label, i, 0)

            picker = ColorPickerButton("#F0F0F0", label_text)
            picker.colorChanged.connect(self._on_theme_modified)
            self.color_pickers[prop_name] = picker
            layout.addWidget(picker, i, 1)

        return group

    def _create_button_colors_group(self) -> QGroupBox:
        """Create button colors group"""
        group = QGroupBox("CTkButton Colors")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; padding-top: 5px; }")
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        layout = QGridLayout(group)
        layout.setSpacing(3)
        layout.setContentsMargins(3, 8, 3, 3)

        colors = [
            ("button_fg_light", "Button FG (Light)"),
            ("button_fg_dark", "Button FG (Dark)"),
            ("button_hover_light", "Hover (Light)"),
            ("button_hover_dark", "Hover (Dark)"),
        ]

        for i, (prop_name, label_text) in enumerate(colors):
            row = i // 2
            col = (i % 2) * 2

            label = QLabel(f"{label_text}:")
            layout.addWidget(label, row, col)

            picker = ColorPickerButton("#2CC985", label_text)
            picker.colorChanged.connect(self._on_theme_modified)
            self.color_pickers[prop_name] = picker
            layout.addWidget(picker, row, col + 1)

        return group

    def _create_entry_colors_group(self) -> QGroupBox:
        """Create entry colors group"""
        group = QGroupBox("CTkEntry Colors")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; padding-top: 5px; }")
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        layout = QGridLayout(group)
        layout.setSpacing(3)
        layout.setContentsMargins(3, 8, 3, 3)

        colors = [
            ("entry_fg_light", "Entry FG (Light)"),
            ("entry_fg_dark", "Entry FG (Dark)"),
            ("entry_border_light", "Border (Light)"),
            ("entry_border_dark", "Border (Dark)"),
        ]

        for i, (prop_name, label_text) in enumerate(colors):
            row = i // 2
            col = (i % 2) * 2

            label = QLabel(f"{label_text}:")
            layout.addWidget(label, row, col)

            picker = ColorPickerButton("#F9F9FA", label_text)
            picker.colorChanged.connect(self._on_theme_modified)
            self.color_pickers[prop_name] = picker
            layout.addWidget(picker, row, col + 1)

        return group

    def _create_json_editor(self) -> QWidget:
        """Create JSON code editor"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel("CustomTkinter Theme JSON:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        # JSON editor
        self.json_editor = QTextEdit()
        self.json_editor.setFont(QFont("Consolas", 9))
        self.json_editor.setPlaceholderText("CustomTkinter theme JSON will appear here...")
        self.json_editor.textChanged.connect(self._on_json_changed)
        layout.addWidget(self.json_editor, 1)

        # Validate button
        validate_btn = QPushButton("Validate JSON")
        validate_btn.clicked.connect(self._validate_json)
        layout.addWidget(validate_btn)

        return container

    # ==================== Theme Operations ====================

    def _new_theme(self):
        """Create new theme"""
        self.theme_data = self._get_default_theme()
        self.current_file = None
        self.file_label.setText("Untitled")
        self._load_theme_to_ui()
        self.themeModified.emit()

    def _open_theme(self):
        """Open theme file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open CustomTkinter Theme",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.theme_data = json.load(f)

            self.current_file = Path(file_path)
            self.file_label.setText(self.current_file.name)
            self._load_theme_to_ui()

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to parse JSON:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")

    def _save_theme(self):
        """Save theme"""
        if not self.current_file:
            self._save_theme_as()
        else:
            self._save_to_file(self.current_file)

    def _save_theme_as(self):
        """Save theme as new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CustomTkinter Theme",
            "custom_theme.json",
            "JSON Files (*.json)"
        )

        if file_path:
            self.current_file = Path(file_path)
            self.file_label.setText(self.current_file.name)
            self._save_to_file(self.current_file)

    def _save_to_file(self, file_path: Path):
        """Save theme data to file"""
        try:
            # Update theme data from JSON editor
            self.theme_data = json.loads(self.json_editor.toPlainText())

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.theme_data, f, indent=2)

            QMessageBox.information(self, "Success", "Theme saved successfully")

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON Error", f"Invalid JSON:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

    def _load_default_theme(self):
        """Load default theme"""
        self.theme_data = self._get_default_theme()
        self._load_theme_to_ui()

    def _get_default_theme(self) -> dict:
        """Get default CustomTkinter theme structure"""
        return {
            "CTk": {
                "fg_color": ["gray92", "gray14"]
            },
            "CTkButton": {
                "corner_radius": 6,
                "border_width": 0,
                "fg_color": ["#2CC985", "#2FA572"],
                "hover_color": ["#0C955A", "#106A43"],
                "border_color": ["#3E454A", "#949A9F"],
                "text_color": ["gray98", "#DCE4EE"],
                "text_color_disabled": ["gray78", "gray68"]
            },
            "CTkEntry": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": ["#F9F9FA", "#343638"],
                "border_color": ["#979DA2", "#565B5E"],
                "text_color": ["gray10", "#DCE4EE"],
                "placeholder_text_color": ["gray52", "gray62"]
            },
            "CTkFont": {
                "Windows": {
                    "family": "Roboto",
                    "size": 13,
                    "weight": "normal"
                }
            }
        }

    def _load_theme_to_ui(self):
        """Load theme data to UI"""
        # Block signals
        self.json_editor.blockSignals(True)
        for picker in self.color_pickers.values():
            picker.blockSignals(True)

        # Update JSON editor
        self.json_editor.setPlainText(json.dumps(self.theme_data, indent=2))

        # Extract and load colors
        self._extract_colors_from_json()

        # Re-enable signals
        self.json_editor.blockSignals(False)
        for picker in self.color_pickers.values():
            picker.blockSignals(False)

    def _extract_colors_from_json(self):
        """Extract colors from JSON to color pickers"""
        try:
            data = json.loads(self.json_editor.toPlainText())

            # Extract CTk colors
            if "CTk" in data and "fg_color" in data["CTk"]:
                fg = data["CTk"]["fg_color"]
                if isinstance(fg, list) and len(fg) >= 2:
                    self.color_pickers["ctk_fg_light"].set_color(fg[0])
                    self.color_pickers["ctk_fg_dark"].set_color(fg[1])

            # Extract button colors
            if "CTkButton" in data:
                btn = data["CTkButton"]
                if "fg_color" in btn and isinstance(btn["fg_color"], list):
                    self.color_pickers["button_fg_light"].set_color(btn["fg_color"][0])
                    self.color_pickers["button_fg_dark"].set_color(btn["fg_color"][1])
                if "hover_color" in btn and isinstance(btn["hover_color"], list):
                    self.color_pickers["button_hover_light"].set_color(btn["hover_color"][0])
                    self.color_pickers["button_hover_dark"].set_color(btn["hover_color"][1])

            # Extract entry colors
            if "CTkEntry" in data:
                entry = data["CTkEntry"]
                if "fg_color" in entry and isinstance(entry["fg_color"], list):
                    self.color_pickers["entry_fg_light"].set_color(entry["fg_color"][0])
                    self.color_pickers["entry_fg_dark"].set_color(entry["fg_color"][1])
                if "border_color" in entry and isinstance(entry["border_color"], list):
                    self.color_pickers["entry_border_light"].set_color(entry["border_color"][0])
                    self.color_pickers["entry_border_dark"].set_color(entry["border_color"][1])

        except Exception as e:
            QMessageBox.warning(self, "Extract Error", f"Failed to extract colors:\n{e}")

    def _update_json_from_colors(self):
        """Update JSON from color picker values"""
        try:
            data = json.loads(self.json_editor.toPlainText())

            # Update CTk colors
            if "CTk" not in data:
                data["CTk"] = {}
            data["CTk"]["fg_color"] = [
                self.color_pickers["ctk_fg_light"].get_color(),
                self.color_pickers["ctk_fg_dark"].get_color()
            ]

            # Update button colors
            if "CTkButton" not in data:
                data["CTkButton"] = {}
            data["CTkButton"]["fg_color"] = [
                self.color_pickers["button_fg_light"].get_color(),
                self.color_pickers["button_fg_dark"].get_color()
            ]
            data["CTkButton"]["hover_color"] = [
                self.color_pickers["button_hover_light"].get_color(),
                self.color_pickers["button_hover_dark"].get_color()
            ]

            # Update entry colors
            if "CTkEntry" not in data:
                data["CTkEntry"] = {}
            data["CTkEntry"]["fg_color"] = [
                self.color_pickers["entry_fg_light"].get_color(),
                self.color_pickers["entry_fg_dark"].get_color()
            ]
            data["CTkEntry"]["border_color"] = [
                self.color_pickers["entry_border_light"].get_color(),
                self.color_pickers["entry_border_dark"].get_color()
            ]

            # Update JSON editor
            self.json_editor.blockSignals(True)
            self.json_editor.setPlainText(json.dumps(data, indent=2))
            self.json_editor.blockSignals(False)

            self.themeModified.emit()

        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Failed to update JSON:\n{e}")

    def _validate_json(self):
        """Validate JSON syntax"""
        try:
            json.loads(self.json_editor.toPlainText())
            QMessageBox.information(self, "Valid", "JSON is valid!")
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"JSON syntax error:\n{e}")

    def _on_theme_modified(self):
        """Handle theme modification"""
        self.themeModified.emit()

    def _on_json_changed(self):
        """Handle JSON editor changes"""
        self.themeModified.emit()
