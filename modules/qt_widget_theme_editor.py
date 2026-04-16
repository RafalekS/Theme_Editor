"""
Qt Widget Theme Editor
Editor for Qt Widget themes with comprehensive widget selector and live preview
"""

import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QListWidget, QTextEdit, QSplitter, QGroupBox, QLineEdit, QMessageBox,
    QInputDialog, QScrollArea, QSpinBox, QRadioButton, QCheckBox,
    QProgressBar, QSlider, QDateEdit, QTimeEdit, QDateTimeEdit, QDoubleSpinBox,
    QTabWidget, QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from typing import Dict, Optional
from .theme_data import QtWidgetTheme
from .theme_manager import ThemeManager
from .widget_indexer import load_visible_ui_index, location_display_name

# ── UI colour constants (dark theme defaults) ─────────────────────────────────
_C_ACCENT       = "#0078D4"
_C_ACCENT2      = "#1E90FF"
_C_BG_DARK      = "#2B2B2B"
_C_BG_MEDIUM    = "#3C3C3C"
_C_BG_LIGHT     = "#555555"
_C_FG_PRIMARY   = "#FFFFFF"
_C_FG_DIM       = "#AAAAAA"
_C_FG_SECONDARY = "#CCCCCC"

# ── Widget type buttons for the selector panel ────────────────────────────────
# (display_name, icon, qt_class_for_index_lookup, primary_css_selector)
WIDGET_BUTTONS: list[tuple[str, str, str, str]] = [
    ("Button",      "⬜",  "QPushButton",  "QPushButton"),
    ("ToolButton",  "🔧",  "QToolButton",  "QToolButton"),
    ("CheckBox",    "☑",   "QCheckBox",    "QCheckBox"),
    ("RadioButton", "○",   "QRadioButton", "QRadioButton"),
    ("Label",       "🔤",  "QLabel",       "QLabel"),
    ("Input",       "📝",  "QLineEdit",    "QLineEdit"),
    ("TextEdit",    "📄",  "QTextEdit",    "QTextEdit"),
    ("ComboBox",    "▼",   "QComboBox",    "QComboBox"),
    ("SpinBox",     "123", "QSpinBox",     "QSpinBox"),
    ("List",        "≡",   "QListWidget",  "QListWidget"),
    ("Tree",        "🌲",  "QTreeWidget",  "QTreeWidget"),
    ("Table",       "⊞",   "QTableWidget", "QTableWidget"),
    ("GroupBox",    "▣",   "QGroupBox",    "QGroupBox"),
    ("TabBar",      "🗂",  "QTabWidget",   "QTabBar::tab"),
    ("ScrollBar",   "│",   "QScrollBar",   "QScrollBar:vertical"),
    ("Splitter",    "┃",   "QSplitter",    "QSplitter::handle"),
    ("ProgressBar", "░",   "QProgressBar", "QProgressBar"),
    ("Slider",      "▬",   "QSlider",      "QSlider::groove:horizontal"),
    ("MenuBar",     "☰",   "QMenuBar",     "QMenuBar"),
    ("Menu",        "📋",  "QMenu",        "QMenu"),
    ("StatusBar",   "⎘",   "QStatusBar",   "QStatusBar"),
    ("Dialog",      "🪟",  "QDialog",      "QDialog"),
    ("ToolTip",     "💬",  "QToolTip",     "QToolTip"),
]


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


# ── WidgetSelectorPanel ───────────────────────────────────────────────────────

