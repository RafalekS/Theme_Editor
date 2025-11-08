"""
Theme Converter UI
User interface for converting themes between different formats
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QMessageBox, QComboBox, QTextEdit,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
from .theme_manager import ThemeManager
from .theme_converter import ThemeConverter
from .theme_data import TerminalTheme, QSSPalette


class ConverterUI(QWidget):
    """
    Theme Converter User Interface
    Convert between Terminal JSON, QSS, CustomTkinter, and Windows Terminal formats
    """

    # Signal emitted when conversion is complete
    conversionComplete = pyqtSignal(str)  # Emits format name

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.converter = ThemeConverter()

        # Loaded themes
        self.terminal_themes = {}
        self.current_source_theme = None

        self._setup_ui()
        self._load_available_themes()

    def _setup_ui(self):
        """Setup converter UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("Theme Converter")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = QLabel("Convert themes between different formats: Terminal JSON ↔ QSS ↔ CustomTkinter ↔ Windows Terminal")
        desc.setStyleSheet("font-size: 9pt; color: #666;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(5)

        # Conversion panel
        conversion_panel = self._create_conversion_panel()
        layout.addWidget(conversion_panel)

        layout.addSpacing(20)

        # Output preview
        output_group = QGroupBox("Conversion Output")
        output_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12pt; }")
        output_layout = QVBoxLayout(output_group)

        self.output_preview = QTextEdit()
        self.output_preview.setFont(QFont("Consolas", 10))
        self.output_preview.setReadOnly(True)
        self.output_preview.setPlaceholderText(
            "Conversion output will appear here...\n\n"
            "Select source format, choose a theme, select target format,\n"
            "and click 'Convert' to see the result."
        )
        output_layout.addWidget(self.output_preview)

        # Export button
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self.export_btn = QPushButton("Export to File...")
        self.export_btn.setStyleSheet("font-weight: bold; padding: 8px 20px;")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._export_result)
        export_layout.addWidget(self.export_btn)

        output_layout.addLayout(export_layout)
        layout.addWidget(output_group)

    def _create_conversion_panel(self) -> QGroupBox:
        """Create conversion selection panel"""
        panel = QGroupBox("Conversion Settings")
        panel.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12pt; }")
        grid = QGridLayout(panel)
        grid.setSpacing(15)

        # Source format
        grid.addWidget(QLabel("Source Format:"), 0, 0)
        self.source_format_combo = QComboBox()
        self.source_format_combo.addItems([
            "Terminal JSON",
            "QSS (Qt Style Sheets)",
            "CustomTkinter (Coming Soon)",
            "Windows Terminal (Coming Soon)"
        ])
        self.source_format_combo.currentTextChanged.connect(self._on_source_format_changed)
        grid.addWidget(self.source_format_combo, 0, 1)

        # Source theme selector
        grid.addWidget(QLabel("Select Theme:"), 1, 0)
        self.source_theme_combo = QComboBox()
        self.source_theme_combo.setMinimumWidth(300)
        grid.addWidget(self.source_theme_combo, 1, 1)

        # OR load from file
        self.load_file_btn = QPushButton("Load from File...")
        self.load_file_btn.clicked.connect(self._load_from_file)
        grid.addWidget(self.load_file_btn, 1, 2)

        # Spacer
        spacer = QLabel("→")
        spacer.setStyleSheet("font-size: 24pt; font-weight: bold; color: #0078D4;")
        spacer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(spacer, 2, 0, 1, 3)

        # Target format
        grid.addWidget(QLabel("Target Format:"), 3, 0)
        self.target_format_combo = QComboBox()
        self.target_format_combo.addItems([
            "QSS (Qt Style Sheets)",
            "Terminal JSON",
            "CustomTkinter (Coming Soon)",
            "Windows Terminal (Coming Soon)"
        ])
        grid.addWidget(self.target_format_combo, 3, 1)

        # Target theme name
        grid.addWidget(QLabel("Theme Name:"), 4, 0)
        from PyQt6.QtWidgets import QLineEdit
        self.theme_name_input = QLineEdit()
        self.theme_name_input.setPlaceholderText("Enter name for converted theme...")
        grid.addWidget(self.theme_name_input, 4, 1, 1, 2)

        # Convert button
        convert_layout = QHBoxLayout()
        convert_layout.addStretch()

        self.convert_btn = QPushButton("🔄 Convert Theme")
        self.convert_btn.setStyleSheet(
            "font-weight: bold; font-size: 14pt; padding: 12px 30px; "
            "background-color: #0078D4; color: white; border-radius: 5px;"
        )
        self.convert_btn.clicked.connect(self._convert_theme)
        convert_layout.addWidget(self.convert_btn)

        convert_layout.addStretch()
        grid.addLayout(convert_layout, 5, 0, 1, 3)

        return panel

    def _load_available_themes(self):
        """Load available themes from theme manager"""
        # Load terminal themes
        self.terminal_themes = self.theme_manager.load_json_themes()
        self._update_source_theme_list()

    def _update_source_theme_list(self):
        """Update source theme list based on selected format"""
        source_format = self.source_format_combo.currentText()

        self.source_theme_combo.clear()

        if "Terminal JSON" in source_format:
            self.source_theme_combo.addItems(sorted(self.terminal_themes.keys()))
        elif "QSS" in source_format:
            # List QSS files
            qss_themes = self.theme_manager.get_qss_theme_list()
            self.source_theme_combo.addItems(qss_themes)
        else:
            self.source_theme_combo.addItem("(Not yet supported)")

    def _on_source_format_changed(self):
        """Handle source format change"""
        self._update_source_theme_list()

    def _load_from_file(self):
        """Load theme from file"""
        source_format = self.source_format_combo.currentText()

        if "Terminal JSON" in source_format:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Load Terminal JSON Theme",
                str(self.theme_manager.themes_dir),
                "JSON Files (*.json);;All Files (*)"
            )
            if filename:
                # Load and add to list
                themes = self.theme_manager.load_json_themes(filename)
                self.terminal_themes.update(themes)
                self._update_source_theme_list()
                QMessageBox.information(self, "Loaded", f"Loaded {len(themes)} theme(s)")

        elif "QSS" in source_format:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Load QSS Theme",
                str(self.theme_manager.qss_themes_dir),
                "QSS Files (*.qss);;All Files (*)"
            )
            if filename:
                self.source_theme_combo.addItem(Path(filename).name)
                self.source_theme_combo.setCurrentText(Path(filename).name)

    def _convert_theme(self):
        """Perform theme conversion"""
        source_format = self.source_format_combo.currentText()
        target_format = self.target_format_combo.currentText()
        theme_name = self.theme_name_input.text() or "Converted Theme"

        # Check if formats are supported
        if "Coming Soon" in source_format or "Coming Soon" in target_format:
            QMessageBox.warning(
                self,
                "Not Supported",
                "This conversion is not yet supported.\n"
                "Currently supported:\n"
                "• Terminal JSON → QSS\n"
                "• QSS → Terminal JSON"
            )
            return

        # Get source theme
        source_theme_name = self.source_theme_combo.currentText()
        if not source_theme_name:
            QMessageBox.warning(self, "No Theme", "Please select a source theme.")
            return

        try:
            # Perform conversion
            result = None

            if "Terminal JSON" in source_format and "QSS" in target_format:
                # Terminal → QSS
                terminal_theme = self.terminal_themes[source_theme_name]
                palette, qss_code = self.converter.terminal_to_qss(terminal_theme, theme_name)
                self.output_preview.setPlainText(qss_code)
                self.current_source_theme = ("qss", qss_code)
                self.export_btn.setEnabled(True)
                result = f"Successfully converted '{source_theme_name}' to QSS"

            elif "QSS" in source_format and "Terminal JSON" in target_format:
                # QSS → Terminal
                qss_file = self.theme_manager.qss_themes_dir / source_theme_name
                palette, qss_code = self.theme_manager.load_qss_theme(qss_file)
                terminal_theme = self.converter.qss_to_terminal(palette, theme_name)

                # Show as JSON
                import json
                json_output = json.dumps(terminal_theme.to_dict(), indent=2)
                self.output_preview.setPlainText(json_output)
                self.current_source_theme = ("terminal", terminal_theme)
                self.export_btn.setEnabled(True)
                result = f"Successfully converted '{source_theme_name}' to Terminal JSON"

            if result:
                self.conversionComplete.emit(target_format)
                QMessageBox.information(self, "Conversion Complete", result)

        except Exception as e:
            QMessageBox.critical(self, "Conversion Error", f"Failed to convert theme:\n{str(e)}")

    def _export_result(self):
        """Export conversion result to file"""
        if not self.current_source_theme:
            QMessageBox.warning(self, "No Result", "No conversion result to export.")
            return

        format_type, data = self.current_source_theme

        if format_type == "qss":
            # Export QSS
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export QSS Theme",
                str(self.theme_manager.qss_themes_dir / "converted.qss"),
                "QSS Files (*.qss);;All Files (*)"
            )
            if filename:
                if not filename.endswith('.qss'):
                    filename += '.qss'
                self.theme_manager.save_qss_theme(data, filename, backup=False)
                QMessageBox.information(self, "Exported", f"Saved to:\n{filename}")

        elif format_type == "terminal":
            # Export Terminal JSON
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Terminal Theme",
                str(self.theme_manager.themes_dir / "converted.json"),
                "JSON Files (*.json);;All Files (*)"
            )
            if filename:
                if not filename.endswith('.json'):
                    filename += '.json'

                import json
                themes_dict = {data.name: data.to_dict()}

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(themes_dict, f, indent=2)

                QMessageBox.information(self, "Exported", f"Saved to:\n{filename}")
