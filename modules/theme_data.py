"""
Theme Data Classes
Data structures for different theme formats (Terminal JSON, QSS, CustomTkinter)
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
import re


@dataclass
class TerminalTheme:
    """Terminal color scheme (JSON format) - 20 color properties"""
    name: str
    background: str
    foreground: str
    cursor: str
    selection: str
    black: str
    red: str
    green: str
    yellow: str
    blue: str
    purple: str
    cyan: str
    white: str
    brightBlack: str
    brightRed: str
    brightGreen: str
    brightYellow: str
    brightBlue: str
    brightPurple: str
    brightCyan: str
    brightWhite: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to JSON-serializable dict"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'TerminalTheme':
        """Create from JSON dict"""
        return cls(**data)

    def validate(self) -> tuple[bool, str]:
        """
        Validate all colors are valid hex format
        Returns: (is_valid, error_message)
        """
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')

        for field_name, value in asdict(self).items():
            if field_name == 'name':
                continue
            if not hex_pattern.match(value):
                return False, f"Invalid color format for '{field_name}': {value} (expected #RRGGBB)"

        return True, ""

    @staticmethod
    def normalize_hex(color: str) -> str:
        """
        Normalize hex color to uppercase #RRGGBB format
        Supports: #RGB, #RRGGBB, rgb(r,g,b)
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

        # Return as-is if not recognized
        return color


@dataclass
class QSSPalette:
    """QSS color palette (8 core colors)"""
    background: str = "#FFFFFF"
    foreground: str = "#000000"
    primary: str = "#0078D4"
    secondary: str = "#6C757D"
    border: str = "#CCCCCC"
    hover: str = "#E5E5E5"
    selected: str = "#0078D4"
    disabled: str = "#999999"

    def to_dict(self) -> Dict[str, str]:
        """Convert to JSON-serializable dict"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'QSSPalette':
        """Create from dict"""
        return cls(**data)

    def validate(self) -> tuple[bool, str]:
        """Validate all colors are valid hex format"""
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')

        for field_name, value in asdict(self).items():
            if not hex_pattern.match(value):
                return False, f"Invalid color format for '{field_name}': {value}"

        return True, ""

    @classmethod
    def from_qss(cls, qss_code: str) -> 'QSSPalette':
        """
        Extract palette from QSS code using regex
        Attempts to find the most common colors used
        """
        # Extract all color values from QSS
        hex_pattern = re.compile(r'#[0-9A-Fa-f]{6}\b')
        colors = hex_pattern.findall(qss_code)

        if not colors:
            return cls()  # Return default palette

        # Count color occurrences
        from collections import Counter
        color_counts = Counter(colors)
        most_common = [color.upper() for color, _ in color_counts.most_common(8)]

        # Try to intelligently assign colors based on common patterns
        palette = cls()

        # Look for common background patterns
        bg_match = re.search(r'QWidget\s*\{[^}]*background-color:\s*(#[0-9A-Fa-f]{6})', qss_code)
        if bg_match:
            palette.background = bg_match.group(1).upper()

        # Look for common foreground/color patterns
        fg_match = re.search(r'QWidget\s*\{[^}]*color:\s*(#[0-9A-Fa-f]{6})', qss_code)
        if fg_match:
            palette.foreground = fg_match.group(1).upper()

        # Look for button primary color
        btn_match = re.search(r'QPushButton\s*\{[^}]*background-color:\s*(#[0-9A-Fa-f]{6})', qss_code)
        if btn_match:
            palette.primary = btn_match.group(1).upper()

        # Look for hover color
        hover_match = re.search(r':hover\s*\{[^}]*background-color:\s*(#[0-9A-Fa-f]{6})', qss_code)
        if hover_match:
            palette.hover = hover_match.group(1).upper()

        # Look for selection color
        sel_match = re.search(r'::item:selected\s*\{[^}]*background-color:\s*(#[0-9A-Fa-f]{6})', qss_code)
        if sel_match:
            palette.selected = sel_match.group(1).upper()

        # Look for border color
        border_match = re.search(r'border.*:\s*(#[0-9A-Fa-f]{6})', qss_code)
        if border_match:
            palette.border = border_match.group(1).upper()

        return palette

    def generate_qss(self, template: str = 'default') -> str:
        """
        Generate QSS code from palette
        Templates: 'default', 'material', 'flat', 'classic'
        """
        if template == 'material':
            return self._generate_material_qss()
        elif template == 'flat':
            return self._generate_flat_qss()
        elif template == 'classic':
            return self._generate_classic_qss()
        else:
            return self._generate_default_qss()

    def _generate_default_qss(self) -> str:
        """Generate default QSS stylesheet"""
        return f"""/* Theme Editor - Generated QSS Theme */

/* Main Window and Widgets */
QWidget {{
    background-color: {self.background};
    color: {self.foreground};
    font-size: 10pt;
}}

/* Buttons */
QPushButton {{
    background-color: {self.primary};
    color: {self.background};
    border: 1px solid {self.border};
    border-radius: 4px;
    padding: 5px 15px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {self.hover};
    color: {self.foreground};
}}

QPushButton:pressed {{
    background-color: {self.selected};
    color: {self.background};
}}

QPushButton:disabled {{
    background-color: {self.disabled};
    color: {self.border};
}}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {self.background};
    color: {self.foreground};
    border: 1px solid {self.border};
    border-radius: 3px;
    padding: 4px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {self.primary};
}}