class WidgetSelectorPanel(QScrollArea):
    """Left panel — button-based widget type selector.
    Shows only widget types that appear in Theme_Editor's own source.
    A 'Show usage panel' checkbox toggles the 3rd pane."""

    widget_selected      = pyqtSignal(str)   # qt_class, e.g. "QPushButton"
    usage_panel_toggled  = pyqtSignal(bool)  # True = show usage panel

    _BTN_H = 36

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumWidth(185)
        self.setMaximumWidth(215)

        self._buttons: dict[str, QPushButton] = {}   # qt_class → button
        self._selected_class: str | None = None

        # Load visible-UI index
        try:
            self._vis_idx = load_visible_ui_index()
        except Exception:
            self._vis_idx = {}

        content = QWidget()
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(6, 6, 6, 8)
        vbox.setSpacing(3)

        # "Show usage panel" checkbox
        self._usage_chk = QCheckBox("Show usage panel")
        self._usage_chk.setStyleSheet(
            f"QCheckBox {{ color: {_C_FG_SECONDARY}; font-size: 9px; }}"
        )
        self._usage_chk.setToolTip(
            "Opens a panel showing which modules use the selected widget.\n"
            "Click any entry to navigate there."
        )
        self._usage_chk.stateChanged.connect(
            lambda s: self.usage_panel_toggled.emit(s == 2)
        )
        vbox.addWidget(self._usage_chk)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {_C_BG_LIGHT};")
        sep.setFixedHeight(1)
        vbox.addWidget(sep)

        title = QLabel("Select widget:")
        title.setStyleSheet(
            f"color: {_C_FG_DIM}; font-style: italic; padding: 2px 0;"
        )
        vbox.addWidget(title)

        # One button per widget type — skip those with 0 visible locations
        for display_name, icon, qt_class, _selector in WIDGET_BUTTONS:
            locations = self._vis_idx.get(qt_class, [])
            if not locations:
                continue

            btn = QPushButton(f"{icon} {display_name}")
            btn.setCheckable(True)
            btn.setFixedHeight(self._BTN_H)
            btn.setStyleSheet(self._btn_style(False))
            btn.setToolTip(f"Used in {len(locations)} location(s)")
            btn.clicked.connect(lambda _c, qc=qt_class: self._select(qc))
            self._buttons[qt_class] = btn
            vbox.addWidget(btn)

        vbox.addStretch()
        self.setWidget(content)

    @staticmethod
    def _btn_style(active: bool) -> str:
        if active:
            return (
                f"QPushButton {{ background-color: {_C_ACCENT}; color: {_C_BG_DARK}; "
                f"border: none; border-radius: 4px; padding: 0 10px; "
                f"font-weight: bold; text-align: left; }}"
            )
        return (
            f"QPushButton {{ background-color: {_C_BG_MEDIUM}; color: {_C_FG_PRIMARY}; "
            f"border: 1px solid {_C_BG_LIGHT}; border-radius: 4px; padding: 0 10px; "
            f"text-align: left; }}"
            f"QPushButton:hover {{ background-color: {_C_BG_LIGHT}; }}"
        )

    def _select(self, qt_class: str):
        for qc, btn in self._buttons.items():
            active = (qc == qt_class)
            btn.setChecked(active)
            btn.setStyleSheet(self._btn_style(active))
        self._selected_class = qt_class
        self.widget_selected.emit(qt_class)

    def set_active(self, qt_class: str | None):
        """Highlight a button without emitting signals."""
        for qc, btn in self._buttons.items():
            active = (qc == qt_class)
            btn.setChecked(active)
            btn.setStyleSheet(self._btn_style(active))
        self._selected_class = qt_class


# ── UsagePanel ────────────────────────────────────────────────────────────────

