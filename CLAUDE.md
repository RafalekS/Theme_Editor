# Theme Editor - Project Requirements Document

## Project Overview

**Project Name:** Theme_Editor
**Type:** Standalone PyQt6 GUI Application
**Purpose:** Universal theme editor supporting multiple theme formats (JSON terminal themes, Windows Terminal themes, QSS themes, CustomTkinter themes) with integrated image converter utility for icon creation

This is a **completely separate project** from SAP_Security_DB. It should be developed in its own repository with its own dependencies and documentation.

---

## Git Repository Setup

### Initial Repository Creation

```bash
# On GitHub/GitLab - create new empty repository named: Theme_Editor

# Local setup
mkdir Theme_Editor
cd Theme_Editor
git init
git remote add origin <your-repo-url>

# Create initial structure
mkdir -p config/themes
mkdir -p config/qss_themes
mkdir -p modules
mkdir -p help
touch README.md
touch requirements.txt
touch main.py

# First commit
git add .
git commit -m "Initial commit: Theme Editor project structure"
git push -u origin main
```

### Project Folder Structure

```
Theme_Editor/
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore file
│
├── assets/                      # Application icons and theme examples
│   ├── theme_editor_dark.ico    # Dark theme application icon
│   ├── theme_editor_dark.png    # Dark theme application icon (PNG)
│   ├── theme_editor_dark_solid.ico
│   ├── theme_editor_dark_solid.png
│   ├── theme_editor_light.ico   # Light theme application icon
│   ├── theme_editor_light.png   # Light theme application icon (PNG)
│   ├── theme_editor_light_solid.ico
│   └── theme_editor_light_solid.png
│
├── modules/                     # Core application modules
│   ├── __init__.py
│   ├── json_theme_editor.py     # JSON terminal themes editor
│   ├── qss_theme_editor.py      # QSS themes editor (based on existing code)
│   ├── ctk_theme_editor.py      # CustomTkinter themes editor
│   ├── theme_converter.py       # Convert between formats
│   ├── image_converter.py       # Image converter utility (PyQt6)
│   ├── color_picker.py          # Reusable color picker widget
│   └── preview_widgets.py       # Theme preview components
│
├── config/                      # Configuration and theme storage
│   ├── config.json              # Application settings
│   ├── templates/               # Example theme templates from other projects
│   │   ├── template_dark.qss    # Example QSS dark theme (from JSON-Template-Combiner)
│   │   ├── template_green.json  # Example CustomTkinter theme
│   │   ├── template_themes.json # 60+ terminal themes (STARTING POINT for terminal themes)
│   │   └── template_wt_settings.json  # Example Windows Terminal settings.json
│   ├── themes/                  # User's JSON terminal themes storage
│   │   └── themes.json          # Active themes file (copied from template_themes.json)
│   └── qss_themes/              # User's QSS theme files storage
│       └── default.qss          # Default QSS theme
│
├── help/                        # Documentation
│   ├── README.md                # User documentation
│   ├── REQUIREMENTS.md          # Duplicate of CLAUDE.md
│   └── TODO.md                  # Progress tracking
│
├── backup/                      # Automatic backups of theme files
│
├── logs/                        # Application logs
│
└── tools/                       # Reference tools and utilities
    ├── theme_editor.py          # Original QSS theme editor (reference)
    └── img_conv/                # Image converter (TO BE REFACTORED to PyQt6)
        ├── img_conv.pyw         # Current CustomTkinter implementation
        └── config/
            └── settings.json    # Image converter settings
```

---

## Supported Theme Formats

### 1. JSON Terminal Themes (Primary Format)

**File Format:** Single JSON file containing multiple themes

**Structure:**
```json
{
  "Theme Name": {
    "name": "Theme Name",
    "background": "#RRGGBB",
    "foreground": "#RRGGBB",
    "black": "#RRGGBB",
    "red": "#RRGGBB",
    "green": "#RRGGBB",
    "yellow": "#RRGGBB",
    "blue": "#RRGGBB",
    "purple": "#RRGGBB",
    "cyan": "#RRGGBB",
    "white": "#RRGGBB",
    "brightBlack": "#RRGGBB",
    "brightRed": "#RRGGBB",
    "brightGreen": "#RRGGBB",
    "brightYellow": "#RRGGBB",
    "brightBlue": "#RRGGBB",
    "brightPurple": "#RRGGBB",
    "brightCyan": "#RRGGBB",
    "brightWhite": "#RRGGBB",
    "cursor": "#RRGGBB",
    "selection": "#RRGGBB"
  }
}
```

**Color Properties (20 total):**
- `name` - Theme display name
- `background` - Terminal background
- `foreground` - Default text color
- `cursor` - Cursor color
- `selection` - Selection highlight color
- ANSI colors: `black`, `red`, `green`, `yellow`, `blue`, `purple`, `cyan`, `white`
- Bright ANSI colors: `brightBlack`, `brightRed`, `brightGreen`, `brightYellow`, `brightBlue`, `brightPurple`, `brightCyan`, `brightWhite`

**Use Cases:**
- Terminal emulators
- CLI tools with color output
- Standalone JSON theme files

---

### 2. Windows Terminal Themes

**File Format:** Embedded in `settings.json` under `schemes` array

**Structure:**
```json
{
  "profiles": { ... },
  "schemes": [
    {
      "name": "Theme Name",
      "background": "#RRGGBB",
      "foreground": "#RRGGBB",
      "black": "#RRGGBB",
      // ... same properties as JSON Terminal Themes
    }
  ],
  "actions": [ ... ]
}
```

