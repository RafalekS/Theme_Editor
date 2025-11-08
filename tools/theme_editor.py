#!/usr/bin/env python3
"""
PyQt6 Theme Editor - Visual QSS Theme Editor
A standalone application for creating and editing PyQt6 themes visually
"""

import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QListWidget,
    QCheckBox, QRadioButton, QGroupBox, QTabWidget, QProgressBar,
    QSpinBox, QSlider, QFileDialog, QMessageBox, QColorDialog,
    QSplitter, QScrollArea, QGridLayout, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QAction


class ColorButton(QPushButton):
    """Custom button widget for color selection"""

    def __init__(self, color="#000000", parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(40, 30)
        self.update_color(color)
        self.clicked.connect(self.choose_color)

    def update_color(self, color):
        """Update button color"""
        self.color = color
        self.setStyleSheet(f"background-color: {color}; border: 2px solid #999;")

    def choose_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor(QColor(self.color), self, "Choose Color")
        if color.isValid():
            self.update_color(color.name())

    def get_color(self):
        """Get current color"""
        return self.color


class ThemePreviewWidget(QWidget):
    """Widget that shows preview of theme with sample UI elements"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup preview UI with various widget types"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Live Theme Preview")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        # Buttons group
        button_group = QGroupBox("Buttons")
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Normal Button"))
        button_layout.addWidget(QPushButton("Disabled Button"))
        disabled_btn = QPushButton("Disabled")
        disabled_btn.setEnabled(False)
        button_layout.addWidget(disabled_btn)
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)

        # Input fields group
        input_group = QGroupBox("Input Fields")
        input_layout = QVBoxLayout()

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter text here...")
        input_layout.addWidget(QLabel("Line Edit:"))
        input_layout.addWidget(line_edit)

        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Multi-line text editor...")
        text_edit.setMaximumHeight(80)
        input_layout.addWidget(QLabel("Text Edit:"))
        input_layout.addWidget(text_edit)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Combo box and spin box
        controls_group = QGroupBox("Controls")
        controls_layout = QFormLayout()

        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        controls_layout.addRow("Combo Box:", combo)

        spin = QSpinBox()
        spin.setRange(0, 100)
        spin.setValue(50)
        controls_layout.addRow("Spin Box:", spin)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Checkboxes and radio buttons
        selection_group = QGroupBox("Selection Controls")
        selection_layout = QVBoxLayout()

        cb1 = QCheckBox("Checkbox Option 1")
        cb1.setChecked(True)
        cb2 = QCheckBox("Checkbox Option 2")
        selection_layout.addWidget(cb1)
        selection_layout.addWidget(cb2)

        rb1 = QRadioButton("Radio Option 1")
        rb1.setChecked(True)
        rb2 = QRadioButton("Radio Option 2")
        selection_layout.addWidget(rb1)
        selection_layout.addWidget(rb2)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Progress bar
        progress_group = QGroupBox("Progress Bar")
        progress_layout = QVBoxLayout()
        progress = QProgressBar()
        progress.setValue(65)
        progress_layout.addWidget(progress)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # List widget
        list_group = QGroupBox("List Widget")
        list_layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.addItems(["List Item 1", "List Item 2", "List Item 3", "List Item 4"])
        list_widget.setCurrentRow(1)
        list_widget.setMaximumHeight(100)
        list_layout.addWidget(list_widget)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(QLabel("Content of Tab 1"), "Tab 1")
        tab_widget.addTab(QLabel("Content of Tab 2"), "Tab 2")
        tab_widget.addTab(QLabel("Content of Tab 3"), "Tab 3")
        tab_widget.setMaximumHeight(100)
        layout.addWidget(tab_widget)

        layout.addStretch()


class ThemeEditorWindow(QMainWindow):
    """Main theme editor window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Theme Editor")
        self.setGeometry(100, 100, 1400, 900)

        # Current theme data
        self.current_theme_file = None
        self.themes_dir = "themes"

        # Color scheme mapping
        self.color_scheme = {
            'background': '#1e1e1e',
            'foreground': '#e0e0e0',
            'primary': '#007acc',
            'secondary': '#3c3c3c',
            'border': '#5a5a5a',
            'hover': '#1177bb',
            'selected': '#094771',
            'disabled': '#6d6d6d',
        }

        self.setup_ui()
        self.setup_menu_bar()
        self.load_available_themes()

    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Top toolbar
        toolbar_layout = QHBoxLayout()

        toolbar_layout.addWidget(QLabel("Load Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self.load_theme)
        toolbar_layout.addWidget(self.theme_combo)

        self.new_theme_btn = QPushButton("New Theme")
        self.new_theme_btn.clicked.connect(self.new_theme)
        toolbar_layout.addWidget(self.new_theme_btn)

        self.save_btn = QPushButton("Save Theme")
        self.save_btn.clicked.connect(self.save_theme)
        toolbar_layout.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("Save As...")
        self.save_as_btn.clicked.connect(self.save_theme_as)
        toolbar_layout.addWidget(self.save_as_btn)

        toolbar_layout.addStretch()

        self.apply_btn = QPushButton("Apply to Preview")
        self.apply_btn.clicked.connect(self.apply_to_preview)
        self.apply_btn.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold; padding: 8px 16px;")
        toolbar_layout.addWidget(self.apply_btn)

        main_layout.addLayout(toolbar_layout)

        # Main splitter (left: controls, right: preview)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Color scheme editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("<b>Color Scheme Editor</b>"))

        # Color pickers
        colors_scroll = QScrollArea()
        colors_scroll.setWidgetResizable(True)
        colors_widget = QWidget()
        colors_layout = QGridLayout(colors_widget)

        self.color_buttons = {}
        row = 0

        color_descriptions = {
            'background': 'Main Background Color',
            'foreground': 'Text Color',
            'primary': 'Primary Accent (Buttons, Links)',
            'secondary': 'Secondary Background',
            'border': 'Border Color',
            'hover': 'Hover State Color',
            'selected': 'Selected Item Color',
            'disabled': 'Disabled Element Color',
        }

        for key, desc in color_descriptions.items():
            label = QLabel(f"{desc}:")
            colors_layout.addWidget(label, row, 0)

            color_btn = ColorButton(self.color_scheme.get(key, '#000000'))
            self.color_buttons[key] = color_btn
            colors_layout.addWidget(color_btn, row, 1)

            # Color code display
            code_label = QLabel(self.color_scheme.get(key, '#000000'))
            code_label.setObjectName(f"code_{key}")
            code_label.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
            colors_layout.addWidget(code_label, row, 2)

            # Connect button to update label
            color_btn.clicked.connect(lambda checked, k=key, btn=color_btn: self.update_color_code(k, btn))

            row += 1

        colors_layout.setRowStretch(row, 1)
        colors_scroll.setWidget(colors_widget)
        left_layout.addWidget(colors_scroll)

        # Generate QSS button
        generate_btn = QPushButton("Generate QSS from Colors")
        generate_btn.clicked.connect(self.generate_qss_from_colors)
        generate_btn.setStyleSheet("background-color: #0e639c; color: white; padding: 10px;")
        left_layout.addWidget(generate_btn)

        # Info label
        info_label = QLabel("Edit colors above and click 'Generate QSS from Colors' to create stylesheet, then 'Apply to Preview' to see changes.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #ffffcc; border: 1px solid #cccc00;")
        left_layout.addWidget(info_label)

        main_splitter.addWidget(left_widget)

        # Right side: Preview
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Preview area (scrollable)
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        self.preview_widget = ThemePreviewWidget()
        preview_scroll.setWidget(self.preview_widget)
        right_splitter.addWidget(preview_scroll)

        # QSS Code editor
        code_widget = QWidget()
        code_layout = QVBoxLayout(code_widget)
        code_layout.setContentsMargins(0, 0, 0, 0)

        code_layout.addWidget(QLabel("<b>QSS Code (Qt Style Sheet)</b>"))

        self.qss_editor = QTextEdit()
        self.qss_editor.setFont(QFont("Courier New", 10))
        self.qss_editor.setPlaceholderText("QSS code will appear here...")
        code_layout.addWidget(self.qss_editor)

        right_splitter.addWidget(code_widget)

        # Set splitter sizes
        right_splitter.setSizes([500, 300])

        main_splitter.addWidget(right_splitter)

        # Set main splitter sizes
        main_splitter.setSizes([400, 1000])

        main_layout.addWidget(main_splitter)

        # Status bar
        self.statusBar().showMessage("Ready. Load or create a theme to start editing.")

    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Theme", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_theme)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Theme...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_theme_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_theme)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_theme_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def load_available_themes(self):
        """Load available theme files from themes directory"""
        self.theme_combo.clear()

        if os.path.exists(self.themes_dir):
            theme_files = [f[:-4] for f in os.listdir(self.themes_dir) if f.endswith('.qss')]
            self.theme_combo.addItems(theme_files)

        if self.theme_combo.count() == 0:
            self.theme_combo.addItem("No themes found")

    def load_theme(self, theme_name):
        """Load a theme file"""
        if theme_name == "No themes found":
            return

        theme_file = os.path.join(self.themes_dir, f"{theme_name}.qss")

        if os.path.exists(theme_file):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    qss_content = f.read()

                self.qss_editor.setPlainText(qss_content)
                self.current_theme_file = theme_file
                self.statusBar().showMessage(f"Loaded theme: {theme_name}")

                # Try to extract colors from QSS
                self.extract_colors_from_qss(qss_content)

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load theme: {str(e)}")

    def extract_colors_from_qss(self, qss_content):
        """Extract color values from QSS content and update color pickers"""
        # Try to find common color patterns
        patterns = {
            'background': r'background-color:\s*(#[0-9a-fA-F]{6})',
            'foreground': r'color:\s*(#[0-9a-fA-F]{6})',
            'border': r'border:.*?(#[0-9a-fA-F]{6})',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, qss_content)
            if match and key in self.color_buttons:
                color = match.group(1)
                self.color_buttons[key].update_color(color)
                self.color_scheme[key] = color
                self.update_color_code(key, self.color_buttons[key])

    def update_color_code(self, key, button):
        """Update color code label when color changes"""
        color = button.get_color()
        self.color_scheme[key] = color

        # Update the label
        code_label = self.findChild(QLabel, f"code_{key}")
        if code_label:
            code_label.setText(color)

    def generate_qss_from_colors(self):
        """Generate QSS stylesheet from current color scheme"""
        # Update color scheme from buttons
        for key, button in self.color_buttons.items():
            self.color_scheme[key] = button.get_color()

        qss = self.create_qss_template(self.color_scheme)
        self.qss_editor.setPlainText(qss)
        self.statusBar().showMessage("QSS generated from color scheme. Click 'Apply to Preview' to see changes.")

    def create_qss_template(self, colors):
        """Create QSS template with color scheme"""
        return f'''/* Generated Theme */

/* Main Window and Base Widgets */
QMainWindow, QDialog, QWidget {{
    background-color: {colors['background']};
    color: {colors['foreground']};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
}}

/* Push Buttons */
QPushButton {{
    background-color: {colors['primary']};
    color: {colors['foreground']};
    border: 1px solid {colors['primary']};
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {colors['hover']};
    border: 1px solid {colors['hover']};
}}

QPushButton:pressed {{
    background-color: {colors['selected']};
}}

QPushButton:disabled {{
    background-color: {colors['secondary']};
    color: {colors['disabled']};
    border: 1px solid {colors['secondary']};
}}

/* Line Edit */
QLineEdit {{
    background-color: {colors['secondary']};
    color: {colors['foreground']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    padding: 5px 8px;
    selection-background-color: {colors['primary']};
}}

QLineEdit:focus {{
    border: 1px solid {colors['primary']};
}}

/* Text Edit */
QTextEdit, QPlainTextEdit {{
    background-color: {colors['background']};
    color: {colors['foreground']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    padding: 8px;
    selection-background-color: {colors['selected']};
}}

/* List Widget */
QListWidget {{
    background-color: {colors['background']};
    color: {colors['foreground']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
}}

QListWidget::item:selected {{
    background-color: {colors['selected']};
    color: {colors['foreground']};
}}

QListWidget::item:hover:!selected {{
    background-color: {colors['secondary']};
}}

/* Combo Box */
QComboBox {{
    background-color: {colors['secondary']};
    color: {colors['foreground']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    padding: 5px 8px;
}}

QComboBox:hover {{
    border: 1px solid {colors['primary']};
}}

QComboBox QAbstractItemView {{
    background-color: {colors['secondary']};
    color: {colors['foreground']};
    border: 1px solid {colors['primary']};
    selection-background-color: {colors['selected']};
}}

/* Spin Box */
QSpinBox {{
    background-color: {colors['secondary']};
    color: {colors['foreground']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    padding: 5px 8px;
}}

/* Check Box */
QCheckBox {{
    color: {colors['foreground']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {colors['border']};
    border-radius: 3px;
    background-color: {colors['secondary']};
}}

QCheckBox::indicator:checked {{
    background-color: {colors['primary']};
    border: 1px solid {colors['primary']};
}}

/* Radio Button */
QRadioButton {{
    color: {colors['foreground']};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {colors['border']};
    border-radius: 9px;
    background-color: {colors['secondary']};
}}

QRadioButton::indicator:checked {{
    background-color: {colors['primary']};
    border: 1px solid {colors['primary']};
}}

/* Group Box */
QGroupBox {{
    color: {colors['foreground']};
    border: 1px solid {colors['border']};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: 500;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: {colors['background']};
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {colors['border']};
    background-color: {colors['background']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background-color: {colors['secondary']};
    color: {colors['foreground']};
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: {colors['primary']};
    color: {colors['foreground']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {colors['hover']};
}}

/* Progress Bar */
QProgressBar {{
    background-color: {colors['secondary']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    text-align: center;
    color: {colors['foreground']};
}}

QProgressBar::chunk {{
    background-color: {colors['primary']};
    border-radius: 3px;
}}

/* Scroll Bar */
QScrollBar:vertical {{
    background-color: {colors['background']};
    width: 14px;
    border-radius: 7px;
}}

QScrollBar::handle:vertical {{
    background-color: {colors['secondary']};
    min-height: 30px;
    border-radius: 7px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors['border']};
}}
'''

    def apply_to_preview(self):
        """Apply current QSS to preview widget"""
        qss = self.qss_editor.toPlainText()

        try:
            self.preview_widget.setStyleSheet(qss)
            self.statusBar().showMessage("Theme applied to preview successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to apply theme: {str(e)}")

    def new_theme(self):
        """Create a new theme"""
        name, ok = QFileDialog.getSaveFileName(
            self,
            "New Theme",
            os.path.join(self.themes_dir, "new_theme.qss"),
            "QSS Files (*.qss)"
        )

        if ok and name:
            self.current_theme_file = name
            self.qss_editor.clear()
            self.generate_qss_from_colors()
            self.statusBar().showMessage(f"New theme ready: {os.path.basename(name)}")

    def open_theme_file(self):
        """Open a theme file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Theme",
            self.themes_dir,
            "QSS Files (*.qss);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    qss_content = f.read()

                self.qss_editor.setPlainText(qss_content)
                self.current_theme_file = file_path
                self.statusBar().showMessage(f"Opened: {os.path.basename(file_path)}")
                self.extract_colors_from_qss(qss_content)

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")

    def save_theme(self):
        """Save current theme"""
        if not self.current_theme_file:
            self.save_theme_as()
            return

        try:
            with open(self.current_theme_file, 'w', encoding='utf-8') as f:
                f.write(self.qss_editor.toPlainText())

            self.statusBar().showMessage(f"Theme saved: {os.path.basename(self.current_theme_file)}")
            QMessageBox.information(self, "Success", "Theme saved successfully!")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save theme: {str(e)}")

    def save_theme_as(self):
        """Save theme with new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Theme As",
            self.themes_dir,
            "QSS Files (*.qss)"
        )

        if file_path:
            try:
                # Ensure .qss extension
                if not file_path.endswith('.qss'):
                    file_path += '.qss'

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.qss_editor.toPlainText())

                self.current_theme_file = file_path
                self.statusBar().showMessage(f"Theme saved as: {os.path.basename(file_path)}")
                self.load_available_themes()
                QMessageBox.information(self, "Success", "Theme saved successfully!")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save theme: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Theme Editor",
            "<h2>PyQt6 Theme Editor</h2>"
            "<p>Visual editor for creating and modifying PyQt6 themes (QSS files).</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Visual color scheme editor</li>"
            "<li>Live preview of theme changes</li>"
            "<li>QSS code editor</li>"
            "<li>Load and save themes</li>"
            "</ul>"
            "<p>Part of JSON Template Combiner project.</p>"
        )


def main():
    """Main entry point"""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("PyQt6 Theme Editor")
    app.setOrganizationName("JSON Template Combiner")

    # Create and show main window
    window = ThemeEditorWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
