"""
Widget Indexer for Theme_Editor
================================
Scans modules/ directory and builds:
  1. Full index  (config/widget_index.json) — every class that mentions the widget
  2. Visible UI index (config/widget_visible_index.json) — only navigable UI
     components (Editor, UI, Dialog, Window) found in modules/

Detection overrides handle implicitly-used widgets:
  QToolTip  → used via .setToolTip(), not instantiated directly
  QScrollBar → auto-created inside QScrollArea
  QTabBar    → auto-created inside QTabWidget

Run as a script to regenerate both files:
    python -m modules.widget_indexer
"""

from __future__ import annotations

import json
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Qt widget types to index
INDEXED_WIDGETS: list[str] = [
    "QPushButton",
    "QToolButton",
    "QLabel",
    "QLineEdit",
    "QTextEdit",
    "QPlainTextEdit",
    "QComboBox",
    "QCheckBox",
    "QRadioButton",
    "QListWidget",
    "QTableWidget",
    "QTreeWidget",
    "QGroupBox",
    "QSpinBox",
    "QTabWidget",
    "QTabBar",
    "QSplitter",
    "QScrollArea",
    "QScrollBar",
    "QProgressBar",
    "QSlider",
    "QFrame",
    "QDialog",
    "QStatusBar",
    "QToolTip",
    "QMenuBar",
    "QMenu",
]

_BASE_DIR           = Path(__file__).parent.parent           # Theme_Editor root
_MODULES_DIR        = Path(__file__).parent                  # modules/
_INDEX_PATH         = _BASE_DIR / "config" / "widget_index.json"
_VISIBLE_INDEX_PATH = _BASE_DIR / "config" / "widget_visible_index.json"

# Class name suffixes that indicate a user-visible, navigable UI component
# JSONTerminalEditor, QSSThemeEditor, ConverterUI, SettingsDialog …
_NAVIGABLE_SUFFIXES = ("Editor", "UI", "Dialog", "Window")

# Detection overrides for implicitly-used widgets
_DETECTION_OVERRIDES: dict[str, str] = {
    "QToolTip":   r"\.setToolTip\s*\(",
    "QScrollBar": r"\b(QScrollArea|QScrollBar)\b",
    "QTabBar":    r"\b(QTabWidget|QTabBar)\b",
}

# Classes that should be excluded from "used in" results (internal helpers)
_SKIP_CLASSES = {
    "ColorPickerButton", "QtWidgetPreviewPanel", "ThemeConverter",
}


# ── Full widget index ─────────────────────────────────────────────────────────

def build_widget_index() -> dict[str, list[str]]:
    """Scan modules/ and return {WidgetType: sorted list of class names}."""
    index: dict[str, set[str]] = {w: set() for w in INDEXED_WIDGETS}

    for py_file in sorted(_MODULES_DIR.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        class_names = re.findall(r"^class\s+([A-Za-z_]\w*)", source, re.MULTILINE)
        if not class_names:
            class_names = [py_file.stem]

        for widget in INDEXED_WIDGETS:
            if re.search(r"\b" + re.escape(widget) + r"\b", source):
                for cn in class_names:
                    if cn not in _SKIP_CLASSES:
                        index[widget].add(cn)

    return {w: sorted(v) for w, v in index.items()}


def save_widget_index(index: dict[str, list[str]]) -> None:
    _INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    logger.info("Widget index saved to %s", _INDEX_PATH)


def load_widget_index() -> dict[str, list[str]]:
    if _INDEX_PATH.exists():
        try:
            data = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
            if data:
                return data
        except Exception:
            pass
    index = build_widget_index()
    save_widget_index(index)
    return index


# ── Visible UI index ──────────────────────────────────────────────────────────

def build_visible_ui_index() -> dict[str, list[str]]:
    """Scan modules/ and return only *navigable* UI class names.

    Navigable = ends with Editor, UI, Dialog, or Window.
    Uses detection overrides for implicitly-used widgets.
    """
    index: dict[str, set[str]] = {w: set() for w in INDEXED_WIDGETS}

    for py_file in sorted(_MODULES_DIR.glob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        all_classes = re.findall(r"^class\s+([A-Za-z_]\w*)", source, re.MULTILINE)
        nav_classes = [
            c for c in all_classes
            if any(c.endswith(s) for s in _NAVIGABLE_SUFFIXES)
            and c not in _SKIP_CLASSES
        ]
        if not nav_classes:
            continue

        for widget in INDEXED_WIDGETS:
            pattern = _DETECTION_OVERRIDES.get(
                widget, r"\b" + re.escape(widget) + r"\b"
            )
            if re.search(pattern, source):
                for cn in nav_classes:
                    index[widget].add(cn)

    return {w: sorted(v) for w, v in index.items()}


def save_visible_ui_index(index: dict[str, list[str]]) -> None:
    _VISIBLE_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_VISIBLE_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    logger.info("Visible UI index saved to %s", _VISIBLE_INDEX_PATH)


def load_visible_ui_index() -> dict[str, list[str]]:
    if _VISIBLE_INDEX_PATH.exists():
        try:
            data = json.loads(_VISIBLE_INDEX_PATH.read_text(encoding="utf-8"))
            if data:
                return data
        except Exception:
            pass
    index = build_visible_ui_index()
    save_visible_ui_index(index)
    return index


# ── Human-readable helpers ────────────────────────────────────────────────────

def location_display_name(class_name: str) -> tuple[str, str]:
    """Return (human_name, type_badge) for a navigable UI class.

    Examples:
        JSONTerminalEditor  → ("JSON Terminal", "editor")
        ConverterUI         → ("Converter",     "ui")
        SettingsDialog      → ("Settings",      "dialog")
    """
    for suffix, badge in (
        ("Editor", "editor"),
        ("UI",     "ui"),
        ("Dialog", "dialog"),
        ("Window", "window"),
    ):
        if class_name.endswith(suffix):
            raw = class_name[:-len(suffix)]
            name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', raw)
            return name, badge
    return class_name, ""


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Scanning modules/ (full index)…")
    idx = build_widget_index()
    save_widget_index(idx)
    print(f"Full index → {_INDEX_PATH}")

    print("Scanning modules/ (visible UI index)…")
    vis = build_visible_ui_index()
    save_visible_ui_index(vis)
    print(f"Visible index → {_VISIBLE_INDEX_PATH}")

    print()
    for widget in INDEXED_WIDGETS:
        vis_locs = vis.get(widget, [])
        vis_n = len(vis_locs)
        print(f"  {widget:20s}  visible={vis_n:2d} — "
              f"{', '.join(vis_locs[:4])}{'…' if vis_n > 4 else ''}")