**Key Differences:**
- Themes are in `schemes` array within larger settings file
- Must preserve other sections when editing (`profiles`, `actions`, etc.)
- No duplicate theme names allowed

**Use Cases:**
- Windows Terminal application
- Extract themes from Windows Terminal to standalone JSON
- Import standalone themes into Windows Terminal

---

### 3. QSS Themes (Qt Style Sheets)

**File Format:** Individual `.qss` files (one per theme)

**Structure:**
```css
/* QSS uses CSS-like syntax for styling Qt widgets */
QWidget {
    background-color: #RRGGBB;
    color: #RRGGBB;
}

QPushButton {
    background-color: #RRGGBB;
    border: 1px solid #RRGGBB;
    border-radius: 4px;
    padding: 5px;
}

QPushButton:hover {
    background-color: #RRGGBB;
}

/* ... more widget styles ... */
```

**Color Palette (8 core colors):**
1. `background` - Main background color
2. `foreground` - Main text color
3. `primary` - Primary accent color
4. `secondary` - Secondary accent color
5. `border` - Border color
6. `hover` - Hover state color
7. `selected` - Selection color
8. `disabled` - Disabled state color

**Use Cases:**
- PyQt6/PyQt5/PySide6 applications
- Qt-based desktop applications
- Visual theme customization

---

### 4. CustomTkinter Themes

**File Format:** Individual `.json` files (one per theme)

**Structure:**
```json
{
  "CTk": {
    "fg_color": ["gray92", "gray14"]
  },
  "CTkButton": {
    "corner_radius": 6,
    "border_width": 0,
    "fg_color": ["#2CC985", "#2FA572"],
    "hover_color": ["#0C955A", "#106A43"],
    "border_color": ["#3E454A", "#949A9F"],
    "text_color": ["gray98", "#DCE4EE"],
    "text_color_disabled": ["gray78", "gray68"]
  },
  "CTkEntry": {
    "corner_radius": 6,
    "border_width": 2,
    "fg_color": ["#F9F9FA", "#343638"],
    "border_color": ["#979DA2", "#565B5E"],
    "text_color": ["gray10", "#DCE4EE"],
    "placeholder_text_color": ["gray52", "gray62"]
  },
  "CTkFont": {
    "Windows": {
      "family": "Roboto",
      "size": 13,
      "weight": "normal"
    }
  }
  /* ... more widget definitions ... */
}
```

**Key Features:**
- Color arrays: `[light_mode_color, dark_mode_color]`
- Widget-specific styling (CTkButton, CTkEntry, CTkLabel, etc.)
- Corner radius and border width settings
- Font definitions per platform (Windows, macOS, Linux)
- Supports named colors (e.g., "gray92") and hex colors (e.g., "#2CC985")

**Color Properties (widget-dependent):**
- `fg_color` - Foreground/background color [light, dark]
- `hover_color` - Hover state color
- `border_color` - Border color
- `text_color` - Text color
- `button_color` - Button/handle color
- `progress_color` - Progress bar fill color
- `selected_color` - Selected state color
- Platform-specific font settings

**Use Cases:**
- CustomTkinter Python applications
- Modern-looking Tkinter GUIs
- Cross-platform Python desktop apps
- Applications requiring light/dark mode switching

---

## Existing Theme Editor Reference

**Source:** tools\theme_editor.py

**Key Components to Reuse:**

### 1. ColorButton Widget
```python
class ColorButton(QPushButton):
    """Custom button for color selection"""
    - Fixed size (40x30)
    - Displays current color as background
    - Opens QColorDialog on click
    - Returns hex color value (#RRGGBB)
```

### 2. ThemePreviewWidget
```python
class ThemePreviewWidget(QWidget):
    """Live preview panel showing theme applied to sample widgets"""
    - QPushButton (normal, disabled)
    - QLineEdit, QTextEdit
    - QComboBox, QSpinBox
    - QCheckBox, QRadioButton
    - QProgressBar
    - QListWidget
    - QTabWidget
    - Real-time stylesheet updates
```

### 3. QSS Generation
- Template-based QSS generation from color palette
- Comprehensive widget coverage (400+ lines)
- Automatic color interpolation for gradients
- State-specific styling (normal, hover, pressed, disabled, focus)

### 4. File Operations
- Load existing `.qss` files
- Extract colors from QSS using regex
- Save themes with `.qss` extension
- "Save As" functionality

---

## Application Assets

### assets/ Folder

**Purpose:**
- Store application icons (both for the app window and as theme examples)
- Provide multiple icon variants for different UI themes

**Contents:**
- `theme_editor_dark.ico/png` - Dark theme application icon (transparent background)
- `theme_editor_dark_solid.ico/png` - Dark theme icon (solid background)
- `theme_editor_light.ico/png` - Light theme application icon (transparent background)
- `theme_editor_light_solid.ico/png` - Light theme icon (solid background)

**Icon Specifications:**
- `.ico` files contain multiple sizes: 32x32, 128x128, 256x256
- `.png` files are high-resolution source images
- Can be created/edited using the integrated Image Converter utility

---

## Configuration Templates

### config/templates/ Folder

**Purpose:**
- Provide example theme files from other projects
- Serve as starting points for new themes
- Reference implementations for different formats

**Contents:**

#### template_dark.qss
- **Source:** JSON-Template-Combiner project
- **Type:** Complete QSS dark theme
- **Usage:** Reference example for QSS theme structure
- **Features:** 345 lines of comprehensive widget styling

#### template_green.json
- **Source:** Custom project
- **Type:** CustomTkinter theme file
- **Usage:** Example CustomTkinter theme implementation
- **Features:** Green accent colors, light/dark mode support