class UsagePanel(QWidget):
    """Right pane — shows which Theme_Editor modules use the selected widget.
    Each location is a clickable button; clicking emits navigate_to(class_name)
    so the main window can switch to that module's tab."""

    navigate_to = pyqtSignal(str)   # emits the class name to navigate to

    _COLS_THRESHOLD_2 = 7
    _COLS_THRESHOLD_3 = 18

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(240)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(6)

        self._title_lbl = QLabel("Select a widget to see where it is used")
        self._title_lbl.setWordWrap(True)
        self._title_lbl.setStyleSheet(
            f"font-weight: bold; color: {_C_ACCENT}; padding-bottom: 4px;"
        )
        outer.addWidget(self._title_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {_C_BG_LIGHT};")
        sep.setFixedHeight(1)
        outer.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        outer.addWidget(scroll, 1)

        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(4)
        scroll.setWidget(self._grid_widget)

        self._hint_lbl = QLabel("Click any location to navigate there")
        self._hint_lbl.setStyleSheet(
            f"color: {_C_FG_DIM}; font-style: italic; font-size: 9px;"
        )
        outer.addWidget(self._hint_lbl)

        self._loc_btns: list[QPushButton] = []

    def update_locations(self, widget_display_name: str, locations: list[str]):
        """Rebuild the grid with new locations, grouped by type then name."""
        # Clear all existing widgets from grid
        for w in self._loc_btns:
            w.deleteLater()
        self._loc_btns.clear()
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        n = len(locations)
        if n == 0:
            self._title_lbl.setText(f"{widget_display_name} — not found in any module")
            self._hint_lbl.hide()
            return

        self._title_lbl.setText(
            f"{widget_display_name}  —  {n} location{'s' if n != 1 else ''}"
        )
        self._hint_lbl.show()

        # Group by type
        groups = {
            "editor": ("🖊  Editors",  []),
            "ui":     ("🧩  Panels",   []),
            "dialog": ("🪟  Dialogs",  []),
            "window": ("🖥  Windows",  []),
            "other":  ("▸  Other",    []),
        }
        for cls_name in locations:
            _, badge = location_display_name(cls_name)
            groups.get(badge, groups["other"])[1].append(cls_name)

        cols = 1
        if n > self._COLS_THRESHOLD_3:
            cols = 3
        elif n > self._COLS_THRESHOLD_2:
            cols = 2

        grid_row = 0
        for badge_key, (section_title, cls_list) in groups.items():
            if not cls_list:
                continue

            hdr = QLabel(section_title)
            hdr.setStyleSheet(
                f"color: {_C_ACCENT2}; font-weight: bold; font-size: 9px; "
                f"letter-spacing: 1px; padding: 6px 0 2px 0; background: transparent;"
            )
            self._grid.addWidget(hdr, grid_row, 0, 1, cols)
            grid_row += 1

            badge_icons = {"editor": "🖊", "ui": "🧩", "dialog": "🪟", "window": "🖥"}
            icon = badge_icons.get(badge_key, "▸")

            for col_idx, cls_name in enumerate(sorted(cls_list)):
                human, badge = location_display_name(cls_name)
                lbl = f"{icon} {human}"

                btn = QPushButton(lbl)
                btn.setToolTip(f"{cls_name}\n({badge})" if badge else cls_name)
                btn.setStyleSheet(self._loc_btn_style())
                btn.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Expanding,
                )
                btn.clicked.connect(lambda _c, cn=cls_name: self.navigate_to.emit(cn))

                row = grid_row + col_idx // cols
                col = col_idx % cols
                self._grid.addWidget(btn, row, col)
                self._loc_btns.append(btn)

            row_count = (len(cls_list) + cols - 1) // cols
            grid_row += row_count

        # Allow buttons to grow vertically when there is room
        if n < 45:
            for r in range(grid_row):
                self._grid.setRowStretch(r, 1)

    @staticmethod
    def _loc_btn_style() -> str:
        return (
            f"QPushButton {{ background-color: {_C_BG_MEDIUM}; color: {_C_FG_PRIMARY}; "
            f"border: 1px solid {_C_BG_LIGHT}; border-radius: 4px; "
            f"padding: 5px 8px; text-align: left; font-size: 9px; }}"
            f"QPushButton:hover {{ background-color: {_C_ACCENT}; "
            f"color: {_C_BG_DARK}; border-color: {_C_ACCENT}; }}"
        )


# ── QtWidgetThemeEditor ───────────────────────────────────────────────────────

