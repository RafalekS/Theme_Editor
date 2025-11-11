# Qt Stylesheet (QSS) Widget Reference Guide

Complete reference for styling Qt widgets using stylesheets. This guide covers properties, sub-controls (::syntax), and pseudo-states (:syntax) for commonly used widgets.

---

## Table of Contents

1. [Universal Properties & Pseudo-States](#universal-properties--pseudo-states)
2. [QTabWidget & QTabBar](#qtabwidget--qtabbar)
3. [QRadioButton](#qradiobutton)
4. [QProgressDialog](#qprogressdialog)
5. [QDialogButtonBox](#qdialogbuttonbox)
6. [QTableWidget (QTableView)](#qtablewidget-qtableview)
7. [QTreeWidget (QTreeView)](#qtreewidget-qtreeview)
8. [QSpinBox & QDoubleSpinBox](#qspinbox--qdoublespinbox)
9. [QWizard & QWizardPage](#qwizard--qwizardpage)
10. [QFontDialog & QInputDialog](#qfontdialog--qinputdialog)
11. [QToolButton](#qtoolbutton)
12. [QSlider](#qslider)
13. [QHeaderView](#qheaderview)
14. [Additional Widgets](#additional-widgets)

---

## Universal Properties & Pseudo-States

### Complete List of Pseudo-States

All pseudo-states use single colon `:` syntax and can be chained with logical AND. Use `!` for negation (e.g., `:!hover`).

**Widget State:**
- `:active` - Widget resides in an active window
- `:disabled` - Widget is disabled
- `:enabled` - Widget is enabled
- `:focus` - Widget has input focus
- `:hover` - Mouse cursor is over the widget

**Selection & Checking:**
- `:checked` - Item is checked (checkboxes, radio buttons, checkable menu items)
- `:unchecked` - Item is not checked
- `:indeterminate` - Checkbox is in indeterminate state
- `:selected` - Item is selected
- `:default` - Default button state

**Positional:**
- `:first` - First item in a list
- `:last` - Last item in a list
- `:middle` - Middle item (not first or last)
- `:only-one` - Only item in a list
- `:alternate` - Every alternate row (when alternating row colors enabled)

**Navigation:**
- `:next-selected` - Next item is selected
- `:previous-selected` - Previous item is selected

**Structural (QTreeView):**
- `:open` - Branch is expanded
- `:closed` - Branch is collapsed
- `:has-children` - Item has children
- `:has-siblings` - Item has siblings
- `:adjoins-item` - Branch adjoins an item

**Direction/Orientation:**
- `:horizontal` - Horizontal orientation
- `:vertical` - Vertical orientation
- `:top` - Top position/orientation
- `:bottom` - Bottom position/orientation
- `:left` - Left position/orientation
- `:right` - Right position/orientation

**State Indicators:**
- `:on` - Toggle button is on
- `:off` - Toggle button is off (or spinbox at min/max)
- `:pressed` - Widget is being pressed
- `:flat` - Flat style widget
- `:editable` - Widget is editable
- `:closable` - Widget can be closed
- `:floatable` - Widget can float
- `:movable` - Widget can be moved
- `:exclusive` - Exclusive selection
- `:non-exclusive` - Non-exclusive selection

### Common Properties (Box Model & Appearance)

**Box Model:**
- `margin`, `margin-top`, `margin-right`, `margin-bottom`, `margin-left`
- `padding`, `padding-top`, `padding-right`, `padding-bottom`, `padding-left`
- `border`, `border-width`, `border-style`, `border-color`
- `border-top`, `border-right`, `border-bottom`, `border-left` (with -width, -style, -color variants)
- `border-radius`, `border-top-left-radius`, `border-top-right-radius`, `border-bottom-left-radius`, `border-bottom-right-radius`
- `border-image` (with -slice, -repeat, -width, -outset variants)
- `width`, `height`, `min-width`, `max-width`, `min-height`, `max-height`

**Background:**
- `background` (shorthand)
- `background-color`
- `background-image`
- `background-repeat` (repeat, repeat-x, repeat-y, no-repeat)
- `background-position` (top, bottom, left, right, center, or pixel/percentage values)
- `background-attachment` (scroll, fixed) - Important for scrollable areas
- `background-clip` (border, padding, content)
- `background-origin` (border, padding, content)

**Text & Font:**
- `color` - Text color
- `font` (shorthand)
- `font-family`
- `font-size`
- `font-style` (normal, italic, oblique)
- `font-weight` (normal, bold, 100-900)
- `text-align` (left, right, center, justify)
- `text-decoration` (none, underline, overline, line-through)
- `letter-spacing`
- `word-spacing`

**Selection:**
- `selection-color` - Selected text color
- `selection-background-color` - Selected text background

**Other:**
- `opacity` (0.0 to 1.0)
- `outline`, `outline-color`, `outline-offset`, `outline-style`, `outline-radius`
- `spacing` - Space between sub-elements
- `image` - Image for sub-controls
- `icon` - Icon image
- `icon-size` - Icon dimensions

**Positioning (for sub-controls):**
- `position` (relative, absolute)
- `top`, `right`, `bottom`, `left` - Offset values
- `subcontrol-origin` (margin, border, padding, content)
- `subcontrol-position` (top left, top center, top right, center left, center, center right, bottom left, bottom center, bottom right)

---

## QTabWidget & QTabBar

### QTabWidget

Container for tab pages with tab bar.

**Supported Properties:**
- Box model: `background`, `background-color`, `border`, `border-radius`, `margin`, `padding`
- Text: `color`, `font`

**Sub-Controls:**

#### `::pane`
The frame that contains the tab pages.

**Properties:** Full box model support
**Example:**
```css
QTabWidget::pane {
    border: 1px solid #3d3d3d;
    background-color: #252526;
    border-radius: 4px;
    top: -1px; /* Overlap with tab bar */
}
```

#### `::tab-bar`
Positions the tab bar within the widget.

**Properties:** `alignment`, `subcontrol-position`, `subcontrol-origin`
**Example:**
```css
QTabWidget::tab-bar {
    alignment: center;
}
```

#### `::left-corner`, `::right-corner`
Corner widgets (if any).

**Properties:** Box model properties

**Pseudo-States:**
- `:top`, `:bottom`, `:left`, `:right` - Position of tabs

---

### QTabBar

The tab bar containing individual tabs.

**Supported Properties:**
- Box model properties
- `spacing` - Space between tabs
- `alignment` - Tab alignment

**Sub-Controls:**

#### `::tab`
Individual tab styling.

**Properties:** Full box model, text, background
**Pseudo-States:**
- `:selected` - Currently selected tab
- `:hover` - Mouse over tab
- `:pressed` - Tab being clicked
- `:disabled` - Disabled tab
- `:only-one` - Single tab
- `:first`, `:last`, `:middle` - Position in tab bar
- `:next-selected`, `:previous-selected` - Adjacent to selected
- `:top`, `:bottom`, `:left`, `:right` - Tab bar position

**Example:**
```css
QTabBar::tab {
    background-color: #2d2d30;
    color: #cccccc;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #007acc;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #3e3e42;
}

QTabBar::tab:first {
    margin-left: 0px;
}

QTabBar::tab:last {
    margin-right: 0px;
}
```

#### `::close-button`
Close button on closable tabs.

**Properties:** Box model, `image`, `subcontrol-position`
**Pseudo-States:** `:hover`, `:pressed`

**Example:**
```css
QTabBar::close-button {
    image: url(close.png);
    subcontrol-position: right;
}

QTabBar::close-button:hover {
    image: url(close-hover.png);
}
```

#### `::tear`
Tear indicator when tabs can be torn off.

**Properties:** Box model, `image`

#### `::scroller`
Scroll buttons when tabs overflow.

**Properties:** `width` (for horizontal), `height` (for vertical)

**Example:**
```css
QTabBar::scroller {
    width: 20px;
}
```

---

## QRadioButton

Radio button with indicator (circle) and text label.

**Supported Properties:**
- Box model properties
- `spacing` - Space between indicator and text
- Text properties

**Sub-Controls:**

#### `::indicator`
The circular radio button indicator.

**Properties:**
- `width`, `height` - Size of indicator
- `border`, `border-radius` - Usually 50% of width/height for circle
- `background-color`, `background-image`
- `image` - Icon when checked

**Positioning:**
- Default: top-left of widget
- Use `subcontrol-position` to change

**Pseudo-States:**
- `:checked` - Radio button selected
- `:unchecked` - Radio button not selected
- `:hover` - Mouse over indicator
- `:pressed` - Being clicked
- `:disabled` - Disabled state
- `:enabled` - Enabled state
- `:focus` - Has keyboard focus

**Example:**
```css
QRadioButton {
    color: #cccccc;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #5a5a5a;
    border-radius: 9px; /* Half of width/height for circle */
    background-color: #3c3c3c;
}

QRadioButton::indicator:hover {
    border: 1px solid #007acc;
}

QRadioButton::indicator:checked {
    background-color: #007acc;
    border: 1px solid #007acc;
    /* Can also use image for checkmark */
    image: url(radio-checked.png);
}

QRadioButton::indicator:disabled {
    background-color: #2d2d30;
    border-color: #3d3d3d;
}
```

---

## QProgressDialog

Dialog showing progress bar and cancel button. Limited styling support.

**Supported Properties:**
- `background`
- `background-clip`
- `background-origin`

**Note:** Inherits from QDialog. Style the contained QPushButton and QProgressBar separately for full customization.

**Example:**
```css
QProgressDialog {
    background-color: #252526;
}

/* Style internal widgets */
QProgressDialog QPushButton {
    min-width: 80px;
    padding: 6px 16px;
}

QProgressDialog QProgressBar {
    border: 1px solid #5a5a5a;
    border-radius: 4px;
}
```

---

## QDialogButtonBox

Container for dialog buttons (OK, Cancel, etc.).

**Supported Properties:**
- Box model properties
- `button-layout` - Button ordering (0=WinLayout, 1=MacLayout, 2=KdeLayout, 3=GnomeLayout)

**Pseudo-States:**
- Standard states: `:enabled`, `:disabled`, `:focus`, `:hover`

**Note:** Style individual QPushButton widgets within the button box.

**Example:**
```css
QDialogButtonBox {
    background-color: #1e1e1e;
    padding: 10px;
    button-layout: 0; /* Windows layout */
}

QDialogButtonBox QPushButton {
    min-width: 80px;
    padding: 6px 16px;
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #0e639c;
    border-radius: 4px;
}

QDialogButtonBox QPushButton:hover {
    background-color: #1177bb;
}
```

---

## QTableWidget (QTableView)

Table/grid widget with rows and columns. Inherits from QAbstractScrollArea and QAbstractItemView.

**Supported Properties:**
- Full box model
- `alternate-background-color` - Color for alternating rows (when enabled)
- `selection-color` - Selected text color
- `selection-background-color` - Selected cell background
- `gridline-color` - Color of grid lines
- `background-attachment` (scroll, fixed) - For scrollable backgrounds
- `show-decoration-selected` - Whether selection extends beyond text

**Sub-Controls:**

#### `::item`
Individual table cells.

**Properties:** Full box model, text, background
**Pseudo-States:**
- `:selected` - Cell is selected
- `:hover` - Mouse over cell
- `:alternate` - In alternating row
- `:focus` - Cell has focus
- `:disabled`, `:enabled`

**Example:**
```css
QTableView {
    background-color: #252526;
    border: 1px solid #3d3d3d;
    gridline-color: #3d3d3d;
    alternate-background-color: #2a2d2e;
    selection-background-color: #094771;
    selection-color: #ffffff;
}

QTableView::item {
    padding: 4px;
    border: none;
}

QTableView::item:selected {
    background-color: #094771;
    color: #ffffff;
}

QTableView::item:hover:!selected {
    background-color: #2a2d2e;
}

QTableView::item:alternate {
    background-color: #292929;
}
```

#### `QTableCornerButton::section`
The corner button (top-left) between horizontal and vertical headers.

**Properties:** Box model (border required for background to show)

**Example:**
```css
QTableCornerButton::section {
    background-color: #2d2d30;
    border: 1px solid #3d3d3d;
}
```

---

## QTreeWidget (QTreeView)

Hierarchical tree widget with expandable branches. Inherits from QAbstractScrollArea and QAbstractItemView.

**Supported Properties:**
- Full box model
- `alternate-background-color` - Alternating row colors
- `selection-color`, `selection-background-color` - Selection styling
- `background-attachment` (scroll, fixed) - Scrollable backgrounds
- `show-decoration-selected` - Whether selection extends to edges

**Sub-Controls:**

#### `::item`
Tree items (nodes).

**Properties:** Full box model, text, background
**Pseudo-States:**
- `:selected` - Item is selected
- `:hover` - Mouse over item
- `:alternate` - In alternating row
- `:focus` - Item has focus
- `:open` - Item is expanded
- `:closed` - Item is collapsed
- `:has-children` - Item has child nodes
- `:has-siblings` - Item has siblings

**Example:**
```css
QTreeView::item {
    padding: 4px;
    border: none;
}

QTreeView::item:selected {
    background-color: #094771;
    color: #ffffff;
}

QTreeView::item:hover:!selected {
    background-color: #2a2d2e;
}
```

#### `::branch`
Tree expansion branches (lines and expand/collapse indicators).

**Properties:**
- `background`, `background-color`
- `border-image` - Use images for branch lines
- `image` - Expand/collapse icons

**Pseudo-States (Combinations):**
The branch sub-control uses complex pseudo-state combinations to style different branch types:

- `:has-siblings` - Branch has sibling items
- `:!has-siblings` - No siblings (last item)
- `:adjoins-item` - Branch is next to an item
- `:!adjoins-item` - Branch is not next to item (vertical line)
- `:has-children` - Item can be expanded
- `:!has-children` - Item is a leaf (no children)
- `:open` - Branch is expanded
- `:closed` - Branch is collapsed

**Common Branch Combinations:**
```css
/* Vertical line (middle of tree) */
QTreeView::branch:has-siblings:!adjoins-item {
    border-image: url(vline.png) 0;
}

/* Branch line with siblings */
QTreeView::branch:has-siblings:adjoins-item {
    border-image: url(branch-more.png) 0;
}

/* End branch (no more siblings below) */
QTreeView::branch:!has-children:!has-siblings:adjoins-item {
    border-image: url(branch-end.png) 0;
}

/* Closed folder with siblings */
QTreeView::branch:closed:has-children:has-siblings {
    border-image: none;
    image: url(branch-closed.png);
}

/* Closed folder without siblings (last item) */
QTreeView::branch:has-children:!has-siblings:closed {
    border-image: none;
    image: url(branch-closed.png);
}

/* Open folder with siblings */
QTreeView::branch:open:has-children:has-siblings {
    border-image: none;
    image: url(branch-open.png);
}

/* Open folder without siblings (last item) */
QTreeView::branch:open:has-children:!has-siblings {
    border-image: none;
    image: url(branch-open.png);
}
```

**Color-only styling (no images):**
```css
QTreeView::branch {
    background-color: #252526;
}

QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {
    border-image: none;
    image: url(branch-closed.png);
}

QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings {
    border-image: none;
    image: url(branch-open.png);
}
```

---

## QSpinBox & QDoubleSpinBox

Numeric input with increment/decrement buttons.

**Supported Properties:**
- Full box model
- Text properties
- `selection-color`, `selection-background-color`

**Sub-Controls:**

#### `::up-button`
Up increment button.

**Properties:**
- Box model
- `subcontrol-origin` (default: border)
- `subcontrol-position` (default: top right)
- `width`, `height`
- `image`, `background-color`

**Pseudo-States:**
- `:hover`, `:pressed`, `:disabled`

**Example:**
```css
QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #5a5a5a;
    background-color: #3c3c3c;
}

QSpinBox::up-button:hover {
    background-color: #4a4a4a;
}

QSpinBox::up-button:pressed {
    background-color: #2c2c2c;
}
```

#### `::up-arrow`
Arrow icon inside up button.

**Properties:**
- `width`, `height`
- `image`
- `border` (for creating triangle with transparent borders)

**Pseudo-States:**
- `:disabled` - When disabled
- `:off` - When at maximum value (cannot increment)

**Example:**
```css
QSpinBox::up-arrow {
    image: url(up-arrow.png);
    width: 7px;
    height: 7px;
}

QSpinBox::up-arrow:disabled,
QSpinBox::up-arrow:off {
    image: url(up-arrow-disabled.png);
}

/* CSS triangle (no image) */
QSpinBox::up-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #cccccc;
    width: 0px;
    height: 0px;
}
```

#### `::down-button`
Down decrement button.

**Properties:** Same as `::up-button`
**Pseudo-States:** `:hover`, `:pressed`, `:disabled`
**Default Position:** bottom right

**Example:**
```css
QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #5a5a5a;
    background-color: #3c3c3c;
}
```

#### `::down-arrow`
Arrow icon inside down button.

**Properties:** Same as `::up-arrow`
**Pseudo-States:**
- `:disabled`, `:off` - When at minimum value

**Example:**
```css
QSpinBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #cccccc;
    width: 0px;
    height: 0px;
}

QSpinBox::down-arrow:disabled,
QSpinBox::down-arrow:off {
    border-top-color: #6d6d6d;
}
```

**Complete Example:**
```css
QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    color: #e0e0e0;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    padding: 5px 8px;
    padding-right: 20px; /* Space for buttons */
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #007acc;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #5a5a5a;
    background-color: #3c3c3c;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #5a5a5a;
    background-color: #3c3c3c;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #cccccc;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #cccccc;
}
```

---

## QWizard & QWizardPage

Wizard dialog for multi-step processes. Limited direct styling support.

**Supported Properties:**
- Basic box model: `background`, `background-color`, `border`
- Text: `color`, `font`

**Styling Approach:**
Style individual child widgets (buttons, labels, etc.) rather than the wizard itself.

**Example:**
```css
QWizard {
    background-color: #252526;
}

QWizardPage {
    background-color: #252526;
}

/* Style wizard buttons */
QWizard QPushButton {
    min-width: 80px;
    padding: 6px 16px;
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #0e639c;
    border-radius: 4px;
}
```

---

## QFontDialog & QInputDialog

Standard dialogs with limited stylesheet support. Apply styles to contained widgets.

**Supported Properties:**
- Basic: `background`, `background-color`, `color`, `font`

**Styling Approach:**
Target child widgets using descendant selectors.

**Example:**
```css
QFontDialog, QInputDialog {
    background-color: #252526;
    color: #cccccc;
}

QFontDialog QListView {
    background-color: #1e1e1e;
    border: 1px solid #3d3d3d;
}

QInputDialog QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    padding: 5px;
}
```

---

## QToolButton

Enhanced button with optional menu/dropdown.

**Supported Properties:**
- Full box model
- Text properties
- `icon-size` - Size of icon

**Sub-Controls:**

#### `::menu-indicator`
Indicator for button menu (small arrow).

**Properties:**
- `width`, `height`
- `image`
- `subcontrol-origin`, `subcontrol-position`
- Default position: bottom-right

**Example:**
```css
QToolButton::menu-indicator {
    image: url(down-arrow.png);
    subcontrol-origin: padding;
    subcontrol-position: bottom right;
    width: 10px;
    height: 10px;
}
```

#### `::menu-button`
The menu button (only in MenuButtonPopup mode).

**Properties:**
- Box model
- `width`
- `border`

**Example:**
```css
QToolButton::menu-button {
    border: 1px solid #5a5a5a;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    width: 16px;
}
```

#### `::menu-arrow`
Arrow inside menu-button.

**Properties:** `image`, size properties

**Example:**
```css
QToolButton::menu-arrow {
    image: url(down-arrow.png);
}

QToolButton::menu-arrow:open {
    position: relative;
    top: 2px;
    left: 2px; /* Shift when menu is open */
}
```

#### `::up-arrow`, `::down-arrow`, `::left-arrow`, `::right-arrow`
Directional arrows (for toolbar navigation).

**Properties:** `image`, size properties

**Pseudo-States:**
- `:checked` - Button is checked/toggled
- `:pressed` - Being pressed
- `:hover` - Mouse over
- `:disabled` - Disabled state
- `:enabled` - Enabled state
- `:focus` - Has focus
- `:flat` - Flat style (no border)
- `:open` - Menu is open

**Complete Example:**
```css
QToolButton {
    background-color: #3c3c3c;
    color: #e0e0e0;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    padding: 6px;
}

QToolButton:hover {
    background-color: #4a4a4a;
    border-color: #007acc;
}

QToolButton:pressed {
    background-color: #2c2c2c;
}

QToolButton:checked {
    background-color: #094771;
    border-color: #007acc;
}

QToolButton:disabled {
    background-color: #2d2d30;
    color: #6d6d6d;
}

QToolButton::menu-indicator {
    image: url(down-arrow.png);
    subcontrol-origin: padding;
    subcontrol-position: bottom right;
}

QToolButton::menu-button {
    border: 1px solid #5a5a5a;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    width: 16px;
}

QToolButton::menu-button:hover {
    border-color: #007acc;
}
```

---

## QSlider

Slider control with groove (track) and handle (thumb).

**Supported Properties:**
- Box model
- For horizontal: `min-width`, `height`
- For vertical: `min-height`, `width`

**Sub-Controls:**

#### `::groove:horizontal` / `::groove:vertical`
The slider track.

**Properties:**
- Box model (border, background)
- `height` (horizontal) or `width` (vertical)

**Positioning:** Positioned in widget's contents rectangle

**Example:**
```css
QSlider::groove:horizontal {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    height: 6px;
    border-radius: 3px;
}

QSlider::groove:vertical {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    width: 6px;
    border-radius: 3px;
}
```

#### `::handle:horizontal` / `::handle:vertical`
The draggable slider thumb.

**Properties:**
- Box model
- `width`, `height`
- `margin` (negative margin to overlap groove)

**Positioning:** Moves within groove

**Pseudo-States:**
- `:hover` - Mouse over handle
- `:pressed` - Being dragged
- `:disabled` - Disabled state

**Example:**
```css
QSlider::handle:horizontal {
    background-color: #007acc;
    border: 1px solid #007acc;
    width: 14px;
    height: 14px;
    margin: -5px 0; /* Vertical margin to center on groove */
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background-color: #1177bb;
}

QSlider::handle:horizontal:pressed {
    background-color: #0d5a8f;
}

QSlider::handle:vertical {
    background-color: #007acc;
    border: 1px solid #007acc;
    width: 14px;
    height: 14px;
    margin: 0 -5px; /* Horizontal margin to center on groove */
    border-radius: 7px;
}
```

#### `::add-page:horizontal` / `::add-page:vertical`
Groove area after the handle (right/bottom).

**Properties:** Background color

**Example:**
```css
QSlider::add-page:horizontal {
    background-color: #2c2c2c;
}

QSlider::add-page:vertical {
    background-color: #2c2c2c;
}
```

#### `::sub-page:horizontal` / `::sub-page:vertical`
Groove area before the handle (left/top). Often used for "filled" progress indicator.

**Properties:** Background color

**Example:**
```css
QSlider::sub-page:horizontal {
    background-color: #007acc;
    border-radius: 3px;
}

QSlider::sub-page:vertical {
    background-color: #007acc;
    border-radius: 3px;
}
```

**Pseudo-States:**
- `:horizontal` - Horizontal orientation
- `:vertical` - Vertical orientation
- `:disabled` - Disabled state
- `:enabled` - Enabled state
- `:focus` - Has keyboard focus

**Complete Example:**
```css
/* Horizontal Slider */
QSlider:horizontal {
    min-width: 200px;
    height: 30px;
}

QSlider::groove:horizontal {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    height: 6px;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background-color: #007acc;
    border-radius: 3px;
}

QSlider::add-page:horizontal {
    background-color: #2c2c2c;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #007acc;
    border: 1px solid #005999;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #1177bb;
}

QSlider::handle:horizontal:pressed {
    background-color: #0d5a8f;
}

/* Vertical Slider */
QSlider:vertical {
    min-height: 200px;
    width: 30px;
}

QSlider::groove:vertical {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    width: 6px;
    border-radius: 3px;
}

QSlider::sub-page:vertical {
    background-color: #007acc;
    border-radius: 3px;
}

QSlider::add-page:vertical {
    background-color: #2c2c2c;
    border-radius: 3px;
}

QSlider::handle:vertical {
    background-color: #007acc;
    border: 1px solid #005999;
    width: 16px;
    height: 16px;
    margin: 0 -6px;
    border-radius: 8px;
}

QSlider::handle:vertical:hover {
    background-color: #1177bb;
}
```

---

## QHeaderView

Header for QTableView/QTreeView showing column/row headers.

**Supported Properties:**
- Box model
- Text properties

**Sub-Controls:**

#### `::section`
Individual header sections (columns/rows).

**Properties:**
- Full box model
- Text properties
- `background-color`, `background-image`

**Pseudo-States:**
- `:first`, `:last`, `:middle`, `:only-one` - Section position
- `:next-selected`, `:previous-selected` - Adjacent to selected section
- `:selected` - Section is selected
- `:checked` - Section is checked (sortable)
- `:horizontal`, `:vertical` - Header orientation

**Example:**
```css
QHeaderView::section {
    background-color: #2d2d30;
    color: #cccccc;
    padding: 6px;
    border: 1px solid #3d3d3d;
    border-top: none;
    border-left: none;
}

QHeaderView::section:horizontal {
    border-right: 1px solid #3d3d3d;
}

QHeaderView::section:vertical {
    border-bottom: 1px solid #3d3d3d;
}

QHeaderView::section:first {
    border-left: none;
}

QHeaderView::section:last {
    border-right: none;
}

QHeaderView::section:hover {
    background-color: #3e3e42;
}

QHeaderView::section:checked {
    background-color: #094771;
}

QHeaderView::section:selected {
    background-color: #007acc;
}
```

#### `::up-arrow`
Sort indicator (ascending).

**Properties:**
- `image`
- `width`, `height`
- `subcontrol-origin`, `subcontrol-position`

**Example:**
```css
QHeaderView::up-arrow {
    image: url(up-arrow.png);
    height: 10px;
    width: 10px;
}
```

#### `::down-arrow`
Sort indicator (descending).

**Properties:** Same as `::up-arrow`

**Example:**
```css
QHeaderView::down-arrow {
    image: url(down-arrow.png);
    height: 10px;
    width: 10px;
}

/* Using CSS triangles instead of images */
QHeaderView::up-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 6px solid #cccccc;
}

QHeaderView::down-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #cccccc;
}
```

---

## Additional Widgets

### QComboBox

**Sub-Controls:**
- `::drop-down` - Dropdown button area
- `::down-arrow` - Arrow icon in dropdown
- `QComboBox QAbstractItemView` - Dropdown menu styling

**Example:**
```css
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #5a5a5a;
}

QComboBox::down-arrow {
    image: url(down-arrow.png);
}
```

### QScrollBar

**Sub-Controls:**
- `::handle:horizontal` / `::handle:vertical` - Draggable thumb
- `::add-line:horizontal` / `::add-line:vertical` - Bottom/right button
- `::sub-line:horizontal` / `::sub-line:vertical` - Top/left button
- `::add-page:horizontal` / `::add-page:vertical` - Area after handle
- `::sub-page:horizontal` / `::sub-page:vertical` - Area before handle
- `::up-arrow`, `::down-arrow`, `::left-arrow`, `::right-arrow` - Button arrows

**Example:**
```css
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 14px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background-color: #424242;
    min-height: 30px;
    border-radius: 7px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4e4e4e;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px; /* Hide scroll buttons */
}
```

### QProgressBar

**Sub-Controls:**
- `::chunk` - Filled portion of progress bar

**Example:**
```css
QProgressBar {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #007acc;
    border-radius: 3px;
}
```

### QGroupBox

**Sub-Controls:**
- `::title` - Group box title text
- `::indicator` - Checkbox (if checkable)

**Example:**
```css
QGroupBox {
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #1e1e1e;
}

QGroupBox::indicator {
    width: 18px;
    height: 18px;
}
```

### QCheckBox

**Sub-Controls:**
- `::indicator` - Checkbox square

**Pseudo-States:**
- `:checked`, `:unchecked`, `:indeterminate`
- `:hover`, `:pressed`, `:disabled`

**Example:**
```css
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #5a5a5a;
    border-radius: 3px;
    background-color: #3c3c3c;
}

QCheckBox::indicator:checked {
    background-color: #007acc;
    image: url(check.png);
}

QCheckBox::indicator:indeterminate {
    background-color: #007acc;
    image: url(indeterminate.png);
}
```

---

## Positioning Reference

### subcontrol-origin Values

Determines which rectangle of the parent element is used as the origin for positioning:

- `margin` - Margin rectangle (outermost)
- `border` - Border rectangle
- `padding` - Padding rectangle (default)
- `content` - Content rectangle (innermost)

### subcontrol-position Values

Alignment within the origin rectangle:

- `top left`, `top center`, `top right`
- `center left`, `center`, `center right`
- `bottom left`, `bottom center`, `bottom right`

### Position Schemes

**Relative Positioning:**
```css
QComboBox::drop-down {
    position: relative;
    top: 2px;  /* Offset from natural position */
    left: 2px;
}
```

**Absolute Positioning:**
```css
QComboBox::drop-down {
    position: absolute;
    top: 0px;    /* Distance from top edge */
    right: 0px;  /* Distance from right edge */
    width: 20px;
    height: 100%;
}
```

---

## Important Notes

### Critical Widget Styling Rules

1. **Complex Widgets:** When styling QComboBox, QScrollBar, QSpinBox, etc., if you customize one sub-control, you must customize all related sub-controls. The widget won't render properly with partial styling.

2. **Box Model:** Border is drawn between margin and padding. Padding is inside the border. Content is inside the padding.

3. **Background Attachment:** For scrollable widgets (QTableView, QTreeView, QTextEdit), use `background-attachment: fixed` to keep background image fixed while content scrolls.

4. **Border Images:** Use `border-image` for sub-controls like tree branches. It tiles/stretches the image to fill the element.

5. **Pseudo-State Chaining:** Chain pseudo-states for specific styling:
   ```css
   QPushButton:hover:!pressed { /* Hover but not pressed */ }
   QTreeView::branch:open:has-children:has-siblings { /* Very specific branch state */ }
   ```

6. **Specificity:** More specific selectors override general ones. Use widget names, object names, and pseudo-states to increase specificity.

7. **Image vs Background-Image:**
   - `image`: For sub-control icons (arrows, checkmarks)
   - `background-image`: For backgrounds that tile/stretch

8. **Creating Triangles (CSS Borders):**
   ```css
   /* Down arrow */
   width: 0;
   height: 0;
   border-left: 4px solid transparent;
   border-right: 4px solid transparent;
   border-top: 5px solid #cccccc;
   ```

---

## Testing & Debugging

**View Applied Stylesheet:**
```python
widget.styleSheet()  # Get current stylesheet
```

**Apply Stylesheet:**
```python
widget.setStyleSheet("QWidget { background-color: #000; }")
```

**Reload Stylesheet:**
```python
with open('theme.qss', 'r') as f:
    app.setStyleSheet(f.read())
```

**Debug Selector Matching:**
- Use `QApplication.setStyleSheet()` for global styles
- Use specific object names: `QWidget#myWidget { ... }`
- Check for typos in sub-control/pseudo-state names
- Remember: order matters! Later rules override earlier ones with same specificity

---

## Resources

- **Official Qt Documentation:** https://doc.qt.io/qt-6/stylesheet-reference.html
- **Syntax Guide:** https://doc.qt.io/qt-6/stylesheet-syntax.html
- **Examples:** https://doc.qt.io/qt-6/stylesheet-examples.html
- **Customization Guide:** https://doc.qt.io/qt-6/stylesheet-customizing.html

---

**Document Version:** 1.0
**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Project:** Theme_Editor - Qt Widget Theme Editor Module
