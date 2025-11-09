"""
Qt Widget Theme Editor
Editor for Qt Widget themes with comprehensive widget selector and live preview
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QListWidget, QTextEdit, QSplitter, QGroupBox, QLineEdit, QMessageBox,
    QInputDialog, QScrollArea, QSpinBox, QRadioButton, QCheckBox,
    QProgressBar, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from typing import Dict, Optional
from .theme_data import QtWidgetTheme
from .theme_manager import ThemeManager


# Comprehensive list of Qt widgets and selectors
QT_WIDGET_SELECTORS = [
    # Main containers
    "QMainWindow",
    "QWidget",
    "QDialog",
    "QFrame",

    # Layout widgets
    "QGroupBox",
    "QGroupBox::title",
    "QTabWidget",
    "QTabWidget::pane",
    "QTabWidget::tab-bar",
    "QTabBar",
    "QTabBar::tab",
    "QTabBar::tab:selected",
    "QTabBar::tab:!selected",
    "QTabBar::tab:hover",
    "QSplitter",
    "QSplitter::handle",
    "QSplitter::handle:horizontal",
    "QSplitter::handle:vertical",

    # Buttons
    "QPushButton",
    "QPushButton:hover",
    "QPushButton:pressed",
    "QPushButton:disabled",
    "QPushButton:checked",
    "QPushButton:flat",
    "QToolButton",
    "QToolButton:hover",
    "QToolButton:pressed",
    "QRadioButton",
    "QRadioButton::indicator",
    "QRadioButton::indicator:checked",
    "QRadioButton::indicator:unchecked",
    "QCheckBox",
    "QCheckBox::indicator",
    "QCheckBox::indicator:checked",
    "QCheckBox::indicator:unchecked",

    # Input fields
    "QLineEdit",
    "QLineEdit:focus",
    "QLineEdit:read-only",
    "QLineEdit:disabled",
    "QTextEdit",
    "QTextEdit:focus",
    "QTextEdit:read-only",
    "QPlainTextEdit",
    "QPlainTextEdit:focus",
    "QSpinBox",
    "QSpinBox::up-button",
    "QSpinBox::down-button",
    "QDoubleSpinBox",
    "QDoubleSpinBox::up-button",
    "QDoubleSpinBox::down-button",

    # Selection widgets
    "QComboBox",
    "QComboBox:hover",
    "QComboBox:on",
    "QComboBox::drop-down",
    "QComboBox::down-arrow",
    "QComboBox QAbstractItemView",
    "QListWidget",
    "QListWidget::item",
    "QListWidget::item:selected",
    "QListWidget::item:hover",
    "QListView",
    "QListView::item",
    "QListView::item:selected",
    "QTreeWidget",
    "QTreeWidget::item",
    "QTreeWidget::item:selected",
    "QTreeWidget::branch",
    "QTreeView",
    "QTreeView::item",
    "QTreeView::item:selected",
    "QTreeView::branch",
    "QTableWidget",
    "QTableWidget::item",
    "QTableWidget::item:selected",
    "QTableView",
    "QTableView::item",
    "QTableView::item:selected",
    "QHeaderView",
    "QHeaderView::section",

    # Display widgets
    "QLabel",
    "QLCDNumber",
    "QProgressBar",
    "QProgressBar::chunk",

    # Containers and scrolling
    "QScrollArea",
    "QScrollBar:vertical",
    "QScrollBar:horizontal",
    "QScrollBar::handle:vertical",
    "QScrollBar::handle:horizontal",
    "QScrollBar::handle:vertical:hover",
    "QScrollBar::handle:horizontal:hover",
    "QScrollBar::add-line:vertical",
    "QScrollBar::add-line:horizontal",
    "QScrollBar::sub-line:vertical",
    "QScrollBar::sub-line:horizontal",
    "QScrollBar::add-page:vertical",
    "QScrollBar::add-page:horizontal",
    "QScrollBar::sub-page:vertical",
    "QScrollBar::sub-page:horizontal",

    # Sliders
    "QSlider",
    "QSlider::groove:horizontal",
    "QSlider::groove:vertical",
    "QSlider::handle:horizontal",
    "QSlider::handle:vertical",
    "QSlider::add-page:horizontal",
    "QSlider::add-page:vertical",
    "QSlider::sub-page:horizontal",
    "QSlider::sub-page:vertical",

    # Menu and toolbar
    "QMenuBar",
    "QMenuBar::item",
    "QMenuBar::item:selected",
    "QMenuBar::item:pressed",
    "QMenu",
    "QMenu::item",
    "QMenu::item:selected",
    "QMenu::separator",
    "QToolBar",
    "QToolBar::separator",
    "QStatusBar",

    # Dialogs
    "QMessageBox",
    "QFileDialog",
    "QColorDialog",
    "QFontDialog",

    # Dock widgets
    "QDockWidget",
    "QDockWidget::title",
    "QDockWidget::close-button",
    "QDockWidget::float-button",

    # Other widgets
    "QCalendarWidget",
    "QDateEdit",
    "QTimeEdit",
    "QDateTimeEdit",
    "QDial",
    "QToolBox",
    "QToolBox::tab",
]


class QtWidgetThemeEditor(QWidget):
    """Qt Widget Theme Editor with live preview"""

    themeModified = pyqtSignal()  # Emitted when theme is modified

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.themes: Dict[str, QtWidgetTheme] = {}
        self.current_theme_name: Optional[str] = None
        self.current_theme: Optional[QtWidgetTheme] = None
        self.unsaved_changes = False

        self._setup_ui()
        self._load_themes()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top controls
        controls_layout = QHBoxLayout()

        # Theme selector
        controls_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        controls_layout.addWidget(self.theme_combo, 1)

        # Theme management buttons
        self.new_theme_btn = QPushButton("New Theme")
        self.new_theme_btn.clicked.connect(self._new_theme)
        controls_layout.addWidget(self.new_theme_btn)

        self.duplicate_theme_btn = QPushButton("Duplicate")
        self.duplicate_theme_btn.clicked.connect(self._duplicate_theme)
        controls_layout.addWidget(self.duplicate_theme_btn)

        self.delete_theme_btn = QPushButton("Delete")
        self.delete_theme_btn.clicked.connect(self._delete_theme)
        controls_layout.addWidget(self.delete_theme_btn)

        controls_layout.addWidget(QLabel("|"))  # Separator

        self.load_file_btn = QPushButton("Load from File...")
        self.load_file_btn.clicked.connect(self._load_from_file)
        controls_layout.addWidget(self.load_file_btn)

        self.save_btn = QPushButton("Save All")
        self.save_btn.clicked.connect(self._save_themes)
        controls_layout.addWidget(self.save_btn)

        layout.addLayout(controls_layout)

        # Main splitter (left: editor, right: preview)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Widget editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        # Widget selector group
        widget_group = QGroupBox("Widget Styles")
        widget_layout = QVBoxLayout(widget_group)

        # Widget list
        self.widget_list = QListWidget()
        self.widget_list.currentTextChanged.connect(self._on_widget_selected)
        widget_layout.addWidget(QLabel("Widgets in theme:"))
        widget_layout.addWidget(self.widget_list, 1)

        # Add widget controls
        add_widget_layout = QHBoxLayout()
        add_widget_layout.addWidget(QLabel("Add widget:"))
        self.widget_selector_combo = QComboBox()
        self.widget_selector_combo.setEditable(True)
        self.widget_selector_combo.addItems(QT_WIDGET_SELECTORS)
        add_widget_layout.addWidget(self.widget_selector_combo, 1)

        self.add_widget_btn = QPushButton("Add")
        self.add_widget_btn.clicked.connect(self._add_widget)
        add_widget_layout.addWidget(self.add_widget_btn)

        widget_layout.addLayout(add_widget_layout)

        # Remove widget button
        self.remove_widget_btn = QPushButton("Remove Selected Widget")
        self.remove_widget_btn.clicked.connect(self._remove_widget)
        widget_layout.addWidget(self.remove_widget_btn)

        editor_layout.addWidget(widget_group, 1)

        # Style editor group
        style_group = QGroupBox("Widget Style Editor")
        style_layout = QVBoxLayout(style_group)

        # Current widget label
        self.current_widget_label = QLabel("Select a widget to edit")
        self.current_widget_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        style_layout.addWidget(self.current_widget_label)

        # Widget preview (show the actual widget being edited)
        preview_label = QLabel("Preview:")
        style_layout.addWidget(preview_label)

        self.widget_preview_container = QWidget()
        self.widget_preview_container.setMinimumHeight(80)
        self.widget_preview_container.setStyleSheet("background-color: #F0F0F0; border: 1px solid #CCC; border-radius: 3px;")
        preview_layout = QVBoxLayout(self.widget_preview_container)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget_preview = QLabel("No widget selected")
        preview_layout.addWidget(self.widget_preview)
        style_layout.addWidget(self.widget_preview_container)

        # Visual style properties
        props_scroll = QScrollArea()
        props_scroll.setWidgetResizable(True)
        props_scroll.setMaximumHeight(250)

        props_widget = QWidget()
        self.props_layout = QVBoxLayout(props_widget)
        self.props_layout.setSpacing(8)
        self.props_layout.addStretch()

        props_scroll.setWidget(props_widget)
        style_layout.addWidget(props_scroll)

        # Raw CSS editor (collapsible)
        self.show_css_btn = QPushButton("▼ Show Raw CSS")
        self.show_css_btn.setCheckable(True)
        self.show_css_btn.clicked.connect(self._toggle_css_editor)
        style_layout.addWidget(self.show_css_btn)

        self.style_edit = QTextEdit()
        self.style_edit.setPlaceholderText("CSS-like style properties (e.g., background-color: #282828; color: #EBDBB2;)")
        self.style_edit.setMaximumHeight(100)
        self.style_edit.textChanged.connect(self._on_raw_style_changed)
        self.style_edit.setVisible(False)
        style_layout.addWidget(self.style_edit)

        # Apply button
        self.apply_style_btn = QPushButton("Apply to Full Preview")
        self.apply_style_btn.clicked.connect(self._apply_preview)
        style_layout.addWidget(self.apply_style_btn)

        editor_layout.addWidget(style_group, 1)

        # Track if we're updating from code (to prevent loops)
        self.updating_from_code = False

        main_splitter.addWidget(editor_widget)

        # Right side: Live preview
        preview_widget = self._create_preview_widget()
        main_splitter.addWidget(preview_widget)

        # Set initial splitter sizes (60% editor, 40% preview)
        main_splitter.setSizes([600, 400])

        layout.addWidget(main_splitter, 1)

    def _create_preview_widget(self) -> QWidget:
        """Create the live preview widget with all Qt widgets"""
        from .preview_widgets import QtWidgetPreviewPanel

        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        # Preview label
        preview_label = QLabel("Live Preview")
        preview_label.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 5px;")
        preview_layout.addWidget(preview_label)

        # Scroll area for preview
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Preview panel
        self.preview_panel = QtWidgetPreviewPanel()
        scroll_area.setWidget(self.preview_panel)

        preview_layout.addWidget(scroll_area, 1)

        return preview_container

    def _load_themes(self):
        """Load themes from file"""
        self.themes = self.theme_manager.load_qt_widget_themes()

        # Update combo box
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItems(sorted(self.themes.keys()))
        self.theme_combo.blockSignals(False)

        # Select first theme if available
        if self.themes:
            self.theme_combo.setCurrentIndex(0)
            self._on_theme_changed(self.theme_combo.currentText())

    def _on_theme_changed(self, theme_name: str):
        """Handle theme selection change"""
        if not theme_name or theme_name not in self.themes:
            return

        self.current_theme_name = theme_name
        self.current_theme = self.themes[theme_name]

        # Update widget list
        self.widget_list.clear()
        self.widget_list.addItems(self.current_theme.get_widget_selectors())

        # Clear style editor
        self.style_edit.blockSignals(True)
        self.style_edit.clear()
        self.style_edit.blockSignals(False)
        self.current_widget_label.setText("Select a widget to edit")

        # Apply to preview
        self._apply_preview()

    def _on_widget_selected(self, widget_selector: str):
        """Handle widget selection in list"""
        if not widget_selector or not self.current_theme:
            return

        style = self.current_theme.get_widget_style(widget_selector)

        self.updating_from_code = True

        # Update raw CSS editor
        self.style_edit.blockSignals(True)
        self.style_edit.setPlainText(style or "")
        self.style_edit.blockSignals(False)

        # Update label
        self.current_widget_label.setText(f"Editing: {widget_selector}")

        # Update widget preview
        self._update_widget_preview(widget_selector, style)

        # Update visual property controls
        self._update_visual_properties(style or "")

        self.updating_from_code = False

    def _on_style_changed(self):
        """Handle style text change"""
        if not self.current_theme or not self.widget_list.currentItem():
            return

        widget_selector = self.widget_list.currentItem().text()
        new_style = self.style_edit.toPlainText()

        # Update theme
        self.current_theme.add_widget_style(widget_selector, new_style)
        self.unsaved_changes = True
        self.themeModified.emit()

    def _add_widget(self):
        """Add a new widget to the current theme"""
        if not self.current_theme:
            QMessageBox.warning(self, "No Theme", "Please select or create a theme first")
            return

        widget_selector = self.widget_selector_combo.currentText().strip()

        if not widget_selector:
            QMessageBox.warning(self, "Invalid Selector", "Please enter a widget selector")
            return

        if widget_selector in self.current_theme.styles:
            QMessageBox.information(self, "Widget Exists", f"Widget '{widget_selector}' already exists in this theme")
            # Select it in the list
            items = self.widget_list.findItems(widget_selector, Qt.MatchFlag.MatchExactly)
            if items:
                self.widget_list.setCurrentItem(items[0])
            return

        # Add widget with default empty style
        self.current_theme.add_widget_style(widget_selector, "")

        # Update widget list
        self.widget_list.clear()
        self.widget_list.addItems(self.current_theme.get_widget_selectors())

        # Select the new widget
        items = self.widget_list.findItems(widget_selector, Qt.MatchFlag.MatchExactly)
        if items:
            self.widget_list.setCurrentItem(items[0])

        self.unsaved_changes = True
        self.themeModified.emit()

    def _remove_widget(self):
        """Remove selected widget from theme"""
        if not self.current_theme or not self.widget_list.currentItem():
            return

        widget_selector = self.widget_list.currentItem().text()

        reply = QMessageBox.question(
            self,
            "Remove Widget",
            f"Remove '{widget_selector}' from theme?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.current_theme.remove_widget_style(widget_selector)

            # Update widget list
            self.widget_list.clear()
            self.widget_list.addItems(self.current_theme.get_widget_selectors())

            # Clear style editor
            self.style_edit.blockSignals(True)
            self.style_edit.clear()
            self.style_edit.blockSignals(False)
            self.current_widget_label.setText("Select a widget to edit")

            self.unsaved_changes = True
            self.themeModified.emit()

    def _new_theme(self):
        """Create a new theme"""
        theme_name, ok = QInputDialog.getText(
            self,
            "New Theme",
            "Enter theme name:"
        )

        if ok and theme_name:
            if theme_name in self.themes:
                QMessageBox.warning(self, "Theme Exists", f"Theme '{theme_name}' already exists")
                return

            # Create new theme with default widgets
            new_theme = QtWidgetTheme(name=theme_name)

            # Add some default widgets
            new_theme.add_widget_style("QWidget", "background-color: #FFFFFF; color: #000000;")
            new_theme.add_widget_style("QPushButton", "background-color: #0078D4; color: #FFFFFF; border-radius: 4px; padding: 6px 12px;")

            self.themes[theme_name] = new_theme

            # Update combo box
            self.theme_combo.blockSignals(True)
            self.theme_combo.clear()
            self.theme_combo.addItems(sorted(self.themes.keys()))
            self.theme_combo.setCurrentText(theme_name)
            self.theme_combo.blockSignals(False)

            self._on_theme_changed(theme_name)

            self.unsaved_changes = True
            self.themeModified.emit()

    def _duplicate_theme(self):
        """Duplicate the current theme"""
        if not self.current_theme:
            QMessageBox.warning(self, "No Theme", "Please select a theme to duplicate")
            return

        new_name, ok = QInputDialog.getText(
            self,
            "Duplicate Theme",
            "Enter new theme name:",
            text=f"{self.current_theme_name} Copy"
        )

        if ok and new_name:
            if new_name in self.themes:
                QMessageBox.warning(self, "Theme Exists", f"Theme '{new_name}' already exists")
                return

            # Create copy
            new_theme = QtWidgetTheme(name=new_name, styles=self.current_theme.styles.copy())
            self.themes[new_name] = new_theme

            # Update combo box
            self.theme_combo.blockSignals(True)
            self.theme_combo.clear()
            self.theme_combo.addItems(sorted(self.themes.keys()))
            self.theme_combo.setCurrentText(new_name)
            self.theme_combo.blockSignals(False)

            self._on_theme_changed(new_name)

            self.unsaved_changes = True
            self.themeModified.emit()

    def _delete_theme(self):
        """Delete the current theme"""
        if not self.current_theme:
            return

        reply = QMessageBox.question(
            self,
            "Delete Theme",
            f"Delete theme '{self.current_theme_name}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.themes[self.current_theme_name]

            # Update combo box
            self.theme_combo.blockSignals(True)
            self.theme_combo.clear()
            if self.themes:
                self.theme_combo.addItems(sorted(self.themes.keys()))
                self.theme_combo.setCurrentIndex(0)
            self.theme_combo.blockSignals(False)

            if self.themes:
                self._on_theme_changed(self.theme_combo.currentText())
            else:
                self.current_theme = None
                self.current_theme_name = None

            self.unsaved_changes = True
            self.themeModified.emit()

    def _save_themes(self):
        """Save all themes to file"""
        try:
            self.theme_manager.save_qt_widget_themes(self.themes)
            self.unsaved_changes = False
            QMessageBox.information(self, "Success", "Qt widget themes saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save themes:\n{e}")

    def _load_from_file(self):
        """Load Qt Widget themes from external JSON file"""
        from PyQt6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Qt Widget Themes",
            str(self.theme_manager.qt_widget_themes_dir),
            "JSON Files (*.json);;All Files (*)"
        )

        if not filename:
            return

        try:
            # Just load the themes - no merge/replace nonsense
            loaded_themes = self.theme_manager.load_qt_widget_themes(filename)

            if not loaded_themes:
                QMessageBox.warning(self, "No Themes", f"No valid Qt Widget themes found in:\n{filename}")
                return

            # Simply replace with loaded themes
            self.themes = loaded_themes

            # Update UI
            self.theme_combo.blockSignals(True)
            self.theme_combo.clear()
            self.theme_combo.addItems(sorted(self.themes.keys()))
            self.theme_combo.blockSignals(False)

            if self.themes:
                self.theme_combo.setCurrentIndex(0)
                self._on_theme_changed(self.theme_combo.currentText())

            self.unsaved_changes = True
            self.themeModified.emit()

            self.status_bar_message = f"Loaded {len(loaded_themes)} theme(s) from {Path(filename).name}"

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load themes:\n{e}")

    def _open_theme(self):
        """Open theme file (wrapper for main.py compatibility)"""
        self._load_from_file()

    def _apply_preview(self):
        """Apply current theme to preview panel"""
        if not self.current_theme:
            return

        stylesheet = self.current_theme.generate_stylesheet()
        self.preview_panel.setStyleSheet(stylesheet)

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.unsaved_changes

    def _toggle_css_editor(self):
        """Toggle raw CSS editor visibility"""
        if self.show_css_btn.isChecked():
            self.style_edit.setVisible(True)
            self.show_css_btn.setText("▲ Hide Raw CSS")
        else:
            self.style_edit.setVisible(False)
            self.show_css_btn.setText("▼ Show Raw CSS")

    def _on_raw_style_changed(self):
        """Handle raw CSS text changes"""
        if self.updating_from_code:
            return

        if not self.current_theme or not self.widget_list.currentItem():
            return

        widget_selector = self.widget_list.currentItem().text()
        new_style = self.style_edit.toPlainText()

        # Update theme
        self.current_theme.add_widget_style(widget_selector, new_style)

        # Update visual properties
        self.updating_from_code = True
        self._update_visual_properties(new_style)
        self._update_widget_preview(widget_selector, new_style)
        self.updating_from_code = False

        self.unsaved_changes = True
        self.themeModified.emit()

    def _update_widget_preview(self, widget_selector: str, style: str):
        """Update the widget preview to show what it looks like"""
        # Clear old preview
        layout = self.widget_preview_container.layout()
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create appropriate widget based on selector
        preview_widget = self._create_preview_widget(widget_selector)

        if preview_widget:
            # Apply the style to the preview widget
            preview_widget.setStyleSheet(f"{widget_selector} {{ {style} }}")
            layout.addWidget(preview_widget)
        else:
            # Fallback: show text
            label = QLabel(f"Preview for {widget_selector}")
            layout.addWidget(label)

    def _create_preview_widget(self, selector: str):
        """Create an actual Qt widget based on the selector"""
        # Extract base widget name (without pseudo-states)
        base_selector = selector.split(':')[0].split('::')[0].strip()

        if base_selector == "QPushButton":
            btn = QPushButton("Sample Button")
            return btn
        elif base_selector == "QLineEdit":
            edit = QLineEdit()
            edit.setPlaceholderText("Sample text...")
            return edit
        elif base_selector == "QLabel":
            return QLabel("Sample Label")
        elif base_selector == "QComboBox":
            combo = QComboBox()
            combo.addItems(["Option 1", "Option 2", "Option 3"])
            return combo
        elif base_selector == "QCheckBox":
            return QCheckBox("Sample Checkbox")
        elif base_selector == "QRadioButton":
            return QRadioButton("Sample Radio")
        elif base_selector == "QProgressBar":
            progress = QProgressBar()
            progress.setValue(65)
            return progress
        elif base_selector == "QSlider":
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setValue(50)
            return slider
        elif base_selector == "QSpinBox":
            return QSpinBox()
        elif base_selector == "QTextEdit":
            edit = QTextEdit()
            edit.setPlaceholderText("Sample text...")
            edit.setMaximumHeight(60)
            return edit
        elif base_selector == "QListWidget":
            list_widget = QListWidget()
            list_widget.addItems(["Item 1", "Item 2", "Item 3"])
            list_widget.setMaximumHeight(80)
            return list_widget
        elif base_selector == "QGroupBox":
            group = QGroupBox("Sample Group")
            layout = QVBoxLayout(group)
            layout.addWidget(QLabel("Content"))
            return group

        # Default: just show a widget
        return QWidget()

    def _update_visual_properties(self, style: str):
        """Parse CSS and create visual property controls"""
        # Clear existing properties
        while self.props_layout.count() > 1:  # Keep the stretch
            item = self.props_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not style:
            return

        # Parse CSS properties
        properties = self._parse_css_properties(style)

        # Create controls for each property
        from .color_picker import ColorPickerButton

        for prop_name, prop_value in properties.items():
            prop_layout = QHBoxLayout()

            # Property label
            label = QLabel(f"{prop_name}:")
            label.setMinimumWidth(120)
            prop_layout.addWidget(label)

            # Check if it's a color property
            if any(color_word in prop_name.lower() for color_word in ['color', 'background', 'border']) and prop_value.startswith('#'):
                # Color picker
                color_picker = ColorPickerButton(prop_value)
                color_picker.colorChanged.connect(lambda c, p=prop_name: self._on_color_changed(p, c))
                prop_layout.addWidget(color_picker)

                # Show hex value
                hex_label = QLabel(prop_value)
                prop_layout.addWidget(hex_label)

            elif prop_name in ['padding', 'margin', 'border-width'] and prop_value.replace('px', '').strip().isdigit():
                # Spinbox for dimensions
                spinbox = QSpinBox()
                spinbox.setRange(0, 100)
                spinbox.setValue(int(prop_value.replace('px', '').strip()))
                spinbox.setSuffix(" px")
                spinbox.valueChanged.connect(lambda v, p=prop_name: self._on_dimension_changed(p, v))
                prop_layout.addWidget(spinbox)

            elif prop_name == 'border-radius' and 'px' in prop_value:
                # Spinbox for border radius
                spinbox = QSpinBox()
                spinbox.setRange(0, 50)
                spinbox.setValue(int(prop_value.replace('px', '').strip()))
                spinbox.setSuffix(" px")
                spinbox.valueChanged.connect(lambda v, p=prop_name: self._on_dimension_changed(p, v))
                prop_layout.addWidget(spinbox)

            else:
                # Text field for other properties
                text_edit = QLineEdit(prop_value)
                text_edit.textChanged.connect(lambda t, p=prop_name: self._on_text_property_changed(p, t))
                prop_layout.addWidget(text_edit)

            prop_layout.addStretch()
            self.props_layout.insertLayout(self.props_layout.count() - 1, prop_layout)

    def _parse_css_properties(self, style: str) -> dict:
        """Parse CSS style string into property dict"""
        properties = {}
        if not style:
            return properties

        # Split by semicolon
        parts = [p.strip() for p in style.split(';') if p.strip()]

        for part in parts:
            if ':' in part:
                prop, value = part.split(':', 1)
                properties[prop.strip()] = value.strip()

        return properties

    def _on_color_changed(self, prop_name: str, color: str):
        """Handle color picker change"""
        if self.updating_from_code:
            return

        self._update_css_property(prop_name, color)

    def _on_dimension_changed(self, prop_name: str, value: int):
        """Handle dimension spinbox change"""
        if self.updating_from_code:
            return

        self._update_css_property(prop_name, f"{value}px")

    def _on_text_property_changed(self, prop_name: str, value: str):
        """Handle text property change"""
        if self.updating_from_code:
            return

        self._update_css_property(prop_name, value)

    def _update_css_property(self, prop_name: str, prop_value: str):
        """Update a single CSS property in the current style"""
        if not self.current_theme or not self.widget_list.currentItem():
            return

        widget_selector = self.widget_list.currentItem().text()
        current_style = self.current_theme.get_widget_style(widget_selector) or ""

        # Parse current properties
        properties = self._parse_css_properties(current_style)

        # Update property
        properties[prop_name] = prop_value

        # Rebuild CSS string
        new_style = "; ".join([f"{k}: {v}" for k, v in properties.items()])

        # Update theme
        self.current_theme.add_widget_style(widget_selector, new_style)

        # Update raw CSS editor
        self.updating_from_code = True
        self.style_edit.setPlainText(new_style)
        self._update_widget_preview(widget_selector, new_style)
        self.updating_from_code = False

        self.unsaved_changes = True
        self.themeModified.emit()