#### template_themes.json ⭐ **IMPORTANT**
- **Source:** SAP_Security_DB project
- **Type:** Collection of 60+ terminal themes
- **Usage:** **STARTING POINT** for terminal theme editor
- **Action:** Copy this to `config/themes/themes.json` on first run
- **Themes included:** GruvboxDark, catppuccin-mocha, GitHub Dark, nord-light, OceanicMaterial, cyberpunk, matrix, and 50+ more

#### template_wt_settings.json
- **Source:** User's Windows Terminal configuration
- **Type:** Complete Windows Terminal settings.json example
- **Usage:** Reference for Windows Terminal integration
- **Features:** Full settings structure with profiles, schemes, actions, keybindings

**Implementation Notes:**
- Templates are read-only references
- Users work with copies in their respective folders (config/themes/, config/qss_themes/)
- Application should check if config/themes/themes.json exists; if not, copy from template_themes.json

---

## Integrated Image Converter Utility

### Current Implementation: tools/img_conv/img_conv.pyw

**Status:** ⚠️ **TO BE REFACTORED TO PyQt6**

**Current Technology Stack:**
- CustomTkinter (modern Tkinter wrapper)
- PIL/Pillow (image processing)
- tkinterdnd2 (drag and drop support)
- cairosvg (optional SVG support)

**Features:**
- GUI and CLI modes
- Drag and drop image support
- Convert between formats: ICO, JPEG, PNG, BMP, GIF, WebP, PPM, PGM, PNM, TIFF, SVG
- Batch conversion
- Quality settings for lossy formats
- Multi-size ICO generation (32x32, 128x128, 256x256)
- Recent files list
- Right-click context menu integration (Windows)

**Refactoring Goals:**
1. **Convert to PyQt6** - Replace CustomTkinter with PyQt6 for consistency
2. **Integrate as module** - Move to `modules/image_converter.py` for reusability
3. **Maintain CLI support** - Keep command-line functionality
4. **Improve UI** - Match Theme Editor's visual style
5. **Add features:**
   - Live image preview
   - Resize/crop capabilities
   - Batch rename
   - Image metadata editor
   - Color palette extraction (useful for theme creation)
   - Export theme colors from image

**Integration Points:**
- Accessible from Tools menu in main application
- Can be launched as standalone utility
- Used for creating/editing application icons
- Extract color palettes from images to create themes

---

## New Features to Implement

### 1. Multi-Format Support

**Unified Interface:**
- Tab-based UI with separate editors for each format:
  - Tab 1: JSON Terminal Themes
  - Tab 2: Windows Terminal Integration
  - Tab 3: QSS Themes
  - Tab 4: CustomTkinter Themes
  - Tab 5: Theme Converter (converts between all formats)

**Format Conversion:**
- Convert terminal themes → QSS (map ANSI colors to UI elements)
- Convert terminal themes → CustomTkinter (map ANSI colors to CTk widgets)
- Convert QSS → terminal themes (extract and map colors)
- Convert CustomTkinter → terminal themes (extract and map colors)
- Export terminal themes to Windows Terminal format
- Import Windows Terminal themes to standalone JSON
- Cross-format color palette extraction

---