class QtWidgetThemeEditor(QWidget):
    """Qt Widget Theme Editor with live preview"""

    themeModified = pyqtSignal()   # Emitted when theme is modified
    navigate_to   = pyqtSignal(str)  # class name to navigate to (forwarded from UsagePanel)

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.themes: Dict[str, QtWidgetTheme] = {}
        self.current_theme_name: Optional[str] = None
        self.current_theme: Optional[QtWidgetTheme] = None
        self.current_file_path: Optional[str] = None  # Track which file is currently loaded
        self.unsaved_changes = False

        self._setup_ui()
        # DON'T load default file on startup - user must choose a file first!

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # File status bar - show which file is currently loaded
        file_status_layout = QHBoxLayout()
        self.file_status_label = QLabel("No file loaded - click 'Load from File...' or 'New File' to start")
        self.file_status_label.setStyleSheet("color: #FF9800; font-weight: bold; padding: 5px; background-color: #3C3C3C; border-radius: 3px;")
        file_status_layout.addWidget(self.file_status_label)
        layout.addLayout(file_status_layout)

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

        self.new_file_btn = QPushButton("New File")
        self.new_file_btn.clicked.connect(self._new_file)
        controls_layout.addWidget(self.new_file_btn)

        self.load_file_btn = QPushButton("Load from File...")
        self.load_file_btn.clicked.connect(self._load_from_file)
        controls_layout.addWidget(self.load_file_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_themes)
        controls_layout.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("Save As...")
        self.save_as_btn.clicked.connect(self._save_as)
        controls_layout.addWidget(self.save_as_btn)

        layout.addLayout(controls_layout)

        # Main splitter: selector | editor | preview | usage
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._main_splitter = main_splitter

        # Pane 0: widget type selector buttons
        self._selector_panel = WidgetSelectorPanel()
        main_splitter.addWidget(self._selector_panel)

        # Pane 1: Widget editor (existing)
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        # Hidden widget list — kept for internal state tracking by existing methods
        self.widget_list = QListWidget()
        self.widget_list.currentTextChanged.connect(self._on_widget_selected)
        self.widget_list.hide()

        # Hidden add-widget combo — still used by _add_widget / _remove_widget
        self.widget_selector_combo = QComboBox()
        self.widget_selector_combo.setEditable(True)
        self.widget_selector_combo.addItems(sorted(QT_WIDGET_SELECTORS))
        self.widget_selector_combo.hide()

        self.remove_widget_btn = QPushButton("Remove Selected Widget")
        self.remove_widget_btn.clicked.connect(self._remove_widget)
        self.remove_widget_btn.hide()

        self.add_widget_btn = QPushButton("Add")
        self.add_widget_btn.clicked.connect(self._add_widget)
        self.add_widget_btn.hide()

        # Style editor group — takes the full middle pane
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
        self.widget_preview_container.setStyleSheet("background-color: #2B2B2B; border: 1px solid #555; border-radius: 3px;")
        preview_layout = QVBoxLayout(self.widget_preview_container)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget_preview = QLabel("No widget selected")
        preview_layout.addWidget(self.widget_preview)
        style_layout.addWidget(self.widget_preview_container)

        # Visual style properties (scrollable with better layout)
        props_scroll = QScrollArea()
        props_scroll.setWidgetResizable(True)
        props_scroll.setMinimumHeight(150)
        props_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        props_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        props_widget = QWidget()
        props_widget.setObjectName("props_content")
        self.props_layout = QVBoxLayout(props_widget)
        self.props_layout.setContentsMargins(5, 5, 5, 5)
        self.props_layout.setSpacing(0)
        self.props_layout.addStretch()

        props_scroll.setWidget(props_widget)

        # Style the scroll area for dark theme
        props_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
            }
            QWidget#props_content {
                background-color: #2B2B2B;
            }
            QScrollBar:vertical {
                border: none;
                background: #1E1E1E;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        style_layout.addWidget(props_scroll, 1)

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

        # Set minimum width for editor side
        editor_widget.setMinimumWidth(380)
        main_splitter.addWidget(editor_widget)

        # Pane 2: Live preview (existing)
        preview_widget = self._create_full_preview_panel()
        preview_widget.setMinimumWidth(300)
        main_splitter.addWidget(preview_widget)

        # Pane 3: Usage panel (hidden initially)
        self._usage_panel = UsagePanel()
        self._usage_panel.hide()
        main_splitter.addWidget(self._usage_panel)

        # Prevent any pane from collapsing to zero
        for i in range(4):
            main_splitter.setCollapsible(i, False)
        main_splitter.setHandleWidth(6)

        # Initial sizes: selector=200, editor=450, preview=350, usage hidden
        main_splitter.setSizes([200, 450, 350, 280])

        # Wire selector panel → editor list + usage panel
        self._selector_panel.widget_selected.connect(self._on_selector_widget_selected)
        self._selector_panel.usage_panel_toggled.connect(self._toggle_usage_panel)

        # Wire usage panel navigation → forward as our own signal
        self._usage_panel.navigate_to.connect(self.navigate_to)

        layout.addWidget(main_splitter, 1)

    def _create_full_preview_panel(self) -> QWidget:
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
        # Connect widget click signal to select widget in editor
        self.preview_panel.widget_clicked.connect(self._on_preview_widget_clicked)
        scroll_area.setWidget(self.preview_panel)

        preview_layout.addWidget(scroll_area, 1)

        return preview_container

    def _on_theme_changed(self, theme_name: str):
        """Handle theme selection change"""
        if not theme_name or theme_name not in self.themes:
            return

        self.current_theme_name = theme_name
        self.current_theme = self.themes[theme_name]

        # Update widget list
        self.widget_list.clear()
        self.widget_list.addItems(self.current_theme.get_widget_selectors())

        # Update add widget dropdown to exclude already-added widgets
        self._update_available_widgets()

        # Clear style editor
        self.style_edit.blockSignals(True)
        self.style_edit.clear()
        self.style_edit.blockSignals(False)
        self.current_widget_label.setText("Select a widget to edit")

        # Apply to preview
        self._apply_preview()

    def _update_available_widgets(self):
        """Update the add widget dropdown to show only widgets not yet in theme"""
        if not self.current_theme:
            return

        # Get current widgets in theme
        existing_widgets = set(self.current_theme.get_widget_selectors())

        # Filter out existing widgets from the full list
        available = [w for w in QT_WIDGET_SELECTORS if w not in existing_widgets]

        # Update combo box
        self.widget_selector_combo.clear()
        self.widget_selector_combo.addItems(sorted(available))

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

        # Sync selector panel highlight and usage panel
        base_class = widget_selector.split(':')[0].split(' ')[0]
        self._selector_panel.set_active(base_class)
        self._update_usage_panel(base_class)

    def _on_preview_widget_clicked(self, widget_selector: str):
        """Handle widget click from preview panel"""
        if not self.current_theme:
            return

        # Check if widget exists in theme, if not add it
        if widget_selector not in self.current_theme.get_widget_selectors():
            # Add the widget with empty style
            self.current_theme.add_widget_style(widget_selector, "")
            self.widget_list.addItem(widget_selector)
            self._update_available_widgets()

        # Find and select the widget in the list
        items = self.widget_list.findItems(widget_selector, Qt.MatchFlag.MatchExactly)
        if items:
            self.widget_list.setCurrentItem(items[0])
            # Scroll to make it visible
            self.widget_list.scrollToItem(items[0])

        # Highlight the corresponding selector button
        base_class = widget_selector.split(':')[0].split(' ')[0]
        self._selector_panel.set_active(base_class)
        self._update_usage_panel(base_class)

    # ── Widget selector panel wiring ──────────────────────────────────────────

    def _on_selector_widget_selected(self, qt_class: str):
        """Handle widget type button click — loads that widget's CSS into the editor."""
        # Determine which CSS selector to edit
        primary_selector = qt_class  # default fallback
        for _name, _icon, qc, sel in WIDGET_BUTTONS:
            if qc == qt_class:
                primary_selector = sel
                break

        if self.current_theme:
            selectors = self.current_theme.get_widget_selectors()
            # Find an existing selector for this widget type
            target = None
            if primary_selector in selectors:
                target = primary_selector
            else:
                # Broaden: any selector whose base class matches
                for s in selectors:
                    base = s.split(':')[0].split(' ')[0]
                    if base == qt_class:
                        target = s
                        break

            if target is None:
                # Not in theme yet — add it with a default style
                default = self._get_default_style(primary_selector)
                self.current_theme.add_widget_style(primary_selector, default)
                self.widget_list.addItem(primary_selector)
                self._update_available_widgets()
                target = primary_selector

            # Select in the hidden widget_list so existing methods work
            items = self.widget_list.findItems(target, Qt.MatchFlag.MatchExactly)
            if items:
                self.widget_list.setCurrentItem(items[0])
            else:
                # Manually trigger the editor update
                self._load_selector_into_editor(target)
        else:
            # No theme loaded — just update the header
            self.current_widget_label.setText(f"Load a theme file first")

        self._update_usage_panel(qt_class)

    def _load_selector_into_editor(self, widget_selector: str):
        """Directly populate the style editor for the given selector."""
        if not self.current_theme:
            return
        style = self.current_theme.get_widget_style(widget_selector) or ""
        self.updating_from_code = True
        self.style_edit.blockSignals(True)
        self.style_edit.setPlainText(style)
        self.style_edit.blockSignals(False)
        self.current_widget_label.setText(f"Editing: {widget_selector}")
        self._update_widget_preview(widget_selector, style)
        self._update_visual_properties(style)
        self.updating_from_code = False

    def _toggle_usage_panel(self, visible: bool):
        """Show or hide the usage panel pane."""
        self._usage_panel.setVisible(visible)
        if visible and self._selector_panel._selected_class:
            self._update_usage_panel(self._selector_panel._selected_class)

    def _update_usage_panel(self, qt_class: str):
        """Populate UsagePanel for the given Qt class."""
        if not self._usage_panel.isVisible():
            return
        vis_idx = self._selector_panel._vis_idx
        locations = vis_idx.get(qt_class, [])
        self._usage_panel.update_locations(qt_class, locations)

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

    def _get_default_style(self, widget_selector: str) -> str:
        """Get default style template for a widget type"""
        # Extract base widget name
        base = widget_selector.split(':')[0].split('::')[0].strip()

        # Default style templates for common widgets
        defaults = {
            "QPushButton": "background-color: #0078D4; color: #FFFFFF; border: 1px solid #555; border-radius: 4px; padding: 6px 12px;",
            "QLineEdit": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555; border-radius: 3px; padding: 4px;",
            "QTextEdit": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555;",
            "QComboBox": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555; border-radius: 3px; padding: 4px;",
            "QCheckBox": "color: #FFFFFF; spacing: 5px;",
            "QCheckBox::indicator": "width: 18px; height: 18px; border: 2px solid #555; border-radius: 3px; background-color: #3C3C3C;",
            "QCheckBox::indicator:checked": "background-color: #0078D4; border-color: #0078D4;",
            "QRadioButton": "color: #FFFFFF; spacing: 5px;",
            "QRadioButton::indicator": "width: 18px; height: 18px; border: 2px solid #555; border-radius: 9px; background-color: #3C3C3C;",
            "QRadioButton::indicator:checked": "background-color: #0078D4; border-color: #0078D4;",
            "QLabel": "color: #FFFFFF; background-color: transparent;",
            "QGroupBox": "color: #FFFFFF; border: 1px solid #555; border-radius: 4px; margin-top: 10px; padding-top: 10px;",
            "QProgressBar": "border: 1px solid #555; border-radius: 3px; background-color: #3C3C3C; text-align: center;",
            "QProgressBar::chunk": "background-color: #0078D4; border-radius: 2px;",
            "QSlider::groove:horizontal": "border: 1px solid #555; height: 6px; background: #3C3C3C; border-radius: 3px;",
            "QSlider::handle:horizontal": "background: #0078D4; border: 1px solid #555; width: 16px; margin: -5px 0; border-radius: 8px;",
            "QSpinBox": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555; border-radius: 3px; padding: 4px;",
            "QDateEdit": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555; border-radius: 3px; padding: 4px;",
            "QTimeEdit": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555; border-radius: 3px; padding: 4px;",
            "QListWidget": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555;",
            "QListWidget::item": "padding: 4px;",
            "QListWidget::item:selected": "background-color: #0078D4; color: #FFFFFF;",
            "QTableWidget": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555; gridline-color: #555;",
            "QTreeWidget": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555;",
            "QScrollBar:vertical": "background: #2B2B2B; width: 12px; border: none;",
            "QScrollBar::handle:vertical": "background: #555555; border-radius: 6px; min-height: 20px;",
            "QTabWidget::pane": "border: 1px solid #555; background-color: #2B2B2B;",
            "QTabBar::tab": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555; padding: 6px 12px;",
            "QTabBar::tab:selected": "background-color: #0078D4; color: #FFFFFF;",
            "QMenuBar": "background-color: #2B2B2B; color: #FFFFFF;",
            "QMenuBar::item": "padding: 4px 8px;",
            "QMenuBar::item:selected": "background-color: #0078D4;",
            "QMenu": "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555;",
            "QMenu::item": "padding: 4px 20px;",
            "QMenu::item:selected": "background-color: #0078D4;",
        }

        # Return default for this widget, or a generic default
        return defaults.get(widget_selector, defaults.get(base, "background-color: #3C3C3C; color: #FFFFFF; border: 1px solid #555;"))

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

        # Add widget with default style based on widget type
        default_style = self._get_default_style(widget_selector)
        self.current_theme.add_widget_style(widget_selector, default_style)

        # Update widget list
        self.widget_list.clear()
        self.widget_list.addItems(self.current_theme.get_widget_selectors())

        # Update available widgets dropdown
        self._update_available_widgets()

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

            # Update available widgets dropdown
            self._update_available_widgets()

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

    def _new_file(self):
        """Start a new file with empty themes"""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to continue?\nUnsaved changes will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Clear everything
        self.themes = {}
        self.current_theme_name = None
        self.current_theme = None
        self.current_file_path = None
        self.unsaved_changes = False

        # Clear UI
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.blockSignals(False)

        self.widget_list.clear()
        self.style_edit.clear()
        self.current_widget_label.setText("Select a widget to edit")

        # Update file status
        self.file_status_label.setText("New file (not saved yet) - use 'Save' to choose location")
        self.file_status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px; background-color: #3C3C3C; border-radius: 3px;")

        QMessageBox.information(
            self,
            "New File",
            "Started new file. Create themes and then use 'Save' to choose where to save."
        )

    def _save_themes(self):
        """Save all themes to file"""
        try:
            # Block signals to prevent any focus changes from triggering unsaved changes
            self.style_edit.blockSignals(True)

            # CRITICAL: Save to the currently loaded file, NOT the default file!
            if self.current_file_path is None:
                # No file loaded yet - prompt user to choose location
                from PyQt6.QtWidgets import QFileDialog
                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Qt Widget Themes",
                    str(self.theme_manager.qt_widget_themes_dir / "qt_themes.json"),
                    "JSON Files (*.json);;All Files (*)"
                )

                if not filename:
                    self.style_edit.blockSignals(False)
                    return  # User cancelled

                self.current_file_path = filename

            # Save to the tracked file
            self.theme_manager.save_qt_widget_themes(self.themes, filepath=self.current_file_path)
            self.unsaved_changes = False

            # Update file status label
            self._update_file_status_label()

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Qt widget themes saved successfully to:\n{self.current_file_path}"
            )

            # Unblock signals
            self.style_edit.blockSignals(False)
        except Exception as e:
            self.style_edit.blockSignals(False)
            QMessageBox.critical(self, "Error", f"Failed to save themes:\n{e}")

    def _save_as(self):
        """Save themes to a new file"""
        from PyQt6.QtWidgets import QFileDialog

        # Suggest current location or default
        suggested_path = self.current_file_path if self.current_file_path else str(self.theme_manager.qt_widget_themes_dir / "qt_themes.json")

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Qt Widget Themes As",
            suggested_path,
            "JSON Files (*.json);;All Files (*)"
        )

        if not filename:
            return  # User cancelled

        try:
            # Update current file path
            self.current_file_path = filename

            # Save to new location
            self.theme_manager.save_qt_widget_themes(self.themes, filepath=self.current_file_path)
            self.unsaved_changes = False

            # Update file status label
            self._update_file_status_label()

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Qt widget themes saved successfully to:\n{self.current_file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save themes:\n{e}")

    def _update_file_status_label(self):
        """Update the file status label to show currently loaded file"""
        if self.current_file_path:
            self.file_status_label.setText(f"Editing: {self.current_file_path}")
            self.file_status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px; background-color: #3C3C3C; border-radius: 3px;")
        else:
            self.file_status_label.setText("No file loaded - click 'Load from File...' or 'New File' to start")
            self.file_status_label.setStyleSheet("color: #FF9800; font-weight: bold; padding: 5px; background-color: #3C3C3C; border-radius: 3px;")

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

            # CRITICAL: Track which file is currently loaded so we save to the right place!
            self.current_file_path = filename

            # Update UI
            self.theme_combo.blockSignals(True)
            self.theme_combo.clear()
            self.theme_combo.addItems(sorted(self.themes.keys()))
            self.theme_combo.blockSignals(False)

            if self.themes:
                self.theme_combo.setCurrentIndex(0)
                self._on_theme_changed(self.theme_combo.currentText())

            self.unsaved_changes = False  # Just loaded, so no unsaved changes yet
            self.themeModified.emit()

            # Update file status label
            self._update_file_status_label()

            QMessageBox.information(
                self,
                "File Loaded",
                f"Loaded {len(loaded_themes)} theme(s) from:\n{filename}\n\nChanges will be saved to this file."
            )

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
            spinbox = QSpinBox()
            spinbox.setValue(50)
            return spinbox
        elif base_selector == "QDoubleSpinBox":
            spinbox = QDoubleSpinBox()
            spinbox.setValue(3.14)
            return spinbox
        elif base_selector == "QDateEdit":
            date_edit = QDateEdit()
            from PyQt6.QtCore import QDate
            date_edit.setDate(QDate.currentDate())
            date_edit.setCalendarPopup(True)
            return date_edit
        elif base_selector == "QTimeEdit":
            time_edit = QTimeEdit()
            from PyQt6.QtCore import QTime
            time_edit.setTime(QTime.currentTime())
            return time_edit
        elif base_selector == "QDateTimeEdit":
            datetime_edit = QDateTimeEdit()
            from PyQt6.QtCore import QDateTime
            datetime_edit.setDateTime(QDateTime.currentDateTime())
            return datetime_edit
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
        elif base_selector == "QTabWidget":
            tabs = QTabWidget()
            tabs.addTab(QLabel("Tab 1 Content"), "Tab 1")
            tabs.addTab(QLabel("Tab 2 Content"), "Tab 2")
            tabs.setMaximumHeight(100)
            return tabs

        # Default: just show a widget
        return QWidget()

    def _update_visual_properties(self, style: str):
        """Parse CSS and create visual property controls using QFormLayout"""
        from PyQt6.QtWidgets import QFormLayout
        from .color_picker import ColorPickerButton

        # Clear existing properties (remove form layout if exists)
        while self.props_layout.count() > 1:  # Keep the stretch
            item = self.props_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Delete the form layout and all its children
                layout = item.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        if not style:
            return

        # Parse CSS properties
        properties = self._parse_css_properties(style)

        if not properties:
            return

        # Create a QFormLayout for proper label-field alignment
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setHorizontalSpacing(12)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Create controls for each property
        for prop_name, prop_value in properties.items():
            # Check if it's a color property (look for color keywords OR hex values anywhere in the value)
            is_color_prop = any(color_word in prop_name.lower() for color_word in ['color', 'background', 'border'])
            has_hex = '#' in prop_value
            is_named_color = prop_value.lower() in ['transparent', 'none', 'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'gray', 'grey']

            if is_color_prop and (has_hex or is_named_color):
                # Extract the actual color value from the property
                # Handle cases like "5px solid #D5A200" or "1px solid transparent"
                color_value = self._extract_color_from_value(prop_value)
                if color_value:
                    # Color picker button
                    color_picker = ColorPickerButton(color_value)
                    color_picker.colorChanged.connect(lambda c, p=prop_name: self._on_color_changed(p, c))
                    form_layout.addRow(f"{prop_name}:", color_picker)
                else:
                    # Fallback to text edit if we can't extract color
                    text_edit = QLineEdit(prop_value)
                    text_edit.textChanged.connect(lambda t, p=prop_name: self._on_text_property_changed(p, t))
                    form_layout.addRow(f"{prop_name}:", text_edit)

            elif prop_name in ['padding', 'margin', 'border-width'] and prop_value.replace('px', '').strip().isdigit():
                # Spinbox for dimensions
                spinbox = QSpinBox()
                spinbox.setRange(0, 100)
                spinbox.setValue(int(prop_value.replace('px', '').strip()))
                spinbox.setSuffix(" px")
                spinbox.valueChanged.connect(lambda v, p=prop_name: self._on_dimension_changed(p, v))
                form_layout.addRow(f"{prop_name}:", spinbox)

            elif prop_name == 'border-radius' and 'px' in prop_value:
                # Spinbox for border radius
                spinbox = QSpinBox()
                spinbox.setRange(0, 50)
                spinbox.setValue(int(prop_value.replace('px', '').strip()))
                spinbox.setSuffix(" px")
                spinbox.valueChanged.connect(lambda v, p=prop_name: self._on_dimension_changed(p, v))
                form_layout.addRow(f"{prop_name}:", spinbox)

            else:
                # Text field for other properties
                text_edit = QLineEdit(prop_value)
                text_edit.textChanged.connect(lambda t, p=prop_name: self._on_text_property_changed(p, t))
                form_layout.addRow(f"{prop_name}:", text_edit)

        # Insert the form layout into the main props layout
        self.props_layout.insertLayout(self.props_layout.count() - 1, form_layout)

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

    def _extract_color_from_value(self, value: str) -> Optional[str]:
        """Extract color value from a CSS property value

        Handles cases like:
        - "#D5A200" -> "#D5A200"
        - "5px solid #D5A200" -> "#D5A200"
        - "transparent" -> "#00000000" (transparent black)
        - "1px solid transparent" -> "#00000000"
        """
        import re

        value_lower = value.lower()

        # Check for hex color
        hex_match = re.search(r'#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?', value)
        if hex_match:
            return hex_match.group(0).upper()

        # Check for named colors (map to hex)
        named_colors = {
            'transparent': '#000000',  # Show as black in picker, but we know it's transparent
            'none': '#000000',
            'black': '#000000',
            'white': '#FFFFFF',
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'cyan': '#00FFFF',
            'magenta': '#FF00FF',
            'gray': '#808080',
            'grey': '#808080',
            'darkgray': '#A9A9A9',
            'darkgrey': '#A9A9A9',
            'lightgray': '#D3D3D3',
            'lightgrey': '#D3D3D3',
        }

        # Check if the entire value is a named color
        if value_lower in named_colors:
            return named_colors[value_lower]

        # Check if value contains a named color (e.g., "1px solid transparent")
        for color_name, hex_val in named_colors.items():
            if color_name in value_lower:
                return hex_val

        return None

    def _on_color_changed(self, prop_name: str, color: str):
        """Handle color picker change"""
        if self.updating_from_code:
            return

        # Get current value to see if we need to replace color within a complex value
        if not self.current_theme or not self.widget_list.currentItem():
            return

        widget_selector = self.widget_list.currentItem().text()
        current_style = self.current_theme.get_widget_style(widget_selector) or ""
        properties = self._parse_css_properties(current_style)
        current_value = properties.get(prop_name, "")

        # If the current value contains more than just a color (e.g., "5px solid #D5A200"),
        # replace just the color part
        import re
        if '#' in current_value:
            # Replace existing hex color with new color
            new_value = re.sub(r'#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?', color, current_value)
        elif any(named in current_value.lower() for named in ['transparent', 'none', 'black', 'white', 'red', 'green', 'blue']):
            # Replace named color with hex color
            # This is tricky, let's just replace the whole value for now
            new_value = color
        else:
            # Just a simple color value
            new_value = color

        self._update_css_property(prop_name, new_value)

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
