"""
Qt Widget Theme Editor
Editor for Qt Widget themes with comprehensive widget selector and live preview
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QListWidget, QTextEdit, QSplitter, QGroupBox, QLineEdit, QMessageBox,
    QInputDialog, QScrollArea
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
        style_group = QGroupBox("Widget Style")
        style_layout = QVBoxLayout(style_group)

        # Current widget label
        self.current_widget_label = QLabel("Select a widget to edit")
        style_layout.addWidget(self.current_widget_label)

        # Style text editor
        self.style_edit = QTextEdit()
        self.style_edit.setPlaceholderText("CSS-like style properties (e.g., background-color: #282828; color: #EBDBB2;)")
        self.style_edit.textChanged.connect(self._on_style_changed)
        style_layout.addWidget(self.style_edit, 1)

        # Apply button
        self.apply_style_btn = QPushButton("Apply Style to Preview")
        self.apply_style_btn.clicked.connect(self._apply_preview)
        style_layout.addWidget(self.apply_style_btn)

        editor_layout.addWidget(style_group, 1)

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

        self.style_edit.blockSignals(True)
        self.style_edit.setPlainText(style or "")
        self.style_edit.blockSignals(False)

        self.current_widget_label.setText(f"Editing: {widget_selector}")

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

    def _apply_preview(self):
        """Apply current theme to preview panel"""
        if not self.current_theme:
            return

        stylesheet = self.current_theme.generate_stylesheet()
        self.preview_panel.setStyleSheet(stylesheet)

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.unsaved_changes
