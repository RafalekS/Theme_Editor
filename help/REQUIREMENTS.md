# Theme Editor - Project Requirements Document

## Project Overview

**Project Name:** Theme_Editor
**Type:** Standalone PyQt6 GUI Application
**Purpose:** Universal theme editor supporting multiple theme formats (JSON terminal themes, Windows Terminal themes, QSS themes)

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
├── .gitignore                   # Git ignore file
│
├── modules/
│   ├── __init__.py
│   ├── json_theme_editor.py     # JSON terminal themes editor
│   ├── qss_theme_editor.py      # QSS themes editor (based on existing code)
│   ├── theme_converter.py       # Convert between formats
│   ├── color_picker.py          # Reusable color picker widget
│   └── preview_widgets.py       # Theme preview components
│
├── config/
│   ├── themes/                  # JSON terminal themes storage
│   │   └── themes.json          # Default themes (from SAP project)
│   └── qss_themes/              # QSS theme files storage
│       └── default.qss
│
└── help/
    ├── README.md                # User documentation
    └── CHANGELOG.md             # Version history
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

## Existing Theme Editor Reference

**Source:** https://github.com/RafalekS/JSON-Template-Combiner/blob/master/theme_editor.py

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

## New Features to Implement

### 1. Multi-Format Support

**Unified Interface:**
- Tab-based UI with separate editors for each format:
  - Tab 1: JSON Terminal Themes
  - Tab 2: Windows Terminal Integration
  - Tab 3: QSS Themes

**Format Conversion:**
- Convert terminal themes → QSS (map ANSI colors to UI elements)
- Convert QSS → terminal themes (extract and map colors)
- Export terminal themes to Windows Terminal format
- Import Windows Terminal themes to standalone JSON

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
- All 16 ANSI colors visible

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

```
PyQt6>=6.6.0
PyQt6-Qt6>=6.6.0
```

Optional:
```
Pygments>=2.17.0  # For QSS syntax highlighting
```

### Python Version
- **Minimum:** Python 3.10
- **Recommended:** Python 3.11+

### Cross-Platform Support
- **Windows:** Primary platform (Windows Terminal integration)
- **Linux:** Full support (except Windows Terminal features)
- **macOS:** Full support (except Windows Terminal features)

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
2. Create backup: `{filename}.backup.{timestamp}`
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
2. Screenshots (all 3 tabs)
3. Installation instructions
4. Quick start guide
5. Supported formats
6. Conversion guide
7. Contributing guidelines
8. License (MIT recommended)

### User Guide (help/README.md)

**Sections:**
1. Getting Started
2. JSON Terminal Theme Editor
   - Creating new themes
   - Editing colors
   - Preview terminal output
3. Windows Terminal Integration
   - Finding settings.json
   - Importing themes
   - Exporting themes
4. QSS Theme Editor
   - Color palette
   - QSS generation
   - Manual editing
5. Theme Conversion
   - Supported conversions
   - Conversion mapping
6. Keyboard Shortcuts
7. Troubleshooting
8. FAQ

---

## Development Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up Git repository
- [ ] Create project structure
- [ ] Implement data classes (TerminalTheme, QSSPalette)
- [ ] Implement ThemeManager (load/save JSON)
- [ ] Create ColorPickerButton widget
- [ ] Basic main window with tabs

### Phase 2: JSON Terminal Editor (Week 2)
- [ ] Theme selector dropdown
- [ ] 20 color pickers in grid layout
- [ ] Terminal preview widget
- [ ] Create/Duplicate/Delete themes
- [ ] Save/Load functionality
- [ ] Undo/Redo support

### Phase 3: QSS Theme Editor (Week 3)
- [ ] Port existing theme_editor.py code
- [ ] Enhance ThemePreviewWidget
- [ ] 8-color palette editor
- [ ] QSS generation from palette
- [ ] QSS code editor
- [ ] Load/Save .qss files
- [ ] Extract colors from QSS

### Phase 4: Windows Terminal Integration (Week 4)
- [ ] Detect Windows Terminal installation
- [ ] Parse settings.json safely
- [ ] List themes in settings
- [ ] Edit selected theme
- [ ] Add/Delete themes in settings
- [ ] Backup mechanism
- [ ] Import/Export functionality

### Phase 5: Theme Conversion (Week 5)
- [ ] Implement ThemeConverter class
- [ ] Terminal JSON → QSS conversion
- [ ] QSS → Terminal JSON conversion
- [ ] Conversion UI in separate tab
- [ ] Batch conversion tools

### Phase 6: Polish & Testing (Week 6)
- [ ] UI/UX improvements
- [ ] Keyboard shortcuts
- [ ] Status bar updates
- [ ] Error handling
- [ ] Unit tests
- [ ] Integration tests
- [ ] Documentation
- [ ] Package for distribution

---

## Success Criteria

**Must Have:**
✅ Edit JSON terminal themes (20 colors)
✅ Create/duplicate/delete themes
✅ Live preview of terminal output
✅ Save/load themes.json
✅ QSS theme editor with color palette
✅ QSS preview widget
✅ Generate QSS from color palette

**Should Have:**
✅ Windows Terminal integration
✅ Import/export Windows Terminal themes
✅ Theme converter (JSON ↔ QSS)
✅ Undo/Redo support
✅ Backup/restore functionality
✅ Syntax highlighting in QSS editor

**Nice to Have:**
✅ Export preview as image
✅ Theme templates library
✅ Batch theme conversion
✅ Color accessibility checker
✅ Theme sharing/import from URL

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

### Existing Code to Port/Reference

1. **theme_editor.py** (from JSON-Template-Combiner)
   - `ColorButton` class → Enhance to `ColorPickerButton`
   - `ThemePreviewWidget` → Use as base for QSSPreviewWidget
   - QSS generation logic → Extract to template system
   - Color extraction regex → Improve and reuse

2. **themes.json** (from SAP_Security_DB)
   - Use as default theme library
   - Reference for TerminalTheme structure

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
- Bug fixes
- Feature requests
- Documentation improvements

---

**Document Version:** 1.0
**Created:** 2025-11-08
**Author:** Based on SAP_Security_DB project requirements
**Status:** Ready for implementation
