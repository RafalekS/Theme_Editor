"""
QSS Theme Editor
Editor for Qt Style Sheets (QSS) with 8-color palette and live preview
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QMessageBox, QFileDialog, QSplitter,
    QTextEdit, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
from .theme_data import QSSPalette
from .theme_manager import ThemeManager
from .color_picker import ColorPickerButton
from .preview_widgets import QSSPreviewWidget


class QSSThemeEditor(QWidget):
    """
    Complete QSS Theme Editor
    Features: 8-color palette editor, QSS code editor, live preview, load/save
    """

    # Signal emitted when theme is modified
    themeModified = pyqtSignal()

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_file = None
        self.current_palette = QSSPalette()
        self.color_pickers = {}  # Dict of property_name -> ColorPickerButton
        self.unsaved_changes = False

        self._setup_ui()
        self._load_default_theme()

    def _setup_ui(self):
        """Setup editor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Top toolbar: File operations and template selector
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Main content: 3-panel layout (Palette + Code + Preview)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Color palette editor (25%)
        palette_editor = self._create_palette_editor()
        splitter.addWidget(palette_editor)

        # Middle: QSS code editor (40%)
        code_editor = self._create_code_editor()
        splitter.addWidget(code_editor)

        # Right: Preview (35%)
        preview_widget = self._create_preview()
        splitter.addWidget(preview_widget)

        # Set splitter proportions
        splitter.setStretchFactor(0, 25)
        splitter.setStretchFactor(1, 40)
        splitter.setStretchFactor(2, 35)

        layout.addWidget(splitter, 1)  # Give stretch factor 1 to expand vertically

    def _create_toolbar(self) -> QWidget:
        """Create top toolbar with file operations and template selector"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(3)

        # File operations
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self._new_theme)
        toolbar_layout.addWidget(self.new_btn)

        self.open_btn = QPushButton("Open QSS...")
        self.open_btn.clicked.connect(self._open_theme)
        toolbar_layout.addWidget(self.open_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_theme)
        toolbar_layout.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("Save As...")
        self.save_as_btn.clicked.connect(self._save_theme_as)
        toolbar_layout.addWidget(self.save_as_btn)

        toolbar_layout.addSpacing(20)

        # Template selector
        label = QLabel("Template:")
        label.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(label)

        self.template_selector = QComboBox()
        self.template_selector.addItems([
            "Default",
            "Material Dark",
            "Material Light",
            "Flat Dark",
            "Flat Light"
        ])
        self.template_selector.currentTextChanged.connect(self._on_template_selected)
        toolbar_layout.addWidget(self.template_selector)

        toolbar_layout.addStretch()

        # Current file label
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: #666;")
        toolbar_layout.addWidget(self.file_label)

        return toolbar

    def _create_palette_editor(self) -> QWidget:
        """Create 8-color palette editor"""
        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(2, 2, 2, 2)
        container_layout.setSpacing(2)

        # Title - REMOVE to save space
        # container_layout.addWidget(title)

        # 8-color palette
        palette_group = QGroupBox("Color Palette")
        palette_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; padding-top: 5px; }")
        palette_layout = QGridLayout(palette_group)
        palette_layout.setSpacing(3)
        palette_layout.setContentsMargins(3, 8, 3, 3)

        colors = [
            ("background", "Background"),
            ("foreground", "Foreground"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("border", "Border"),
            ("hover", "Hover"),
            ("selected", "Selected"),
            ("disabled", "Disabled"),
        ]

        for i, (prop_name, label_text) in enumerate(colors):
            # Label
            label = QLabel(f"{label_text}:")
            palette_layout.addWidget(label, i, 0)

            # Color picker
            picker = ColorPickerButton("#000000", label_text)
            picker.colorChanged.connect(lambda _, p=prop_name: self._on_color_changed(p))
            self.color_pickers[prop_name] = picker
            palette_layout.addWidget(picker, i, 1)

        container_layout.addWidget(palette_group)

        # Generate button
        generate_btn = QPushButton("Generate QSS")
        generate_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        generate_btn.clicked.connect(self._generate_qss_from_palette)
        container_layout.addWidget(generate_btn)

        # Extract button
        extract_btn = QPushButton("Extract Palette")
        extract_btn.setStyleSheet("padding: 5px;")
        extract_btn.clicked.connect(self._extract_palette_from_qss)
        container_layout.addWidget(extract_btn)

        # Don't add stretch - scroll area handles sizing
        scroll.setWidget(container)

        return scroll

    def _create_code_editor(self) -> QWidget:
        """Create QSS code editor"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Title - REMOVE to save space
        # layout.addWidget(title)

        # Code editor (plain text for now, syntax highlighting can be added later)
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 9))
        self.code_editor.setPlaceholderText(
            "/* Qt Style Sheet (QSS) */\n\n"
            "QWidget {\n"
            "    background-color: #282828;\n"
            "    color: #EBDBB2;\n"
            "}\n\n"
            "/* Edit QSS code here or generate from palette... */"
        )
        self.code_editor.textChanged.connect(self._on_code_changed)
        layout.addWidget(self.code_editor)

        # Apply button
        apply_btn = QPushButton("Apply to Preview")
        apply_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        apply_btn.clicked.connect(self._apply_to_preview)
        layout.addWidget(apply_btn)

        return container

    def _create_preview(self) -> QWidget:
        """Create preview panel"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.preview = QSSPreviewWidget()
        layout.addWidget(self.preview, 1)  # Expand to fill space

        return container

    # ==================== Theme Operations ====================

    def _load_default_theme(self):
        """Load default theme"""
        # Set default palette
        self.current_palette = QSSPalette(
            background="#FFFFFF",
            foreground="#000000",
            primary="#0078D4",
            secondary="#6C757D",
            border="#CCCCCC",
            hover="#E5E5E5",
            selected="#0078D4",
            disabled="#999999"
        )
        self._update_palette_pickers()
        self._generate_qss_from_palette()
        # Reset unsaved flag after initialization
        self.unsaved_changes = False

    def _update_palette_pickers(self):
        """Update color pickers with current palette"""
        for prop_name, picker in self.color_pickers.items():
            picker.blockSignals(True)  # Block signals during update
            color = getattr(self.current_palette, prop_name)
            picker.set_color(color)
            picker.blockSignals(False)  # Re-enable signals

    def _on_color_changed(self, property_name: str):
        """Handle color picker change"""
        # Update palette
        new_color = self.color_pickers[property_name].get_color()
        setattr(self.current_palette, property_name, new_color)

        # Mark as unsaved
        self.unsaved_changes = True
        self.themeModified.emit()

    def _on_code_changed(self):
        """Handle QSS code change"""
        self.unsaved_changes = True
        self.themeModified.emit()

    def _on_template_selected(self, template_name: str):
        """Handle template selection"""
        # Create palette based on template
        if template_name == "Material Dark":
            self.current_palette = QSSPalette(
                background="#1E1E1E",
                foreground="#FFFFFF",
                primary="#BB86FC",
                secondary="#03DAC6",
                border="#3C3C3C",
                hover="#2D2D2D",
                selected="#BB86FC",
                disabled="#666666"
            )
        elif template_name == "Material Light":
            self.current_palette = QSSPalette(
                background="#FAFAFA",
                foreground="#212121",
                primary="#6200EE",
                secondary="#03DAC6",
                border="#E0E0E0",
                hover="#F5F5F5",
                selected="#6200EE",
                disabled="#BDBDBD"
            )
        elif template_name == "Flat Dark":
            self.current_palette = QSSPalette(
                background="#2C3E50",
                foreground="#ECF0F1",
                primary="#3498DB",
                secondary="#2ECC71",
                border="#34495E",
                hover="#34495E",
                selected="#3498DB",
                disabled="#7F8C8D"
            )
        elif template_name == "Flat Light":
            self.current_palette = QSSPalette(
                background="#ECF0F1",
                foreground="#2C3E50",
                primary="#3498DB",
                secondary="#2ECC71",
                border="#BDC3C7",
                hover="#E0E0E0",
                selected="#3498DB",
                disabled="#95A5A6"
            )
        else:  # Default
            self._load_default_theme()
            return

        self._update_palette_pickers()
        self._generate_qss_from_palette()
        # Reset unsaved flag after template change
        self.unsaved_changes = False

    # ==================== QSS Operations ====================

    def _generate_qss_from_palette(self):
        """Generate QSS code from current palette"""
        qss = self.current_palette.generate_qss()
        # Block signals to prevent triggering "unsaved changes"
        self.code_editor.blockSignals(True)
        self.code_editor.setPlainText(qss)
        self.code_editor.blockSignals(False)
        self._apply_to_preview()

    def _extract_palette_from_qss(self):
        """Extract color palette from current QSS code"""
        qss_code = self.code_editor.toPlainText()
        if not qss_code.strip():
            QMessageBox.warning(self, "Empty QSS", "No QSS code to extract colors from.")
            return

        # Extract palette
        self.current_palette = QSSPalette.from_qss(qss_code)
        self._update_palette_pickers()

        QMessageBox.information(
            self,
            "Palette Extracted",
            "Color palette has been extracted from QSS code.\n"
            "Adjust colors if needed."
        )

    def _apply_to_preview(self):
        """Apply current QSS to preview"""
        qss_code = self.code_editor.toPlainText()
        self.preview.set_qss(qss_code)

    # ==================== File Operations ====================

    def _new_theme(self):
        """Create new theme"""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Current theme has unsaved changes. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.current_file = None
        self.file_label.setText("No file loaded")
        self._load_default_theme()
        self.unsaved_changes = False

    def _open_theme(self):
        """Open QSS file"""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Current theme has unsaved changes. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open QSS Theme",
            str(self.theme_manager.qss_themes_dir),
            "QSS Files (*.qss);;All Files (*)"
        )

        if filename:
            try:
                palette, qss_code = self.theme_manager.load_qss_theme(filename)
                self.current_palette = palette
                self.current_file = filename
                self.file_label.setText(Path(filename).name)
                self.code_editor.setPlainText(qss_code)
                self._update_palette_pickers()
                self._apply_to_preview()
                self.unsaved_changes = False
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load QSS file:\n{str(e)}")

    def _save_theme(self):
        """Save current theme"""
        if self.current_file:
            try:
                qss_code = self.code_editor.toPlainText()
                self.theme_manager.save_qss_theme(qss_code, self.current_file)
                self.unsaved_changes = False
                QMessageBox.information(self, "Saved", f"Theme saved to {Path(self.current_file).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save QSS file:\n{str(e)}")
        else:
            self._save_theme_as()

    def _save_theme_as(self):
        """Save theme as new file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save QSS Theme As",
            str(self.theme_manager.qss_themes_dir / "theme.qss"),
            "QSS Files (*.qss);;All Files (*)"
        )

        if filename:
            # Ensure .qss extension
            if not filename.endswith('.qss'):
                filename += '.qss'

            try:
                qss_code = self.code_editor.toPlainText()
                self.theme_manager.save_qss_theme(qss_code, filename)
                self.current_file = filename
                self.file_label.setText(Path(filename).name)
                self.unsaved_changes = False
                QMessageBox.information(self, "Saved", f"Theme saved to {Path(filename).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save QSS file:\n{str(e)}")

    # ==================== Public Methods ====================

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.unsaved_changes

    def get_current_qss(self) -> str:
        """Get current QSS code"""
        return self.code_editor.toPlainText()
