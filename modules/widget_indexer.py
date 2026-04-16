"""
Widget Indexer for Theme_Editor
================================
Scans modules/ directory and builds:
  1. Full index  (config/widget_index.json) — every class that mentions the widget
  2. Visible UI index (config/widget_visible_index.json) — only navigable UI
     components (Editor, UI, Dialog, Window) found in modules/
  3. Navigation tree (config/nav_tree.json) — parent/child hierarchy built from
     addTab() calls in main.py and modules/, with accurate per-method widget detection

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
_MAIN_PY_PATH       = _BASE_DIR / "main.py"
_NAV_TREE_PATH      = _BASE_DIR / "config" / "nav_tree.json"

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


# ── Navigation tree ──────────────────────────────────────────────────────────
# Scans main.py for top-level tabs and modules/*.py for .addTab() calls to
# build the full parent→child hierarchy with real display labels.


def _strip_label(class_name: str) -> str:
    """'JSONTerminalEditor' → 'JSON Terminal', 'ConverterUI' → 'Converter'"""
    for suffix in ("Editor", "UI", "Dialog", "Window"):
        if class_name.endswith(suffix):
            raw = class_name[: -len(suffix)]
            return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", raw).strip()
    return class_name


def _split_class_chunks(src: str) -> list[tuple[str, str]]:
    """Return [(class_name, class_body_text)] for every class in src."""
    starts = [
        (m.start(), m.group(1))
        for m in re.finditer(r"^class\s+([A-Za-z_]\w*)", src, re.MULTILINE)
    ]
    if not starts:
        return []
    return [
        (name, src[pos: starts[i + 1][0] if i + 1 < len(starts) else len(src)])
        for i, (pos, name) in enumerate(starts)
    ]


def _extract_method_body(src: str, method_name: str) -> str:
    """Return the source text of a named method, or '' if not found."""
    m = re.search(r"\bdef\s+" + re.escape(method_name) + r"\s*\(", src)
    if not m:
        return ""
    line_start = src.rfind("\n", 0, m.start()) + 1
    base_indent = m.start() - line_start
    lines = src[m.start():].split("\n")
    body = [lines[0]]
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped and not stripped.startswith("#"):
            if (len(line) - len(stripped)) <= base_indent:
                break
        body.append(line)
    return "\n".join(body)


def build_navigation_tree() -> list[dict]:
    """
    Build a full navigation hierarchy by scanning main.py (top-level tabs)
    and all modules/*.py (addTab calls within editor classes).

    Each entry: {"id", "label", "type", "parent_id", "parent_label",
                 "source_class", "builder"}
      - id:           class name OR "ParentClass::Label" for anonymous subtabs
      - source_class: class whose file contains the widget code
      - builder:      method name to scan for widgets (anonymous subtabs only)
    """
    nav: dict[str, dict] = {}

    # ── Step 1: top-level tabs from ThemeEditorMainWindow in main.py ──────────
    if _MAIN_PY_PATH.exists():
        src = _MAIN_PY_PATH.read_text(encoding="utf-8", errors="ignore")

        # Build attr_map: self.attr → {class, builder}
        attr_map: dict[str, dict] = {}
        for am in re.finditer(
            r"self\.(\w+)\s*=\s*(?:self\.(\w+)\s*\(|([A-Z][A-Za-z]\w*)\s*\()",
            src,
        ):
            attr = am.group(1)
            if am.group(2):
                attr_map[attr] = {"builder": am.group(2), "class": None}
            else:
                attr_map[attr] = {"builder": None, "class": am.group(3)}

        for tab_m in re.finditer(
            r"\.addTab\s*\(\s*([^,]+?)\s*,\s*['\"]([^'\"]+)['\"]",
            src,
        ):
            widget_expr = tab_m.group(1).strip()
            tab_label   = tab_m.group(2).strip()
            if not tab_label:
                continue

            child_cls = None
            # Case A: ClassName(...)
            ma = re.match(r"([A-Z][A-Za-z]\w*)\s*\(", widget_expr)
            if ma:
                child_cls = ma.group(1)
            # Case C: self.attr
            elif re.match(r"self\.(\w+)$", widget_expr):
                mc   = re.match(r"self\.(\w+)$", widget_expr)
                info = attr_map.get(mc.group(1))
                if info and info["class"]:
                    child_cls = info["class"]

            if child_cls and child_cls not in nav:
                nav[child_cls] = {
                    "id":           child_cls,
                    "label":        tab_label,
                    "type":         "Tab",
                    "parent_id":    None,
                    "parent_label": None,
                    "source_class": child_cls,
                    "builder":      None,
                }

    # ── Step 2: scan modules/*.py for addTab calls (sub-editors / panels) ─────
    for py_file in sorted(_MODULES_DIR.glob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        try:
            src = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for cls_name, cls_body in _split_class_chunks(src):
            parent_entry = nav.get(cls_name)
            parent_label = parent_entry["label"] if parent_entry else _strip_label(cls_name)

            # Map: self.attr → {class, builder}
            attr_map: dict[str, dict] = {}
            for am in re.finditer(
                r"self\.(\w+)\s*=\s*(?:self\.(\w+)\s*\(|([A-Z][A-Za-z]\w*)\s*\()",
                cls_body,
            ):
                attr = am.group(1)
                if am.group(2):
                    attr_map[attr] = {"builder": am.group(2), "class": None}
                else:
                    attr_map[attr] = {"builder": None, "class": am.group(3)}

            # Map: local_var → ClassName
            local_var_map: dict[str, str] = {}
            for lm in re.finditer(
                r"^\s+(\w+)\s*=\s*([A-Z][A-Za-z]\w*)\s*\(",
                cls_body,
                re.MULTILINE,
            ):
                local_var_map[lm.group(1)] = lm.group(2)

            for tab_m in re.finditer(
                r"\.addTab\s*\(\s*([^,]+?)\s*,\s*['\"]([^'\"]+)['\"]",
                cls_body,
            ):
                widget_expr = tab_m.group(1).strip()
                tab_label   = tab_m.group(2).strip()
                if not tab_label:
                    continue

                child_id   = None
                source_cls = cls_name
                builder    = None

                # Case A: ClassName(...)
                ma = re.match(r"([A-Z][A-Za-z]\w*)\s*\(", widget_expr)
                if ma:
                    child_id   = ma.group(1)
                    source_cls = ma.group(1)

                # Case B: self.method(...)
                elif re.match(r"self\.(\w+)\s*\(", widget_expr):
                    mb      = re.match(r"self\.(\w+)\s*\(", widget_expr)
                    builder = mb.group(1)
                    child_id = f"{cls_name}::{tab_label}"

                # Case C: self.attr
                elif re.match(r"self\.(\w+)$", widget_expr):
                    mc   = re.match(r"self\.(\w+)$", widget_expr)
                    info = attr_map.get(mc.group(1))
                    if info and info["class"]:
                        child_id   = info["class"]
                        source_cls = info["class"]
                    elif info and info["builder"]:
                        builder  = info["builder"]
                        child_id = f"{cls_name}::{tab_label}"
                    else:
                        child_id = f"{cls_name}::{tab_label}"

                # Case D: local variable
                elif re.match(r"^\w+$", widget_expr):
                    named = local_var_map.get(widget_expr)
                    if named:
                        child_id   = named
                        source_cls = named
                    else:
                        child_id = f"{cls_name}::{tab_label}"

                else:
                    continue

                if child_id not in nav:
                    nav[child_id] = {
                        "id":           child_id,
                        "label":        tab_label,
                        "type":         "SubTab",
                        "parent_id":    cls_name,
                        "parent_label": parent_label,
                        "source_class": source_cls,
                        "builder":      builder,
                    }
                elif nav[child_id].get("parent_id") is None:
                    nav[child_id]["parent_id"]    = cls_name
                    nav[child_id]["parent_label"] = parent_label

    return list(nav.values())


def get_widgets_for_nav_entry(entry: dict) -> list[str]:
    """Return Qt widget class names used in a specific navigation entry.

    For anonymous subtabs (builder method given), scans only that method body.
    For named-class entries, scans the whole class file.
    """
    source_cls = entry.get("source_class")
    builder    = entry.get("builder")

    if not source_cls:
        return []

    src_text = ""
    for py_file in _MODULES_DIR.glob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            txt = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if re.search(r"^class\s+" + re.escape(source_cls) + r"\b", txt, re.MULTILINE):
            src_text = txt
            break

    if not src_text:
        return []

    scan_src = _extract_method_body(src_text, builder) if builder else src_text
    if not scan_src:
        scan_src = src_text

    found = []
    for widget in INDEXED_WIDGETS:
        pattern = _DETECTION_OVERRIDES.get(widget, r"\b" + re.escape(widget) + r"\b")
        if re.search(pattern, scan_src):
            found.append(widget)
    return found


def build_entries_by_qt_class() -> dict[str, list[dict]]:
    """Build {qt_class: [nav_entries]} with accurate per-method-body detection.

    Unlike using vis_idx (whole-file), this scans only the specific builder
    method body for anonymous subtabs, giving accurate per-panel widget lists.
    """
    nav_tree = load_navigation_tree()

    # Preload all module source files keyed by class name (read each file once)
    _file_cache: dict[str, str] = {}
    for py_file in _MODULES_DIR.glob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            txt = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for cls in re.findall(r"^class\s+([A-Za-z_]\w*)", txt, re.MULTILINE):
            _file_cache[cls] = txt

    result: dict[str, list[dict]] = {}
    seen: set[tuple] = set()

    for entry in nav_tree:
        source_cls = entry.get("source_class")
        builder    = entry.get("builder")
        if not source_cls:
            continue
        src_text = _file_cache.get(source_cls, "")
        if not src_text:
            continue
        scan_src = _extract_method_body(src_text, builder) if builder else src_text
        if not scan_src:
            scan_src = src_text

        for widget in INDEXED_WIDGETS:
            pattern = _DETECTION_OVERRIDES.get(widget, r"\b" + re.escape(widget) + r"\b")
            if re.search(pattern, scan_src):
                key = (widget, entry["id"])
                if key not in seen:
                    seen.add(key)
                    result.setdefault(widget, []).append(entry)

    return result


def save_navigation_tree(tree: list[dict]) -> None:
    """Persist the navigation tree to config/nav_tree.json."""
    _NAV_TREE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_NAV_TREE_PATH, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)
    logger.info("Navigation tree saved to %s", _NAV_TREE_PATH)


def load_navigation_tree() -> list[dict]:
    """Load cached navigation tree; rebuild if missing."""
    if _NAV_TREE_PATH.exists():
        try:
            data = json.loads(_NAV_TREE_PATH.read_text(encoding="utf-8"))
            if data:
                return data
        except Exception:
            pass
    tree = build_navigation_tree()
    save_navigation_tree(tree)
    return tree


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

    print("Building navigation tree…")
    tree = build_navigation_tree()
    save_navigation_tree(tree)
    print(f"Nav tree → {_NAV_TREE_PATH}  ({len(tree)} entries)")
    print()
    for e in sorted(tree, key=lambda x: (x.get("parent_id") or "", x["label"])):
        indent = "  " if e.get("parent_id") else ""
        parent = f"  ← {e['parent_label']}" if e.get("parent_label") else ""
        print(f"  {indent}{e['type']:8s}  {e['label']}{parent}")

    print()
    for widget in INDEXED_WIDGETS:
        vis_locs = vis.get(widget, [])
        vis_n = len(vis_locs)
        print(f"  {widget:20s}  visible={vis_n:2d} — "
              f"{', '.join(vis_locs[:4])}{'…' if vis_n > 4 else ''}")
