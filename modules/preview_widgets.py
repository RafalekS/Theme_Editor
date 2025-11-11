"""
Preview Widgets
Live preview components for different theme formats
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QTextEdit, QLabel, QFrame, QPushButton, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton, QProgressBar, QSlider,
    QListWidget, QTreeWidget, QTableWidget, QTabWidget, QGroupBox,
    QScrollArea, QTreeWidgetItem, QTableWidgetItem, QSplitter,
    QPlainTextEdit, QDateEdit, QTimeEdit, QDateTimeEdit, QCalendarWidget,
    QDial, QLCDNumber, QToolBar, QToolButton, QToolBox, QDockWidget,
    QHeaderView
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import pyqtSignal


class TerminalPreviewWidget(QWidget):
    """
    Preview terminal output with theme colors
    Shows sample terminal commands and output with ANSI color highlighting
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup preview UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Terminal Preview")
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(title)

        # Terminal output area
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Consolas", 10))
        self.terminal_output.setMinimumHeight(400)

        # Frame style for terminal
        self.terminal_frame = QFrame()
        frame_layout = QVBoxLayout(self.terminal_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self.terminal_output)

        layout.addWidget(self.terminal_frame)

        # Generate sample terminal content
        self._update_preview()

    def set_theme(self, theme):
        """
        Apply theme to terminal preview

        Args:
            theme: TerminalTheme object
        """
        self.current_theme = theme
        self._update_preview()

    def _update_preview(self):
        """Update terminal preview with current theme"""
        if self.current_theme is None:
            return

        # Set terminal background and foreground
        self.terminal_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.current_theme.background};
                color: {self.current_theme.foreground};
                border: 2px solid {self.current_theme.brightBlack};
                border-radius: 4px;
                padding: 10px;
            }}
        """)

        # Clear and rebuild content
        self.terminal_output.clear()
        cursor = self.terminal_output.textCursor()

        # Sample terminal content with colors
        self._add_prompt(cursor)
        self._add_text(cursor, "ls -la\n", self.current_theme.foreground)

        # Directory listing with colors
        self._add_text(cursor, "drwxr-xr-x  ", self.current_theme.brightBlack)
        self._add_text(cursor, "5 user user ", self.current_theme.foreground)
        self._add_text(cursor, "4096 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  8 12:00 ", self.current_theme.yellow)
        self._add_text(cursor, ".\n", self.current_theme.blue, bold=True)

        self._add_text(cursor, "drwxr-xr-x ", self.current_theme.brightBlack)
        self._add_text(cursor, "23 user user ", self.current_theme.foreground)
        self._add_text(cursor, "4096 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  7 18:30 ", self.current_theme.yellow)
        self._add_text(cursor, "..\n", self.current_theme.blue, bold=True)

        self._add_text(cursor, "-rw-r--r--  ", self.current_theme.brightBlack)
        self._add_text(cursor, "1 user user  ", self.current_theme.foreground)
        self._add_text(cursor, "220 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  1 09:15 ", self.current_theme.yellow)
        self._add_text(cursor, ".bashrc\n", self.current_theme.foreground)

        self._add_text(cursor, "-rwxr-xr-x  ", self.current_theme.brightBlack)
        self._add_text(cursor, "1 user user ", self.current_theme.foreground)
        self._add_text(cursor, "1024 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  8 08:00 ", self.current_theme.yellow)
        self._add_text(cursor, "main.py\n", self.current_theme.green, bold=True)

        self._add_text(cursor, "drwxr-xr-x  ", self.current_theme.brightBlack)
        self._add_text(cursor, "2 user user ", self.current_theme.foreground)
        self._add_text(cursor, "4096 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  7 14:22 ", self.current_theme.yellow)
        self._add_text(cursor, "modules\n", self.current_theme.blue, bold=True)

        cursor.insertText("\n")

        # Git status example
        self._add_prompt(cursor)
        self._add_text(cursor, "git status\n", self.current_theme.foreground)
        self._add_text(cursor, "On branch ", self.current_theme.foreground)
        self._add_text(cursor, "main\n", self.current_theme.cyan, bold=True)
        self._add_text(cursor, "Your branch is up to date with ", self.current_theme.foreground)
        self._add_text(cursor, "'origin/main'\n", self.current_theme.cyan)
        cursor.insertText("\n")

        self._add_text(cursor, "Changes not staged for commit:\n", self.current_theme.red, bold=True)
        self._add_text(cursor, "  modified:   ", self.current_theme.red)
        self._add_text(cursor, "main.py\n", self.current_theme.foreground)
        cursor.insertText("\n")

        self._add_text(cursor, "Untracked files:\n", self.current_theme.red, bold=True)
        self._add_text(cursor, "  ", self.current_theme.foreground)
        self._add_text(cursor, "modules/\n", self.current_theme.red)
        cursor.insertText("\n")

        # Success message
        self._add_prompt(cursor)
        self._add_text(cursor, "npm install\n", self.current_theme.foreground)
        self._add_text(cursor, "✓ ", self.current_theme.green, bold=True)
        self._add_text(cursor, "Successfully installed ", self.current_theme.foreground)
        self._add_text(cursor, "25 packages\n", self.current_theme.brightGreen, bold=True)
        cursor.insertText("\n")

        # Error message
        self._add_prompt(cursor)
        self._add_text(cursor, "python broken_script.py\n", self.current_theme.foreground)
        self._add_text(cursor, "Error: ", self.current_theme.brightRed, bold=True)
        self._add_text(cursor, "Module not found\n", self.current_theme.red)
        self._add_text(cursor, "  File ", self.current_theme.foreground)
        self._add_text(cursor, '"broken_script.py"', self.current_theme.yellow)
        self._add_text(cursor, ", line ", self.current_theme.foreground)
        self._add_text(cursor, "42\n", self.current_theme.cyan)
        cursor.insertText("\n")

        # ANSI color test
        self._add_prompt(cursor)
        self._add_text(cursor, "echo 'Color Test'\n", self.current_theme.foreground)

        # Normal colors
        self._add_text(cursor, "■ ", self.current_theme.black)
        self._add_text(cursor, "■ ", self.current_theme.red)
        self._add_text(cursor, "■ ", self.current_theme.green)
        self._add_text(cursor, "■ ", self.current_theme.yellow)
        self._add_text(cursor, "■ ", self.current_theme.blue)
        self._add_text(cursor, "■ ", self.current_theme.purple)
        self._add_text(cursor, "■ ", self.current_theme.cyan)
        self._add_text(cursor, "■ ", self.current_theme.white)
        self._add_text(cursor, " Normal\n", self.current_theme.foreground)

        # Bright colors
        self._add_text(cursor, "■ ", self.current_theme.brightBlack)
        self._add_text(cursor, "■ ", self.current_theme.brightRed)
        self._add_text(cursor, "■ ", self.current_theme.brightGreen)
        self._add_text(cursor, "■ ", self.current_theme.brightYellow)
        self._add_text(cursor, "■ ", self.current_theme.brightBlue)
        self._add_text(cursor, "■ ", self.current_theme.brightPurple)
        self._add_text(cursor, "■ ", self.current_theme.brightCyan)
        self._add_text(cursor, "■ ", self.current_theme.brightWhite)
        self._add_text(cursor, " Bright\n", self.current_theme.foreground)

        cursor.insertText("\n")
        self._add_prompt(cursor)

    def _add_prompt(self, cursor):
        """Add command prompt"""
        if self.current_theme:
            self._add_text(cursor, "user@host", self.current_theme.green, bold=True)
            self._add_text(cursor, ":", self.current_theme.foreground)
            self._add_text(cursor, "~/project", self.current_theme.blue, bold=True)
            self._add_text(cursor, "$ ", self.current_theme.foreground)

    def _add_text(self, cursor, text, color, bold=False):
        """
        Add colored text to terminal

        Args:
            cursor: QTextCursor
            text: Text to add
            color: Hex color string
            bold: Whether text should be bold
        """
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)

        cursor.insertText(text, fmt)


class QSSPreviewWidget(QWidget):
    """
    Live preview of QSS theme on sample Qt widgets
    Shows comprehensive widget gallery with theme applied
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_qss = ""
        self._setup_ui()

    def _setup_ui(self):
        """Setup preview UI with sample widgets"""
        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for all widgets
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("QSS Theme Preview")
        title.setObjectName("previewTitle")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        # Buttons group
        buttons_group = QGroupBox("Buttons")
        buttons_layout = QHBoxLayout()
        
        normal_btn = QPushButton("Normal Button")
        buttons_layout.addWidget(normal_btn)
        
        disabled_btn = QPushButton("Disabled Button")
        disabled_btn.setEnabled(False)
        buttons_layout.addWidget(disabled_btn)
        
        buttons_group.setLayout(buttons_layout)
        layout.addWidget(buttons_group)

        # Input fields group
        input_group = QGroupBox("Input Fields")
        input_layout = QFormLayout()

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter text here...")
        input_layout.addRow("Line Edit:", line_edit)

        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Multi-line text editor...")
        text_edit.setMaximumHeight(80)
        input_layout.addRow("Text Edit:", text_edit)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Controls group
        controls_group = QGroupBox("Controls")
        controls_layout = QFormLayout()

        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        controls_layout.addRow("Combo Box:", combo)

        spinbox = QSpinBox()
        spinbox.setRange(0, 100)
        spinbox.setValue(50)
        controls_layout.addRow("Spin Box:", spinbox)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(75)
        controls_layout.addRow("Slider:", slider)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Checkboxes and Radio buttons
        check_radio_group = QGroupBox("Checkboxes & Radio Buttons")
        check_radio_layout = QVBoxLayout()

        checkbox1 = QCheckBox("Checkbox 1 (Checked)")
        checkbox1.setChecked(True)
        check_radio_layout.addWidget(checkbox1)

        checkbox2 = QCheckBox("Checkbox 2 (Unchecked)")
        check_radio_layout.addWidget(checkbox2)

        checkbox3 = QCheckBox("Checkbox 3 (Disabled)")
        checkbox3.setEnabled(False)
        check_radio_layout.addWidget(checkbox3)

        radio1 = QRadioButton("Radio Button 1 (Selected)")
        radio1.setChecked(True)
        check_radio_layout.addWidget(radio1)

        radio2 = QRadioButton("Radio Button 2")
        check_radio_layout.addWidget(radio2)

        check_radio_group.setLayout(check_radio_layout)
        layout.addWidget(check_radio_group)

        # Progress bar
        progress_group = QGroupBox("Progress Bar")
        progress_layout = QVBoxLayout()

        progress = QProgressBar()
        progress.setValue(60)
        progress_layout.addWidget(progress)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # List widget
        list_group = QGroupBox("List Widget")
        list_layout = QVBoxLayout()

        list_widget = QListWidget()
        list_widget.addItems(["Item 1", "Item 2", "Item 3 (Selected)", "Item 4", "Item 5"])
        list_widget.setCurrentRow(2)
        list_widget.setMaximumHeight(120)
        list_layout.addWidget(list_widget)

        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Tree widget
        tree_group = QGroupBox("Tree Widget")
        tree_layout = QVBoxLayout()

        tree = QTreeWidget()
        tree.setHeaderLabels(["Name", "Value"])
        tree.setMaximumHeight(120)
        
        root1 = QTreeWidgetItem(tree, ["Root Item 1", "100"])
        child1 = QTreeWidgetItem(root1, ["Child 1.1", "50"])
        child2 = QTreeWidgetItem(root1, ["Child 1.2", "50"])
        
        root2 = QTreeWidgetItem(tree, ["Root Item 2", "200"])
        child3 = QTreeWidgetItem(root2, ["Child 2.1", "100"])
        
        tree.expandAll()
        tree_layout.addWidget(tree)

        tree_group.setLayout(tree_layout)
        layout.addWidget(tree_group)

        # Table widget
        table_group = QGroupBox("Table Widget")
        table_layout = QVBoxLayout()

        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        table.setMaximumHeight(150)
        
        for row in range(3):
            for col in range(3):
                table.setItem(row, col, QTableWidgetItem(f"Cell {row},{col}"))
        
        table.selectRow(1)
        table_layout.addWidget(table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Tab widget
        tab_group = QGroupBox("Tab Widget")
        tab_layout = QVBoxLayout()

        tabs = QTabWidget()
        tabs.addTab(QLabel("Content of Tab 1"), "Tab 1")
        tabs.addTab(QLabel("Content of Tab 2"), "Tab 2")
        tabs.addTab(QLabel("Content of Tab 3"), "Tab 3")
        tabs.setMaximumHeight(100)
        tab_layout.addWidget(tabs)

        tab_group.setLayout(tab_layout)
        layout.addWidget(tab_group)

        layout.addStretch()

        scroll.setWidget(container)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Store reference to container for applying QSS
        self.preview_container = container

    def set_qss(self, qss_code: str):
        """
        Apply QSS code to preview

        Args:
            qss_code: QSS stylesheet code
        """
        self.current_qss = qss_code
        if self.preview_container:
            self.preview_container.setStyleSheet(qss_code)


class QtWidgetPreviewPanel(QWidget):
    """
    Comprehensive preview panel showing all Qt widgets
    Used by Qt Widget Theme Editor
    """

    # Signal emitted when a widget is clicked (sends widget selector name)
    widget_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._widget_map = {}  # Maps widget instance to selector name
        self._setup_ui()

    def _register_clickable_widget(self, widget, selector_name):
        """Register a widget to emit signal when clicked"""
        self._widget_map[widget] = selector_name
        widget.installEventFilter(self)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)

        # Also install event filter on all child widgets to catch clicks
        # on composite widgets (e.g., clicking tab bar in QTabWidget)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Filter events to detect widget clicks"""
        if event.type() == QEvent.Type.MouseButtonPress:
            # Walk up the parent hierarchy to find the closest registered widget
            # This handles composite widgets (e.g., clicking on tab bar finds QTabWidget)
            current = obj
            while current is not None:
                if current in self._widget_map:
                    selector = self._widget_map[current]
                    self.widget_clicked.emit(selector)
                    return False  # Let the event propagate
                current = current.parentWidget()
        return super().eventFilter(obj, event)

    def _setup_ui(self):
        """Setup comprehensive widget preview"""
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for all widgets
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Buttons group
        buttons_group = QGroupBox("Buttons")
        buttons_layout = QVBoxLayout()

        # Regular buttons
        btn_row1 = QHBoxLayout()
        normal_btn = QPushButton("Normal Button")
        self._register_clickable_widget(normal_btn, "QPushButton")
        btn_row1.addWidget(normal_btn)

        disabled_btn = QPushButton("Disabled Button")
        disabled_btn.setEnabled(False)
        self._register_clickable_widget(disabled_btn, "QPushButton:disabled")
        btn_row1.addWidget(disabled_btn)

        hover_btn = QPushButton("Hover Me")
        self._register_clickable_widget(hover_btn, "QPushButton:hover")
        btn_row1.addWidget(hover_btn)
        buttons_layout.addLayout(btn_row1)

        # Checkboxes and radio buttons
        check_radio_layout = QHBoxLayout()
        checkbox1 = QCheckBox("Unchecked")
        self._register_clickable_widget(checkbox1, "QCheckBox")
        check_radio_layout.addWidget(checkbox1)

        checked = QCheckBox("Checked")
        checked.setChecked(True)
        self._register_clickable_widget(checked, "QCheckBox::indicator:checked")
        check_radio_layout.addWidget(checked)

        radio1 = QRadioButton("Radio 1")
        self._register_clickable_widget(radio1, "QRadioButton")
        check_radio_layout.addWidget(radio1)

        radio2 = QRadioButton("Radio 2")
        radio2.setChecked(True)
        self._register_clickable_widget(radio2, "QRadioButton::indicator:checked")
        check_radio_layout.addWidget(radio2)
        buttons_layout.addLayout(check_radio_layout)

        buttons_group.setLayout(buttons_layout)
        main_layout.addWidget(buttons_group)

        # Input fields group
        inputs_group = QGroupBox("Input Fields")
        inputs_layout = QVBoxLayout()

        # Line edit
        inputs_layout.addWidget(QLabel("QLineEdit:"))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Type here...")
        self._register_clickable_widget(line_edit, "QLineEdit")
        inputs_layout.addWidget(line_edit)

        # Read-only line edit
        inputs_layout.addWidget(QLabel("QLineEdit (read-only):"))
        readonly_edit = QLineEdit("Read-only text")
        readonly_edit.setReadOnly(True)
        self._register_clickable_widget(readonly_edit, "QLineEdit:read-only")
        inputs_layout.addWidget(readonly_edit)

        # Text edit
        inputs_layout.addWidget(QLabel("QTextEdit:"))
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Multi-line text...")
        text_edit.setMaximumHeight(60)
        self._register_clickable_widget(text_edit, "QTextEdit")
        inputs_layout.addWidget(text_edit)

        inputs_group.setLayout(inputs_layout)
        main_layout.addWidget(inputs_group)

        # Selection widgets group
        selection_group = QGroupBox("Selection Widgets")
        selection_layout = QVBoxLayout()

        # ComboBox
        selection_layout.addWidget(QLabel("QComboBox:"))
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        self._register_clickable_widget(combo, "QComboBox")
        selection_layout.addWidget(combo)

        # Spin boxes
        spin_layout = QHBoxLayout()
        spin_layout.addWidget(QLabel("QSpinBox:"))
        spinbox = QSpinBox()
        self._register_clickable_widget(spinbox, "QSpinBox")
        spin_layout.addWidget(spinbox)
        spin_layout.addWidget(QLabel("QDoubleSpinBox:"))
        doublespinbox = QDoubleSpinBox()
        self._register_clickable_widget(doublespinbox, "QDoubleSpinBox")
        spin_layout.addWidget(doublespinbox)
        selection_layout.addLayout(spin_layout)

        # List widget
        selection_layout.addWidget(QLabel("QListWidget:"))
        list_widget = QListWidget()
        list_widget.addItems(["Item 1", "Item 2 (selected)", "Item 3", "Item 4"])
        list_widget.setCurrentRow(1)
        list_widget.setMaximumHeight(80)
        self._register_clickable_widget(list_widget, "QListWidget")
        selection_layout.addWidget(list_widget)

        selection_group.setLayout(selection_layout)
        main_layout.addWidget(selection_group)

        # Progress and sliders group
        progress_group = QGroupBox("Progress & Sliders")
        progress_layout = QVBoxLayout()

        # Progress bar
        progress_layout.addWidget(QLabel("QProgressBar:"))
        progress = QProgressBar()
        progress.setValue(65)
        self._register_clickable_widget(progress, "QProgressBar")
        progress_layout.addWidget(progress)

        # Slider
        progress_layout.addWidget(QLabel("QSlider:"))
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setValue(50)
        self._register_clickable_widget(slider, "QSlider")
        progress_layout.addWidget(slider)

        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # Tabs group
        tabs_group = QGroupBox("QTabWidget")
        tabs_layout = QVBoxLayout()

        tab_widget = QTabWidget()
        tab_widget.addTab(QLabel("Content of Tab 1"), "Tab 1")
        tab_widget.addTab(QLabel("Content of Tab 2"), "Tab 2")
        tab_widget.addTab(QLabel("Content of Tab 3"), "Tab 3")
        tab_widget.setMaximumHeight(100)
        self._register_clickable_widget(tab_widget, "QTabWidget")
        tabs_layout.addWidget(tab_widget)

        tabs_group.setLayout(tabs_layout)
        main_layout.addWidget(tabs_group)

        # Scrollbar demo
        scroll_group = QGroupBox("QScrollBar & QScrollArea")
        scroll_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)
        for i in range(10):
            scroll_content_layout.addWidget(QLabel(f"Scroll content line {i + 1}"))
        scroll_area.setWidget(scroll_content)
        scroll_area.setMaximumHeight(80)
        self._register_clickable_widget(scroll_area, "QScrollArea")
        scroll_layout.addWidget(scroll_area)

        scroll_group.setLayout(scroll_layout)
        main_layout.addWidget(scroll_group)

        # Menu and status bar demo
        menu_group = QGroupBox("QMenuBar & QStatusBar Preview")
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(QLabel("(Menu and status bars are shown in main window)"))
        menu_group.setLayout(menu_layout)
        main_layout.addWidget(menu_group)

        # Splitter demo
        splitter_group = QGroupBox("QSplitter")
        splitter_layout = QVBoxLayout()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(QLabel("Left pane"))
        splitter.addWidget(QLabel("Right pane"))
        splitter.setMaximumHeight(50)
        self._register_clickable_widget(splitter, "QSplitter")
        splitter_layout.addWidget(splitter)

        splitter_group.setLayout(splitter_layout)
        main_layout.addWidget(splitter_group)

        # Tree and Table widgets group
        tree_table_group = QGroupBox("QTreeWidget & QTableWidget")
        tree_table_layout = QHBoxLayout()

        # Tree widget
        tree_layout = QVBoxLayout()
        tree_layout.addWidget(QLabel("QTreeWidget:"))
        tree = QTreeWidget()
        tree.setHeaderLabels(["Name", "Value"])
        tree.setMaximumHeight(120)

        root1 = QTreeWidgetItem(tree, ["Root 1", "100"])
        child1 = QTreeWidgetItem(root1, ["Child 1.1", "50"])
        child2 = QTreeWidgetItem(root1, ["Child 1.2", "50"])

        root2 = QTreeWidgetItem(tree, ["Root 2 (selected)", "200"])
        child3 = QTreeWidgetItem(root2, ["Child 2.1", "100"])

        tree.expandAll()
        tree.setCurrentItem(root2)
        self._register_clickable_widget(tree, "QTreeWidget")
        tree_layout.addWidget(tree)
        tree_table_layout.addLayout(tree_layout)

        # Table widget
        table_layout = QVBoxLayout()
        table_layout.addWidget(QLabel("QTableWidget:"))
        table = QTableWidget(4, 3)
        table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        table.setMaximumHeight(120)

        for row in range(4):
            for col in range(3):
                table.setItem(row, col, QTableWidgetItem(f"R{row}C{col}"))

        table.selectRow(1)
        self._register_clickable_widget(table, "QTableWidget")
        table_layout.addWidget(table)
        tree_table_layout.addLayout(table_layout)

        tree_table_group.setLayout(tree_table_layout)
        main_layout.addWidget(tree_table_group)

        # PlainTextEdit and Frame group
        plain_frame_group = QGroupBox("QPlainTextEdit & QFrame")
        plain_frame_layout = QHBoxLayout()

        # PlainTextEdit
        plain_layout = QVBoxLayout()
        plain_layout.addWidget(QLabel("QPlainTextEdit:"))
        plain_text = QPlainTextEdit()
        plain_text.setPlainText("Plain text editor\nLine 2\nLine 3")
        plain_text.setMaximumHeight(80)
        self._register_clickable_widget(plain_text, "QPlainTextEdit")
        plain_layout.addWidget(plain_text)
        plain_frame_layout.addLayout(plain_layout)

        # Frame
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(QLabel("QFrame:"))
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame.setMinimumHeight(80)
        frame_inner = QVBoxLayout(frame)
        frame_inner.addWidget(QLabel("Content inside QFrame"))
        self._register_clickable_widget(frame, "QFrame")
        frame_layout.addWidget(frame)
        plain_frame_layout.addLayout(frame_layout)

        plain_frame_group.setLayout(plain_frame_layout)
        main_layout.addWidget(plain_frame_group)

        # Date/Time widgets group
        datetime_group = QGroupBox("Date & Time Widgets")
        datetime_layout = QGridLayout()

        datetime_layout.addWidget(QLabel("QDateEdit:"), 0, 0)
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        self._register_clickable_widget(date_edit, "QDateEdit")
        datetime_layout.addWidget(date_edit, 0, 1)

        datetime_layout.addWidget(QLabel("QTimeEdit:"), 0, 2)
        time_edit = QTimeEdit()
        self._register_clickable_widget(time_edit, "QTimeEdit")
        datetime_layout.addWidget(time_edit, 0, 3)

        datetime_layout.addWidget(QLabel("QDateTimeEdit:"), 1, 0)
        datetime_edit = QDateTimeEdit()
        self._register_clickable_widget(datetime_edit, "QDateTimeEdit")
        datetime_layout.addWidget(datetime_edit, 1, 1, 1, 3)

        datetime_group.setLayout(datetime_layout)
        main_layout.addWidget(datetime_group)

        # Calendar widget group
        calendar_group = QGroupBox("QCalendarWidget")
        calendar_layout = QVBoxLayout()

        calendar = QCalendarWidget()
        calendar.setMaximumHeight(200)
        self._register_clickable_widget(calendar, "QCalendarWidget")
        calendar_layout.addWidget(calendar)

        calendar_group.setLayout(calendar_layout)
        main_layout.addWidget(calendar_group)

        # Dial and LCD group
        dial_lcd_group = QGroupBox("QDial & QLCDNumber")
        dial_lcd_layout = QHBoxLayout()

        # Dial
        dial_layout = QVBoxLayout()
        dial_layout.addWidget(QLabel("QDial:"))
        dial = QDial()
        dial.setMinimum(0)
        dial.setMaximum(100)
        dial.setValue(75)
        dial.setNotchesVisible(True)
        dial.setMaximumSize(100, 100)
        self._register_clickable_widget(dial, "QDial")
        dial_layout.addWidget(dial)
        dial_layout.addStretch()
        dial_lcd_layout.addLayout(dial_layout)

        # LCD Number
        lcd_layout = QVBoxLayout()
        lcd_layout.addWidget(QLabel("QLCDNumber:"))
        lcd = QLCDNumber()
        lcd.setDigitCount(6)
        lcd.display(123.45)
        lcd.setMaximumHeight(60)
        self._register_clickable_widget(lcd, "QLCDNumber")
        lcd_layout.addWidget(lcd)
        lcd_layout.addStretch()
        dial_lcd_layout.addLayout(lcd_layout)

        dial_lcd_group.setLayout(dial_lcd_layout)
        main_layout.addWidget(dial_lcd_group)

        # ToolBar and ToolButton group
        toolbar_group = QGroupBox("QToolBar & QToolButton")
        toolbar_layout = QVBoxLayout()

        toolbar = QToolBar("Sample Toolbar")
        toolbar.addAction("Action 1")
        toolbar.addAction("Action 2")
        toolbar.addSeparator()

        tool_btn = QToolButton()
        tool_btn.setText("Tool Button")
        self._register_clickable_widget(tool_btn, "QToolButton")
        toolbar.addWidget(tool_btn)

        self._register_clickable_widget(toolbar, "QToolBar")
        toolbar_layout.addWidget(toolbar)

        # Standalone tool buttons
        tool_btn_row = QHBoxLayout()
        tool_btn_row.addWidget(QLabel("QToolButton:"))
        tool_btn1 = QToolButton()
        tool_btn1.setText("Normal")
        self._register_clickable_widget(tool_btn1, "QToolButton")
        tool_btn_row.addWidget(tool_btn1)

        tool_btn2 = QToolButton()
        tool_btn2.setText("Checkable")
        tool_btn2.setCheckable(True)
        tool_btn2.setChecked(True)
        self._register_clickable_widget(tool_btn2, "QToolButton:checked")
        tool_btn_row.addWidget(tool_btn2)
        tool_btn_row.addStretch()

        toolbar_layout.addLayout(tool_btn_row)

        toolbar_group.setLayout(toolbar_layout)
        main_layout.addWidget(toolbar_group)

        # ToolBox group
        toolbox_group = QGroupBox("QToolBox")
        toolbox_layout = QVBoxLayout()

        toolbox = QToolBox()
        toolbox.addItem(QLabel("Content of Page 1"), "Page 1")
        toolbox.addItem(QLabel("Content of Page 2"), "Page 2")
        toolbox.addItem(QLabel("Content of Page 3"), "Page 3")
        toolbox.setMaximumHeight(150)
        self._register_clickable_widget(toolbox, "QToolBox")
        toolbox_layout.addWidget(toolbox)

        toolbox_group.setLayout(toolbox_layout)
        main_layout.addWidget(toolbox_group)

        # DockWidget info (can't easily preview in panel)
        dock_group = QGroupBox("QDockWidget")
        dock_layout = QVBoxLayout()
        dock_layout.addWidget(QLabel("QDockWidget is shown in the main window."))
        dock_layout.addWidget(QLabel("It appears as a dockable panel that can float or dock to edges."))
        dock_group.setLayout(dock_layout)
        main_layout.addWidget(dock_group)

        # Add stretch to push everything to top
        main_layout.addStretch()

        # Set scroll widget and add to main layout
        scroll.setWidget(container)

        # Main layout for this widget
        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(scroll)
