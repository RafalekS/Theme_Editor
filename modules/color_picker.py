"""
Color Picker Widget
Enhanced color picker button with multiple input methods and validation
"""

from PyQt6.QtWidgets import QPushButton, QColorDialog, QMenu, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QAction, QCursor
import re


class ColorPickerButton(QPushButton):
    """
    Enhanced color picker button with multiple features:
    - Click to open QColorDialog
    - Display current color as background
    - Show hex value as text
    - Right-click context menu for copy/paste
    - Hover tooltip with RGB/HSL values
    - Color validation
    """

    # Signal emitted when color changes
    colorChanged = pyqtSignal(str)  # Emits hex color (#RRGGBB)

    def __init__(self, color: str = "#000000", label: str = "", parent=None):
        """
        Initialize ColorPickerButton

        Args:
            color: Initial hex color (#RRGGBB)
            label: Optional label to display instead of hex value
            parent: Parent widget
        """
        super().__init__(parent)
        self.color = self._normalize_color(color)
        self.label = label
        # Larger, more visible color picker button
        self.setMinimumSize(120, 32)
        self.setMaximumHeight(32)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.clicked.connect(self._choose_color)
        self._update_display()

    def _normalize_color(self, color: str) -> str:
        """
        Normalize color to uppercase #RRGGBB format

        Args:
            color: Color string (various formats supported)

        Returns:
            Normalized hex color (#RRGGBB)
        """
        color = color.strip().upper()

        # Handle #RGB shorthand
        if re.match(r'^#[0-9A-F]{3}$', color):
            r, g, b = color[1], color[2], color[3]
            return f"#{r}{r}{g}{g}{b}{b}"

        # Handle #RRGGBB
        if re.match(r'^#[0-9A-F]{6}$', color):
            return color

        # Handle rgb(r, g, b)
        rgb_match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color.lower())
        if rgb_match:
            r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
            return f"#{r:02X}{g:02X}{b:02X}"

        # Default to black if invalid
        return "#000000"

    def _update_display(self):
        """Update button appearance with current color"""
        # Calculate text color (black or white) based on background luminance
        text_color = self._get_contrast_color()

        # Display label or hex value
        display_text = self.label if self.label else self.color

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: {text_color};
                border: 2px solid #999;
                border-radius: 3px;
                font-weight: bold;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                border: 2px solid #333;
            }}
        """)
        self.setText(display_text)

        # Update tooltip with color details
        rgb = self._hex_to_rgb(self.color)
        hsl = self._rgb_to_hsl(*rgb)
        tooltip = f"Hex: {self.color}\nRGB: rgb({rgb[0]}, {rgb[1]}, {rgb[2]})\nHSL: hsl({hsl[0]}°, {hsl[1]}%, {hsl[2]}%)"
        self.setToolTip(tooltip)

    def _get_contrast_color(self) -> str:
        """
        Get contrasting text color (black or white) based on background

        Returns:
            '#FFFFFF' or '#000000'
        """
        r, g, b = self._hex_to_rgb(self.color)

        # Calculate relative luminance (ITU-R BT.709)
        luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

        # Return black for light backgrounds, white for dark backgrounds
        return '#000000' if luminance > 0.5 else '#FFFFFF'

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hsl(self, r: int, g: int, b: int) -> tuple[int, int, int]:
        """
        Convert RGB to HSL

        Returns:
            Tuple of (hue[0-360], saturation[0-100], lightness[0-100])
        """
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2

        if max_c == min_c:
            h = s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)

            if max_c == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_c == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4

            h /= 6

        return (int(h * 360), int(s * 100), int(l * 100))

    def _choose_color(self):
        """Open color picker dialog"""
        initial_color = QColor(self.color)
        color = QColorDialog.getColor(initial_color, self, "Choose Color")

        if color.isValid():
            new_color = color.name().upper()
            if new_color != self.color:
                self.set_color(new_color)

    def _show_context_menu(self, position):
        """Show right-click context menu"""
        menu = QMenu(self)

        # Copy hex value
        copy_hex_action = QAction("Copy Hex", self)
        copy_hex_action.triggered.connect(lambda: self._copy_to_clipboard(self.color))
        menu.addAction(copy_hex_action)

        # Copy RGB value
        rgb = self._hex_to_rgb(self.color)
        rgb_str = f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
        copy_rgb_action = QAction("Copy RGB", self)
        copy_rgb_action.triggered.connect(lambda: self._copy_to_clipboard(rgb_str))
        menu.addAction(copy_rgb_action)

        menu.addSeparator()

        # Paste color
        paste_action = QAction("Paste Color", self)
        paste_action.triggered.connect(self._paste_color)
        menu.addAction(paste_action)

        # Enter hex manually
        enter_action = QAction("Enter Hex Value...", self)
        enter_action.triggered.connect(self._enter_hex_manually)
        menu.addAction(enter_action)

        menu.exec(QCursor.pos())

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _paste_color(self):
        """Paste color from clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()

        if text:
            try:
                normalized = self._normalize_color(text)
                if self._is_valid_hex(normalized):
                    self.set_color(normalized)
                else:
                    QMessageBox.warning(self, "Invalid Color", f"Could not parse color: {text}")
            except Exception as e:
                QMessageBox.warning(self, "Invalid Color", f"Error parsing color: {e}")

    def _enter_hex_manually(self):
        """Enter hex color value manually via dialog"""
        text, ok = QInputDialog.getText(
            self,
            "Enter Hex Color",
            "Enter hex color value (e.g., #RRGGBB):",
            text=self.color
        )

        if ok and text:
            try:
                normalized = self._normalize_color(text)
                if self._is_valid_hex(normalized):
                    self.set_color(normalized)
                else:
                    QMessageBox.warning(self, "Invalid Color", f"Invalid hex color format: {text}")
            except Exception as e:
                QMessageBox.warning(self, "Invalid Color", f"Error parsing color: {e}")

    def _is_valid_hex(self, color: str) -> bool:
        """Validate hex color format"""
        return bool(re.match(r'^#[0-9A-F]{6}$', color))

    def set_color(self, color: str):
        """
        Set button color programmatically

        Args:
            color: Hex color string
        """
        normalized = self._normalize_color(color)
        if normalized != self.color:
            self.color = normalized
            self._update_display()
            self.colorChanged.emit(self.color)

    def get_color(self) -> str:
        """
        Get current color

        Returns:
            Hex color string (#RRGGBB)
        """
        return self.color

    def set_label(self, label: str):
        """
        Set button label (displayed instead of hex value)

        Args:
            label: Label text
        """
        self.label = label
        self._update_display()
