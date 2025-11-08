"""
JSON Terminal Theme Editor
Editor for terminal color schemes (JSON format with 20 colors)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QComboBox, QPushButton, QLabel, QMessageBox, QInputDialog,
    QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from .theme_data import TerminalTheme
from .theme_manager import ThemeManager
from .color_picker import ColorPickerButton
from .preview_widgets import TerminalPreviewWidget


class JSONTerminalEditor(QWidget):
    """
    Complete JSON Terminal Theme Editor
    Features: 20-color editor, theme selector, create/duplicate/delete, live preview
    """

    # Signal emitted when theme is modified
    themeModified = pyqtSignal()

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.themes = {}  # Dict of theme_name -> TerminalTheme
        self.current_theme_name = None
        self.color_pickers = {}  # Dict of property_name -> ColorPickerButton
        self.unsaved_changes = False

        self._setup_ui()
        self._load_themes()

    def _setup_ui(self):
        """Setup editor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Top toolbar: Theme selector and actions
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Main content: Color editor + Preview (side by side)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Color editor
        color_editor = self._create_color_editor()
        splitter.addWidget(color_editor)

        # Right: Preview
        preview_widget = self._create_preview()
        splitter.addWidget(preview_widget)

        # Set splitter proportions (60% editor, 40% preview)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter, 1)  # Give stretch factor 1 to expand vertically

    def _create_toolbar(self) -> QWidget:
        """Create top toolbar with theme selector and action buttons"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(3)

        # Theme selector
        label = QLabel("Select Theme:")
        label.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(label)

        self.theme_selector = QComboBox()
        self.theme_selector.setMinimumWidth(250)
        self.theme_selector.currentTextChanged.connect(self._on_theme_selected)
        toolbar_layout.addWidget(self.theme_selector)

        toolbar_layout.addSpacing(20)

        # Action buttons
        self.new_btn = QPushButton("New Theme")
        self.new_btn.clicked.connect(self._create_new_theme)
        toolbar_layout.addWidget(self.new_btn)

        self.duplicate_btn = QPushButton("Duplicate")
        self.duplicate_btn.clicked.connect(self._duplicate_theme)
        toolbar_layout.addWidget(self.duplicate_btn)

        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self._rename_theme)
        toolbar_layout.addWidget(self.rename_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_theme)
        toolbar_layout.addWidget(self.delete_btn)

        toolbar_layout.addStretch()

        # Save button
        self.save_btn = QPushButton("Save All Themes")
        self.save_btn.setStyleSheet("font-weight: bold; padding: 6px 15px;")
        self.save_btn.clicked.connect(self._save_themes)
        toolbar_layout.addWidget(self.save_btn)

        return toolbar

    def _create_color_editor(self) -> QWidget:
        """Create color editor with 20 color pickers"""
        # Scrollable area for color pickers
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(2, 2, 2, 2)
        container_layout.setSpacing(2)

        # Title - REMOVE to save space
        # container_layout.addWidget(title)

        # Color picker groups
        # Group 1: Basic colors
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

        # Group 2: ANSI colors (normal)
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

        # Group 3: Bright ANSI colors
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

        container_layout.addStretch()
        scroll.setWidget(container)

        return scroll

    def _create_color_group(self, title: str, colors: list) -> QGroupBox:
        """
        Create a group box with color pickers

        Args:
            title: Group box title
            colors: List of (property_name, display_label) tuples

        Returns:
            QGroupBox with color pickers
        """
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; padding-top: 5px; }")

        # Use grid layout (2 columns)
        layout = QGridLayout(group)
        layout.setSpacing(3)
        layout.setContentsMargins(3, 8, 3, 3)

        for i, (prop_name, label_text) in enumerate(colors):
            row = i // 2
            col = (i % 2) * 2  # 0 or 2 (label, picker, label, picker)

            # Label
            label = QLabel(f"{label_text}:")
            layout.addWidget(label, row, col)

            # Color picker
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
        layout.addWidget(self.preview, 1)  # Expand to fill space

        return container

    # ==================== Theme Management ====================

    def _load_themes(self):
        """Load themes from theme manager"""
        self.themes = self.theme_manager.load_json_themes()

        # Populate theme selector
        self.theme_selector.clear()
        if self.themes:
            self.theme_selector.addItems(sorted(self.themes.keys()))
            self.theme_selector.setCurrentIndex(0)
        else:
            # No themes - create a default one
            self._create_default_theme()

    def _create_default_theme(self):
        """Create a default theme if none exist"""
        default_theme = TerminalTheme(
            name="Default",
            background="#282828",
            foreground="#EBDBB2",
            cursor="#EBDBB2",
            selection="#504945",
            black="#282828",
            red="#CC241D",
            green="#98971A",
            yellow="#D79921",
            blue="#458588",
            purple="#B16286",
            cyan="#689D6A",
            white="#A89984",
            brightBlack="#928374",
            brightRed="#FB4934",
            brightGreen="#B8BB26",
            brightYellow="#FABD2F",
            brightBlue="#83A598",
            brightPurple="#D3869B",
            brightCyan="#8EC07C",
            brightWhite="#EBDBB2"
        )
        self.themes["Default"] = default_theme
        self.theme_selector.addItem("Default")
        self.theme_selector.setCurrentIndex(0)

    def _on_theme_selected(self, theme_name: str):
        """Handle theme selection change"""
        if not theme_name or theme_name not in self.themes:
            return

        # Check for unsaved changes
        if self.unsaved_changes and self.current_theme_name:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Theme '{self.current_theme_name}' has unsaved changes. Save before switching?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._save_current_theme()
            elif reply == QMessageBox.StandardButton.Cancel:
                # Revert selection
                if self.current_theme_name:
                    self.theme_selector.setCurrentText(self.current_theme_name)
                return

        self.current_theme_name = theme_name
        self.unsaved_changes = False

        # Load theme into color pickers (block signals to prevent false "modified" trigger)
        theme = self.themes[theme_name]
        for prop_name, picker in self.color_pickers.items():
            picker.blockSignals(True)  # Block signals during initialization
            color = getattr(theme, prop_name)
            picker.set_color(color)
            picker.blockSignals(False)  # Re-enable signals

        # Update preview
        self.preview.set_theme(theme)

    def _on_color_changed(self, property_name: str):
        """Handle color picker change"""
        if not self.current_theme_name:
            return

        # Update theme object
        theme = self.themes[self.current_theme_name]
        new_color = self.color_pickers[property_name].get_color()
        setattr(theme, property_name, new_color)

        # Mark as unsaved
        self.unsaved_changes = True
        self.themeModified.emit()

        # Update preview
        self.preview.set_theme(theme)

    # ==================== Theme Actions ====================

    def _create_new_theme(self):
        """Create a new blank theme"""
        name, ok = QInputDialog.getText(
            self,
            "New Theme",
            "Enter theme name:"
        )

        if ok and name:
            # Check if name already exists
            if name in self.themes:
                QMessageBox.warning(self, "Name Exists", f"A theme named '{name}' already exists.")
                return

            # Create new theme (copy from current or use default)
            if self.current_theme_name:
                # Copy current theme
                current = self.themes[self.current_theme_name]
                new_theme = TerminalTheme(**current.to_dict())
                new_theme.name = name
            else:
                # Create blank theme
                new_theme = TerminalTheme(
                    name=name,
                    background="#000000",
                    foreground="#FFFFFF",
                    cursor="#FFFFFF",
                    selection="#444444",
                    black="#000000",
                    red="#CC0000",
                    green="#00CC00",
                    yellow="#CCCC00",
                    blue="#0000CC",
                    purple="#CC00CC",
                    cyan="#00CCCC",
                    white="#CCCCCC",
                    brightBlack="#666666",
                    brightRed="#FF0000",
                    brightGreen="#00FF00",
                    brightYellow="#FFFF00",
                    brightBlue="#0000FF",
                    brightPurple="#FF00FF",
                    brightCyan="#00FFFF",
                    brightWhite="#FFFFFF"
                )

            self.themes[name] = new_theme
            self.theme_selector.addItem(name)
            self.theme_selector.setCurrentText(name)
            self.unsaved_changes = True

    def _duplicate_theme(self):
        """Duplicate current theme"""
        if not self.current_theme_name:
            QMessageBox.warning(self, "No Theme", "Please select a theme to duplicate.")
            return

        name, ok = QInputDialog.getText(
            self,
            "Duplicate Theme",
            f"Enter name for duplicate of '{self.current_theme_name}':",
            text=f"{self.current_theme_name} Copy"
        )

        if ok and name:
            # Check if name already exists
            if name in self.themes:
                QMessageBox.warning(self, "Name Exists", f"A theme named '{name}' already exists.")
                return

            # Duplicate theme
            current = self.themes[self.current_theme_name]
            duplicate = TerminalTheme(**current.to_dict())
            duplicate.name = name

            self.themes[name] = duplicate
            self.theme_selector.addItem(name)
            self.theme_selector.setCurrentText(name)
            self.unsaved_changes = True

    def _rename_theme(self):
        """Rename current theme"""
        if not self.current_theme_name:
            QMessageBox.warning(self, "No Theme", "Please select a theme to rename.")
            return

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Theme",
            f"Enter new name for '{self.current_theme_name}':",
            text=self.current_theme_name
        )

        if ok and new_name and new_name != self.current_theme_name:
            # Check if name already exists
            if new_name in self.themes:
                QMessageBox.warning(self, "Name Exists", f"A theme named '{new_name}' already exists.")
                return

            # Rename theme
            theme = self.themes.pop(self.current_theme_name)
            theme.name = new_name
            self.themes[new_name] = theme

            # Update selector
            index = self.theme_selector.currentIndex()
            self.theme_selector.removeItem(index)
            self.theme_selector.insertItem(index, new_name)
            self.theme_selector.setCurrentIndex(index)

            self.current_theme_name = new_name
            self.unsaved_changes = True

    def _delete_theme(self):
        """Delete current theme"""
        if not self.current_theme_name:
            QMessageBox.warning(self, "No Theme", "Please select a theme to delete.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Theme",
            f"Are you sure you want to delete theme '{self.current_theme_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Delete theme
            del self.themes[self.current_theme_name]

            # Remove from selector
            index = self.theme_selector.currentIndex()
            self.theme_selector.removeItem(index)

            self.current_theme_name = None
            self.unsaved_changes = True

    def _save_current_theme(self):
        """Save current theme to themes dict"""
        if not self.current_theme_name:
            return

        # Theme is already updated in self.themes via _on_color_changed
        # Just mark as saved
        self.unsaved_changes = False

    def _save_themes(self):
        """Save all themes to file"""
        try:
            self.theme_manager.save_json_themes(self.themes)
            self.unsaved_changes = False
            QMessageBox.information(
                self,
                "Saved",
                f"Successfully saved {len(self.themes)} themes to themes.json"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save themes:\n{str(e)}"
            )

    # ==================== Public Methods ====================

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.unsaved_changes

    def get_current_theme(self) -> TerminalTheme:
        """Get current theme"""
        if self.current_theme_name:
            return self.themes.get(self.current_theme_name)
        return None