### 2. JSON Terminal Theme Editor

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Theme Selector [Dropdown ▼]  [New] [Duplicate] [Delete]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Color Palette (20 colors in grid):                        │
│  ┌──────────────┬──────────────┬──────────────┐           │
│  │ Background   │ Foreground   │ Cursor       │  [#RRGGBB]│
│  ├──────────────┼──────────────┼──────────────┤           │
│  │ Selection    │ Black        │ Red          │           │
│  ├──────────────┼──────────────┼──────────────┤           │
│  │ Green        │ Yellow       │ Blue         │           │
│  └──────────────┴──────────────┴──────────────┘           │
│                                                             │
│  [Preview Terminal Output]                                 │
│  ┌───────────────────────────────────────────────────┐    │
│  │ $ ls -la                                           │    │
│  │ drwxr-xr-x  5 user user 4096 Nov  8 12:00 .       │    │
│  │ drwxr-xr-x 23 user user 4096 Nov  7 18:30 ..      │    │
│  │ -rw-r--r--  1 user user  220 Nov  1 09:15 .bashrc │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  [Save Theme]  [Export to Windows Terminal]                │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Load `themes.json` containing multiple themes
- Select theme from dropdown
- Edit all 20 color properties with color pickers
- Real-time preview showing colored terminal output
- Create new themes (duplicate existing or start blank)
- Delete themes (with confirmation)
- Rename themes
- Export single theme or all themes
- Import themes from other JSON files
- Validate hex color format
- Undo/Redo support

**Preview Content:**
- Sample terminal commands with syntax highlighting
- Directory listings (different colors for files, dirs, executables)
- Git status output
- Error messages (red)
- Success messages (green)
- Warning messages (yellow)
- All colors visible

---

### 3. Windows Terminal Integration

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Windows Terminal settings.json Path:                       │
│  [C:\Users\...\AppData\Local\...\settings.json] [Browse]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Available Themes in settings.json:                        │
│  ┌──────────────────────────────────────────────┐         │
│  │ ○ Campbell                                    │         │
│  │ ○ One Half Dark                              │         │
│  │ ● Gruvbox Dark (currently editing)           │         │
│  │ ○ Nord                                        │         │
│  └──────────────────────────────────────────────┘         │
│                                                             │
│  [Edit Selected]  [Add New]  [Delete]  [Import from JSON] │
│                                                             │
│  Color Editor (same as JSON Terminal Theme Editor)         │
│                                                             │
│  [Save to settings.json]  [Export to Standalone JSON]      │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Detect Windows Terminal installation automatically
- Browse for custom `settings.json` location
- Parse `settings.json` safely (preserve all other settings)
- List all themes in `schemes` array
- Edit selected theme inline
- Add new themes to schemes
- Delete themes from schemes
- Backup `settings.json` before saving
- Validate JSON structure before writing
- Export theme to standalone JSON file
- Import themes from standalone JSON to Windows Terminal
- Detect theme name conflicts

**Safety Features:**
- **CRITICAL:** Always backup settings.json before modifying
- Validate JSON structure before saving
- Preserve formatting/comments if possible
- Show diff before applying changes
- Rollback on error

---

### 4. QSS Theme Editor (Enhanced)

**Based on existing editor with improvements:**

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  QSS Theme: [default.qss ▼]  [New] [Open] [Save] [Save As]│
├──────────────────┬──────────────────────────────────────────┤
│  Color Palette   │  Live Preview                            │
│                  │                                          │
│  Background  ■   │  ┌────────────────────────────────┐     │
│  Foreground  ■   │  │ [Button] [Disabled Button]     │     │
│  Primary     ■   │  │                                │     │
│  Secondary   ■   │  │ Input: [___________]           │     │
│  Border      ■   │  │                                │     │
│  Hover       ■   │  │ ☑ Checkbox  ○ Radio            │     │
│  Selected    ■   │  │                                │     │
│  Disabled    ■   │  │ Progress: ████░░░░░░ 40%      │     │
│                  │  └────────────────────────────────┘     │
│  [Generate QSS]  │                                          │
│                  │  QSS Code Editor:                        │
├──────────────────┤  ┌────────────────────────────────┐     │
│                  │  │ QWidget {                      │     │
│                  │  │   background-color: #282828;   │     │
│                  │  │   color: #EBDBB2;              │     │
│                  │  │ }                              │     │
│                  │  │                                │     │
│                  │  │ QPushButton {                  │     │
│                  │  │   background-color: #458588;   │     │
│                  │  │   ...                          │     │
│                  │  └────────────────────────────────┘     │
│                  │                                          │
│                  │  [Apply to Preview]                     │
└──────────────────┴──────────────────────────────────────────┘
```

**Enhanced Features:**
- Color palette editor (8 core colors)
- Auto-generate comprehensive QSS from palette
- Manual QSS code editor with syntax highlighting
- Real-time preview on sample widgets
- Load existing .qss files
- Extract colors from loaded QSS (regex-based)
- Save/Save As functionality
- Recent files list
- QSS template library (Material, Flat, Classic, etc.)
- Color scheme presets
- Export color palette as JSON

**QSS Generation Templates:**
- Material Design style
- Flat UI style
- Classic Windows style
- macOS style
- Custom (user-editable template)

---

### 5. Theme Converter

**Conversions Supported:**

#### Terminal JSON → QSS
```
Mapping:
- background      → QWidget background-color
- foreground      → QWidget color
- blue            → QPushButton background (primary)
- brightBlue      → QPushButton:hover background
- green           → success state colors
- red             → error state colors
- selection       → selected item background
- cursor          → focus indicator color
```

#### QSS → Terminal JSON
```
Extract:
- Main background → background
- Main foreground → foreground
- Primary color   → blue
- Secondary color → cyan
- Success color   → green
- Error color     → red
- etc.
```

#### Terminal JSON ↔ Windows Terminal
```
- Simple format conversion
- Preserve all 20 color properties
- Handle name mapping
```

---

## UI/UX Requirements

### Main Window

**Menu Bar:**
```
File
├── New Theme
├── Open Theme File...
├── Save
├── Save As...
├── Import from Windows Terminal...
├── Export to Windows Terminal...
├── Recent Files ►
├── Exit

Edit
├── Undo (Ctrl+Z)
├── Redo (Ctrl+Y)
├── Duplicate Theme
├── Rename Theme
├── Delete Theme

View
├── JSON Terminal Editor
├── Windows Terminal Integration
├── QSS Theme Editor
├── Theme Converter

Tools
├── Convert JSON to QSS
├── Convert QSS to JSON
├── Batch Export Themes
├── Import Theme Library
├── Validate All Themes

Help
├── Documentation
├── Keyboard Shortcuts
├── About
```

**Status Bar:**
- Current file path
- Current theme name
- Unsaved changes indicator (*)
- Color format (HEX/RGB/HSL toggle)

---

### Color Picker Component

**Reusable Widget:**
```python
class ColorPickerButton(QPushButton):
    """Enhanced color picker with multiple input methods"""

    Features:
    - Click to open QColorDialog
    - Display current color as background
    - Show hex value as text (#RRGGBB)
    - Right-click for color format options:
      - Copy hex value
      - Copy RGB value
      - Paste color from clipboard
    - Hover tooltip showing RGB/HSL values
    - Visual contrast indicator (warn if poor contrast with background)
```

**Color Validation:**
- Ensure valid hex format (#RRGGBB)
- Allow shorthand (#RGB → #RRGGBB)
- Support alpha channel (#RRGGBBAA) for future use
- Paste color from clipboard (detect various formats)

---

### Preview Widgets

#### Terminal Preview Widget
```python
class TerminalPreviewWidget(QWidget):
    """Preview terminal output with theme colors"""

    Shows:
    - Command prompt with colored username/hostname
    - Directory listings with color-coded file types
    - Git status output (colored branch, status)
    - Error messages (red text)
    - Success messages (green text)
    - Warning messages (yellow text)
    - All 16 ANSI colors in a test pattern

    Features:
    - Real-time color updates
    - Sample text from templates
    - User can edit sample text
    - Export preview as image (PNG)
```

#### QSS Preview Widget (Enhanced)
```python
class QSSPreviewWidget(QWidget):
    """Live preview of QSS theme on sample widgets"""

    Widgets shown:
    - QPushButton (normal, hover, pressed, disabled)
    - QLineEdit (normal, focus, disabled)
    - QTextEdit (with sample text)
    - QComboBox (with sample items)
    - QSpinBox, QDoubleSpinBox
    - QCheckBox (checked, unchecked, disabled)
    - QRadioButton (selected, unselected)
    - QProgressBar (animated)
    - QSlider (horizontal, vertical)
    - QListWidget (with selection)
    - QTreeWidget (with expandable items)
    - QTableWidget (with headers, selection)
    - QTabWidget (multiple tabs)
    - QGroupBox (with content)
    - QScrollBar (horizontal, vertical)
    - QMenuBar, QMenu (popup on hover)
    - QToolBar, QToolButton
    - QStatusBar

    Features:
    - Interactive (can click, type, select)
    - Real-time stylesheet application
    - Side-by-side before/after comparison
    - Export preview as image
```

---

## Technical Specifications

### Dependencies (requirements.txt)

**Core Dependencies:**
```
PyQt6>=6.6.0
PyQt6-Qt6>=6.6.0
Pillow>=10.0.0           # Image processing for Image Converter utility
```

**Optional Dependencies:**
```
Pygments>=2.17.0         # For QSS/JSON syntax highlighting in code editors
cairosvg>=2.7.0          # For SVG support in Image Converter (Linux/macOS)
```

**Note on cairosvg:**
- Windows: Requires additional setup (Cairo DLLs), optional
- Linux: Install via package manager (e.g., `apt install libcairo2-dev`)
- macOS: Install via Homebrew (e.g., `brew install cairo`)

### Python Version
- **Minimum:** Python 3.10
- **Recommended:** Python 3.11+
- **Tested on:** Python 3.11, 3.12

### Cross-Platform Support
- **Windows:** Primary platform (Windows Terminal integration, full feature support)
- **Linux:** Full support (except Windows Terminal features, SVG support with cairosvg)
- **macOS:** Full support (except Windows Terminal features, SVG support with cairosvg)

---

## Data Structures

### Theme Data Classes

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TerminalTheme:
    """Terminal color scheme (JSON format)"""
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

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict"""
        pass

    @classmethod
    def from_dict(cls, data: dict) -> 'TerminalTheme':
        """Create from JSON dict"""
        pass

    def validate(self) -> bool:
        """Validate all colors are valid hex"""
        pass


@dataclass
class QSSPalette:
    """QSS color palette (8 colors)"""
    background: str
    foreground: str
    primary: str
    secondary: str
    border: str
    hover: str
    selected: str
    disabled: str

    def generate_qss(self, template: str = 'default') -> str:
        """Generate QSS code from palette"""
        pass

    @classmethod
    def from_qss(cls, qss_code: str) -> 'QSSPalette':
        """Extract palette from QSS code"""
        pass


@dataclass
class CustomTkinterTheme:
    """CustomTkinter theme structure"""
    name: str
    theme_data: dict  # Complete CTk theme JSON structure

    # Common color properties (extracted for easy editing)
    primary_color: list[str, str]      # [light_mode, dark_mode]
    secondary_color: list[str, str]    # [light_mode, dark_mode]
    background_color: list[str, str]   # [light_mode, dark_mode]
    text_color: list[str, str]         # [light_mode, dark_mode]

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict"""
        pass

    @classmethod
    def from_dict(cls, data: dict, name: str) -> 'CustomTkinterTheme':
        """Create from JSON dict"""
        pass

    def extract_colors(self) -> dict:
        """Extract all unique colors used in theme"""
        pass

    def apply_color_scheme(self, colors: dict):
        """Apply color scheme to all widgets"""
        pass
```

### Theme Manager

```python
class ThemeManager:
    """Central theme management"""

    def load_json_themes(self, filepath: str) -> dict[str, TerminalTheme]:
        """Load themes from JSON file"""
        pass

    def save_json_themes(self, filepath: str, themes: dict[str, TerminalTheme]):
        """Save themes to JSON file"""
        pass

    def load_windows_terminal_settings(self, filepath: str) -> dict:
        """Load Windows Terminal settings.json"""
        pass

    def save_windows_terminal_settings(self, filepath: str, settings: dict, backup: bool = True):
        """Save to Windows Terminal settings.json with backup"""
        pass

    def load_qss_theme(self, filepath: str) -> tuple[QSSPalette, str]:
        """Load QSS file, return palette and full code"""
        pass

    def save_qss_theme(self, filepath: str, qss_code: str):
        """Save QSS code to file"""
        pass

    def load_ctk_theme(self, filepath: str) -> CustomTkinterTheme:
        """Load CustomTkinter theme from JSON file"""
        pass

    def save_ctk_theme(self, filepath: str, theme: CustomTkinterTheme):
        """Save CustomTkinter theme to JSON file"""
        pass
```

### Theme Converter

```python
class ThemeConverter:
    """Convert between theme formats"""

    def terminal_to_qss(self, terminal_theme: TerminalTheme) -> QSSPalette:
        """Convert terminal theme to QSS palette"""
        pass

    def qss_to_terminal(self, qss_palette: QSSPalette, name: str) -> TerminalTheme:
        """Convert QSS palette to terminal theme"""
        pass

    def json_to_windows_terminal(self, theme: TerminalTheme) -> dict:
        """Convert JSON theme to Windows Terminal format"""
        pass

    def windows_terminal_to_json(self, wt_scheme: dict) -> TerminalTheme:
        """Convert Windows Terminal scheme to JSON theme"""
        pass

    def terminal_to_ctk(self, terminal_theme: TerminalTheme) -> CustomTkinterTheme:
        """Convert terminal theme to CustomTkinter theme"""
        pass

    def ctk_to_terminal(self, ctk_theme: CustomTkinterTheme, name: str) -> TerminalTheme:
        """Convert CustomTkinter theme to terminal theme"""
        pass

    def qss_to_ctk(self, qss_palette: QSSPalette, name: str) -> CustomTkinterTheme:
        """Convert QSS palette to CustomTkinter theme"""
        pass

    def ctk_to_qss(self, ctk_theme: CustomTkinterTheme) -> QSSPalette:
        """Convert CustomTkinter theme to QSS palette"""
        pass
```

---

## Configuration Files

### Default Themes (config/themes/themes.json)

**Initial content:** Copy all themes from SAP_Security_DB `config/themes/themes.json`

This provides 60+ pre-made terminal themes as starting point.

### QSS Templates (config/qss_templates/)

**Default templates:**
- `material.qss` - Material Design style
- `flat.qss` - Flat UI style
- `classic.qss` - Classic Windows style
- `dark.qss` - Dark mode base
- `light.qss` - Light mode base

---

## File Operations & Safety

### Backup Strategy

**Before any save operation:**
1. Check if file exists
2. Create backup: `backup\{filename}.backup.{timestamp}`
3. Attempt save
4. If save fails, restore from backup
5. Keep last 5 backups, delete older ones

**Example:**
```
themes.json
themes.json.backup.2025-11-08_120530
themes.json.backup.2025-11-08_115212
themes.json.backup.2025-11-07_183445
```

### Undo/Redo System

**Implementation:**
- Command pattern for all edits
- Store last 50 actions
- Undo: Ctrl+Z
- Redo: Ctrl+Y

**Actions tracked:**
- Color change
- Theme rename
- Theme create/delete
- Import/Export

---

## Testing Requirements

### Unit Tests

**Test coverage:**
- Color validation (hex format)
- JSON parsing/serialization
- Theme conversions (JSON ↔ QSS)
- Windows Terminal settings.json parsing
- Backup/restore functionality

### Integration Tests

- Full workflow: Create theme → Edit → Save → Load
- Import from Windows Terminal → Edit → Export back
- Convert JSON theme → QSS → Apply to app

### Manual Testing

- Test all color pickers work
- Verify previews update in real-time
- Test undo/redo chain
- Verify backup/restore works
- Test on Windows (Windows Terminal integration)

---

## Documentation Requirements

### README.md

**Contents:**
1. Project description
2. Screenshots (all 5 tabs: Terminal, Windows Terminal, QSS, CustomTkinter, Converter)
3. Installation instructions
4. Quick start guide
5. Supported formats (4 formats)
6. Conversion guide
7. Image Converter utility
8. Contributing guidelines
9. License (MIT)

### User Guide (help/README.md)

**Sections:**
1. Getting Started
   - Installation
   - First launch (template_themes.json auto-copy)
   - Application layout
2. JSON Terminal Theme Editor
   - Creating new themes
   - Editing colors (20 color properties)
   - Preview terminal output
   - Export/Import
3. Windows Terminal Integration
   - Finding settings.json
   - Importing themes
   - Exporting themes
   - Safety features (auto-backup)
4. QSS Theme Editor
   - Color palette (8 colors)
   - QSS generation from palette
   - Manual QSS editing
   - Preview widgets
5. CustomTkinter Theme Editor
   - Widget-based color editing
   - Light/Dark mode support
   - Preview CustomTkinter widgets
   - Platform-specific font settings
6. Theme Conversion
   - Supported conversions
   - Conversion mapping tables
   - Batch conversion
7. Image Converter Utility
   - Supported formats
   - Icon creation
   - Batch operations
   - Color palette extraction
8. Keyboard Shortcuts
9. Troubleshooting
10. FAQ

---

## Development Phases

### Phase 1: Core Infrastructure (Week 1)
- [x] Set up Git repository ✓
- [x] Create project structure ✓
- [x] Add assets (icons) ✓
- [x] Add config/templates ✓
- [ ] Implement data classes (TerminalTheme, QSSPalette, CustomTkinterTheme)
- [ ] Implement ThemeManager (load/save JSON, QSS, CTk)
- [ ] Create ColorPickerButton widget
- [ ] Basic main window with 5 tabs
- [ ] First-run setup (copy template_themes.json)

### Phase 2: JSON Terminal Editor (Week 2)
- [ ] Theme selector dropdown
- [ ] 20 color pickers in grid layout
- [ ] Terminal preview widget
- [ ] Create/Duplicate/Delete themes
- [ ] Save/Load functionality (themes.json)
- [ ] Undo/Redo support

### Phase 3: QSS Theme Editor (Week 3)
- [ ] Port existing theme_editor.py code
- [ ] Enhance ThemePreviewWidget
- [ ] 8-color palette editor
- [ ] QSS generation from palette
- [ ] QSS code editor with syntax highlighting
- [ ] Load/Save .qss files
- [ ] Extract colors from QSS

### Phase 4: CustomTkinter Theme Editor (Week 4)
- [ ] Implement CustomTkinterTheme data class
- [ ] Widget-based color editor (CTkButton, CTkEntry, etc.)
- [ ] Light/Dark mode color pairs editing
- [ ] CustomTkinter preview widget (if possible without CTk dependency)
- [ ] JSON editor for advanced settings
- [ ] Load/Save .json CTk themes
- [ ] Color extraction from CTk themes

### Phase 5: Windows Terminal Integration (Week 5)
- [ ] Detect Windows Terminal installation
- [ ] Parse settings.json safely (preserve all sections)
- [ ] List themes in settings
- [ ] Edit selected theme
- [ ] Add/Delete themes in settings
- [ ] Backup mechanism (automatic before save)
- [ ] Import/Export functionality
- [ ] Theme name conflict detection

### Phase 6: Theme Conversion (Week 6)
- [ ] Implement ThemeConverter class
- [ ] Terminal JSON → QSS conversion
- [ ] Terminal JSON → CustomTkinter conversion
- [ ] QSS → Terminal JSON conversion
- [ ] CustomTkinter → Terminal JSON conversion
- [ ] QSS ↔ CustomTkinter conversion
- [ ] Conversion UI in separate tab
- [ ] Batch conversion tools
- [ ] Conversion preview (before/after)

### Phase 7: Image Converter Refactoring (Week 7) ⭐ NEW
- [ ] Analyze current img_conv.pyw implementation
- [ ] Design PyQt6 UI layout
- [ ] Implement ImageConverter module (modules/image_converter.py)
- [ ] Port GUI functionality to PyQt6:
  - [ ] File selection dialog
  - [ ] Drag & drop support (PyQt6 QDrag/QDrop)
  - [ ] Image preview
  - [ ] Format selection
  - [ ] Quality slider
  - [ ] Progress bar
  - [ ] Recent files menu
- [ ] Port CLI functionality
- [ ] Batch conversion dialog
- [ ] Multi-size ICO generation
- [ ] SVG support (optional with cairosvg)
- [ ] Add NEW features:
  - [ ] Resize/crop tools
  - [ ] Color palette extraction
  - [ ] Generate theme from image colors
- [ ] Integration with main application (Tools menu)
- [ ] Testing (GUI and CLI modes)

### Phase 8: Polish & Testing (Week 8)
- [ ] UI/UX improvements across all tabs
- [ ] Consistent styling (apply QSS theme to app itself)
- [ ] Keyboard shortcuts (document in help)
- [ ] Status bar updates
- [ ] Error handling and user-friendly messages
- [ ] Input validation
- [ ] Unit tests (all data classes and converters)
- [ ] Integration tests (workflows)
- [ ] Documentation (README, User Guide)
- [ ] Package for distribution (PyInstaller/cx_Freeze)
- [ ] Create installer (optional)

---

## Success Criteria

**Must Have:**
- [ ] Edit JSON terminal themes (20 colors)
- [ ] Create/duplicate/delete themes
- [ ] Live preview of terminal output
- [ ] Save/load themes.json (auto-copy from template on first run)
- [ ] QSS theme editor with color palette
- [ ] QSS preview widget
- [ ] Generate QSS from color palette
- [ ] CustomTkinter theme editor
- [ ] Edit CustomTkinter themes (light/dark mode)
- [ ] Image Converter utility (PyQt6 version)
- [ ] Convert between image formats
- [ ] Multi-size ICO generation

**Should Have:**
- [ ] Windows Terminal integration
- [ ] Import/export Windows Terminal themes
- [ ] Theme converter (JSON ↔ QSS ↔ CustomTkinter)
- [ ] Undo/Redo support
- [ ] Backup/restore functionality (automatic for Windows Terminal)
- [ ] Syntax highlighting in code editors
- [ ] CLI mode for Image Converter
- [ ] Color palette extraction from images
- [ ] Template library (60+ terminal themes included)

**Nice to Have:**
- [ ] Export preview as image
- [ ] Batch theme conversion
- [ ] Color accessibility checker (contrast warnings)
- [ ] Theme sharing/import from URL
- [ ] Generate theme from image colors
- [ ] Resize/crop in Image Converter
- [ ] Package as standalone executable
- [ ] Apply theme to the app itself (dogfooding)

---

## Example Themes to Include

**From SAP_Security_DB themes.json:**
Copy all 60+ themes as default theme library:
- GruvboxDark
- catppuccin-mocha
- GitHub Dark
- nord-light
- OceanicMaterial
- cyberpunk
- matrix
- ... and 50+ more

**Default QSS Themes:**
Create 5 base QSS templates:
1. **Dark Material** - Material Design dark theme
2. **Light Material** - Material Design light theme
3. **Gruvbox QSS** - Convert Gruvbox terminal theme to QSS
4. **Nord QSS** - Convert Nord terminal theme to QSS
5. **Classic Windows** - Windows 7/10 style theme

---

## Notes for Development

### Important Design Decisions

1. **Single JSON file for terminal themes**
   - All themes in one `themes.json` file (like SAP project)
   - User can create multiple theme files if needed
   - Default file: `config/themes/themes.json`

2. **Individual QSS files**
   - One `.qss` file per theme
   - Stored in `config/qss_themes/`
   - User can organize in subfolders

3. **Windows Terminal settings.json**
   - NEVER overwrite entire file
   - Only modify `schemes` array
   - Preserve all other settings
   - ALWAYS backup before editing

4. **Color format standardization**
   - Internal: Always uppercase hex (#RRGGBB)
   - Display: Can show RGB, HSL, hex (user preference)
   - Validation: Accept #RGB, #RRGGBB, rgb(), etc., convert to standard

5. **Preview updates**
   - Real-time as colors change
   - Debounce rapid changes (200ms delay)
   - Option to disable auto-update for performance

### Code Quality Standards

- **Type hints:** Use throughout
- **Docstrings:** All public methods
- **Error handling:** Try/except with specific exceptions
- **Logging:** Use Python logging module
- **Config:** Store user preferences in `config.json`
- **Validation:** All user input validated
- **Testing:** Minimum 70% code coverage

### Performance Considerations

- **Large theme files:** Paginate theme list if >100 themes
- **Preview updates:** Use QTimer.singleShot for debouncing
- **JSON parsing:** Use built-in `json` module (fast enough)
- **QSS application:** Don't reload entire stylesheet, only changed widgets

---

## Reference Materials

### tools/ Folder - Reference Code

**Purpose:** Contains reference implementations and utilities to be refactored/integrated

#### tools/theme_editor.py
- **Source:** JSON-Template-Combiner project
- **Current Status:** Standalone QSS theme editor
- **Language:** Python 3 with PyQt6
- **Lines:** ~785 lines
- **Usage:** Reference implementation for QSS theme editor

**Key Components to Port/Reference:**
1. `ColorButton` class → Enhance to `ColorPickerButton`
   - 40x30 fixed size
   - Color selection with QColorDialog
   - Hex color display
2. `ThemePreviewWidget` class → Use as base for QSSPreviewWidget
   - Comprehensive widget coverage
   - Live preview functionality
3. QSS generation logic → Extract to template system
   - Template-based stylesheet generation
   - 8-color palette system
4. Color extraction regex → Improve and reuse
   - Extract colors from existing QSS files

#### tools/img_conv/img_conv.pyw
- **Source:** Custom utility project
- **Current Status:** ⚠️ TO BE REFACTORED TO PyQt6
- **Language:** Python 3 with CustomTkinter
- **Lines:** ~1017 lines
- **Dependencies:** customtkinter, PIL/Pillow, tkinterdnd2, cairosvg (optional)

**Current Features:**
- Dual mode (GUI and CLI)
- Drag & drop support
- Format conversion: ICO, JPEG, PNG, BMP, GIF, WebP, TIFF, SVG
- Batch conversion
- Quality settings
- Multi-size ICO generation (32x32, 128x128, 256x256)
- Recent files tracking
- Settings persistence

**Refactoring Tasks:**
1. Convert UI from CustomTkinter → PyQt6
2. Replace tkinterdnd2 with PyQt6 drag/drop
3. Move to `modules/image_converter.py`
4. Maintain CLI functionality
5. Add new features (color extraction, resize/crop)
6. Integrate with main app (Tools menu)

### Template Files - Starting Points

1. **config/templates/template_themes.json** ⭐ MOST IMPORTANT
   - **Source:** SAP_Security_DB project
   - **Content:** 60+ terminal themes (1037 lines)
   - **Usage:** Copy to `config/themes/themes.json` on first run
   - **Purpose:** Default theme library for terminal theme editor

2. **config/templates/template_dark.qss**
   - **Source:** JSON-Template-Combiner project
   - **Content:** Complete dark theme QSS (345 lines)
   - **Usage:** Reference for QSS structure

3. **config/templates/template_green.json**
   - **Source:** Custom project
   - **Content:** CustomTkinter theme example (358 lines)
   - **Usage:** Reference for CustomTkinter theme structure

4. **config/templates/template_wt_settings.json**
   - **Source:** User's Windows Terminal configuration
   - **Content:** Complete settings.json example (2434 lines)
   - **Usage:** Reference for Windows Terminal integration

### Color Conversion Formulas

**Hex ↔ RGB:**
```python
def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"
```

**RGB ↔ HSL:** (for color picker enhancements)
Use `colorsys` module

---

## License

**Recommended:** MIT License

Reasoning:
- Permissive open-source license
- Allows commercial and private use
- Compatible with PyQt6 (GPL/Commercial)
- Encourages community contributions

---

## Contact & Contributions

**Repository:** https://github.com/RafalekS/Theme_Editor (TBD)
**Issues:** https://github.com/RafalekS/Theme_Editor/issues
**Discussions:** https://github.com/RafalekS/Theme_Editor/discussions

**Contributions welcome:**
- New theme templates
- QSS generation templates
- CustomTkinter theme templates
- Bug fixes
- Feature requests
- Documentation improvements
- Image converter enhancements

---

## Document Changelog

### Version 1.1 - 2025-11-08 (Current)
**Major Additions:**
- ✅ Added **CustomTkinter Theme Format** support (4th format)
- ✅ Added **assets/** folder documentation (application icons)
- ✅ Added **config/templates/** folder documentation (example themes)
- ✅ Added **Integrated Image Converter** utility section
- ✅ Added **Phase 7: Image Converter Refactoring** to development plan
- ✅ Added **Phase 4: CustomTkinter Theme Editor** to development plan
- ✅ Updated folder structure to match actual implementation
- ✅ Added CustomTkinterTheme data class
- ✅ Updated ThemeManager with CTk theme support
- ✅ Updated ThemeConverter with CTk conversion methods
- ✅ Updated dependencies (added Pillow, cairosvg)
- ✅ Updated Success Criteria with new features
- ✅ Expanded Reference Materials section
- ✅ Updated documentation requirements

**Key Changes:**
- Tab count increased from 3 to 5 (added CustomTkinter and Converter tabs)
- Development phases extended from 6 to 8 weeks
- Template files documented with line counts and usage
- Image converter marked for PyQt6 refactoring
- Added color palette extraction feature
- Added "generate theme from image" feature

### Version 1.0 - 2025-11-08 (Initial)
- Initial requirements document
- JSON Terminal Themes support
- Windows Terminal integration
- QSS Themes support
- Basic project structure

---

**Document Version:** 1.1
**Created:** 2025-11-08
**Last Updated:** 2025-11-08
**Author:** Rafal Staska (based on SAP_Security_DB project requirements)
**Status:** Updated with all current project additions - Ready for implementation