/* ComboBox */
QComboBox {{
    background-color: {self.background};
    color: {self.foreground};
    border: 1px solid {self.border};
    border-radius: 3px;
    padding: 4px;
}}

QComboBox:hover {{
    border: 1px solid {self.primary};
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {self.background};
    color: {self.foreground};
    selection-background-color: {self.selected};
    selection-color: {self.background};
}}

/* SpinBox */
QSpinBox, QDoubleSpinBox {{
    background-color: {self.background};
    color: {self.foreground};
    border: 1px solid {self.border};
    border-radius: 3px;
    padding: 3px;
}}

/* CheckBox and RadioButton */
QCheckBox, QRadioButton {{
    color: {self.foreground};
    spacing: 5px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {self.border};
    background-color: {self.background};
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {self.primary};
}}

/* ProgressBar */
QProgressBar {{
    background-color: {self.background};
    border: 1px solid {self.border};
    border-radius: 3px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {self.primary};
    border-radius: 2px;
}}

/* Slider */
QSlider::groove:horizontal {{
    background: {self.border};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {self.primary};
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

/* List, Tree, Table */
QListWidget, QTreeWidget, QTableWidget {{
    background-color: {self.background};
    color: {self.foreground};
    border: 1px solid {self.border};
    alternate-background-color: {self.hover};
}}

QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
    background-color: {self.selected};
    color: {self.background};
}}

/* TabWidget */
QTabWidget::pane {{
    border: 1px solid {self.border};
    background-color: {self.background};
}}

QTabBar::tab {{
    background-color: {self.hover};
    color: {self.foreground};
    border: 1px solid {self.border};
    padding: 6px 12px;
}}

QTabBar::tab:selected {{
    background-color: {self.primary};
    color: {self.background};
}}

/* GroupBox */
QGroupBox {{
    border: 1px solid {self.border};
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
    color: {self.foreground};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: {self.foreground};
}}

/* MenuBar and Menu */
QMenuBar {{
    background-color: {self.background};
    color: {self.foreground};
}}

QMenuBar::item:selected {{
    background-color: {self.hover};
}}

QMenu {{
    background-color: {self.background};
    color: {self.foreground};
    border: 1px solid {self.border};
}}

QMenu::item:selected {{
    background-color: {self.selected};
    color: {self.background};
}}

/* StatusBar */
QStatusBar {{
    background-color: {self.background};
    color: {self.foreground};
    border-top: 1px solid {self.border};
}}

/* ScrollBar */
QScrollBar:vertical {{
    background: {self.background};
    width: 12px;
    border: 1px solid {self.border};
}}

QScrollBar::handle:vertical {{
    background: {self.primary};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

    def _generate_material_qss(self) -> str:
        """Generate Material Design style QSS"""
        # Simplified - full implementation would be more extensive
        return self._generate_default_qss()

    def _generate_flat_qss(self) -> str:
        """Generate Flat UI style QSS"""
        return self._generate_default_qss()

    def _generate_classic_qss(self) -> str:
        """Generate Classic Windows style QSS"""
        return self._generate_default_qss()


@dataclass
class CustomTkinterTheme:
    """CustomTkinter theme structure with light/dark mode support"""
    name: str
    theme_data: Dict[str, Any] = field(default_factory=dict)

    # Common color properties (extracted for easy editing)
    primary_color: List[str] = field(default_factory=lambda: ["#3B8ED0", "#1F6AA5"])
    secondary_color: List[str] = field(default_factory=lambda: ["#5FB878", "#4A9960"])
    background_color: List[str] = field(default_factory=lambda: ["gray92", "gray14"])
    text_color: List[str] = field(default_factory=lambda: ["gray10", "#DCE4EE"])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        if self.theme_data:
            return self.theme_data

        # Generate default theme structure
        return {
            "CTk": {
                "fg_color": self.background_color
            },
            "CTkButton": {
                "fg_color": self.primary_color,
                "hover_color": self.secondary_color,
                "text_color": ["gray98", "#DCE4EE"]
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], name: str) -> 'CustomTkinterTheme':
        """Create from JSON dict"""
        theme = cls(name=name, theme_data=data)

        # Extract common colors if available
        if "CTkButton" in data:
            btn = data["CTkButton"]
            if "fg_color" in btn:
                theme.primary_color = btn["fg_color"]
            if "hover_color" in btn:
                theme.secondary_color = btn["hover_color"]

        if "CTk" in data:
            if "fg_color" in data["CTk"]:
                theme.background_color = data["CTk"]["fg_color"]

        return theme

    def extract_colors(self) -> Dict[str, List[str]]:
        """Extract all unique colors used in theme"""
        colors = {}

        def extract_from_dict(d: dict, prefix: str = ""):
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, list) and len(value) == 2:
                    # Likely a [light, dark] color pair
                    if all(isinstance(v, str) for v in value):
                        colors[full_key] = value
                elif isinstance(value, dict):
                    extract_from_dict(value, full_key)

        extract_from_dict(self.theme_data)
        return colors

    def apply_color_scheme(self, color_map: Dict[str, List[str]]):
        """Apply color scheme to theme data"""
        def update_dict(d: dict, prefix: str = ""):
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if full_key in color_map:
                    d[key] = color_map[full_key]
                elif isinstance(value, dict):
                    update_dict(value, full_key)

        update_dict(self.theme_data)
