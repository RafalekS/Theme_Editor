"""
Preview Widgets
Live preview components for different theme formats
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor


class TerminalPreviewWidget(QWidget):
    """
    Preview terminal output with theme colors
    Shows sample terminal commands and output with ANSI color highlighting
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup preview UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Terminal Preview")
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(title)

        # Terminal output area
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Consolas", 10))
        self.terminal_output.setMinimumHeight(400)

        # Frame style for terminal
        self.terminal_frame = QFrame()
        frame_layout = QVBoxLayout(self.terminal_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self.terminal_output)

        layout.addWidget(self.terminal_frame)

        # Generate sample terminal content
        self._update_preview()

    def set_theme(self, theme):
        """
        Apply theme to terminal preview

        Args:
            theme: TerminalTheme object
        """
        self.current_theme = theme
        self._update_preview()

    def _update_preview(self):
        """Update terminal preview with current theme"""
        if self.current_theme is None:
            return

        # Set terminal background and foreground
        self.terminal_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.current_theme.background};
                color: {self.current_theme.foreground};
                border: 2px solid {self.current_theme.brightBlack};
                border-radius: 4px;
                padding: 10px;
            }}
        """)

        # Clear and rebuild content
        self.terminal_output.clear()
        cursor = self.terminal_output.textCursor()

        # Sample terminal content with colors
        self._add_prompt(cursor)
        self._add_text(cursor, "ls -la\n", self.current_theme.foreground)

        # Directory listing with colors
        self._add_text(cursor, "drwxr-xr-x  ", self.current_theme.brightBlack)
        self._add_text(cursor, "5 user user ", self.current_theme.foreground)
        self._add_text(cursor, "4096 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  8 12:00 ", self.current_theme.yellow)
        self._add_text(cursor, ".\n", self.current_theme.blue, bold=True)

        self._add_text(cursor, "drwxr-xr-x ", self.current_theme.brightBlack)
        self._add_text(cursor, "23 user user ", self.current_theme.foreground)
        self._add_text(cursor, "4096 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  7 18:30 ", self.current_theme.yellow)
        self._add_text(cursor, "..\n", self.current_theme.blue, bold=True)

        self._add_text(cursor, "-rw-r--r--  ", self.current_theme.brightBlack)
        self._add_text(cursor, "1 user user  ", self.current_theme.foreground)
        self._add_text(cursor, "220 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  1 09:15 ", self.current_theme.yellow)
        self._add_text(cursor, ".bashrc\n", self.current_theme.foreground)

        self._add_text(cursor, "-rwxr-xr-x  ", self.current_theme.brightBlack)
        self._add_text(cursor, "1 user user ", self.current_theme.foreground)
        self._add_text(cursor, "1024 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  8 08:00 ", self.current_theme.yellow)
        self._add_text(cursor, "main.py\n", self.current_theme.green, bold=True)

        self._add_text(cursor, "drwxr-xr-x  ", self.current_theme.brightBlack)
        self._add_text(cursor, "2 user user ", self.current_theme.foreground)
        self._add_text(cursor, "4096 ", self.current_theme.cyan)
        self._add_text(cursor, "Nov  7 14:22 ", self.current_theme.yellow)
        self._add_text(cursor, "modules\n", self.current_theme.blue, bold=True)

        cursor.insertText("\n")

        # Git status example
        self._add_prompt(cursor)
        self._add_text(cursor, "git status\n", self.current_theme.foreground)
        self._add_text(cursor, "On branch ", self.current_theme.foreground)
        self._add_text(cursor, "main\n", self.current_theme.cyan, bold=True)
        self._add_text(cursor, "Your branch is up to date with ", self.current_theme.foreground)
        self._add_text(cursor, "'origin/main'\n", self.current_theme.cyan)
        cursor.insertText("\n")

        self._add_text(cursor, "Changes not staged for commit:\n", self.current_theme.red, bold=True)
        self._add_text(cursor, "  modified:   ", self.current_theme.red)
        self._add_text(cursor, "main.py\n", self.current_theme.foreground)
        cursor.insertText("\n")

        self._add_text(cursor, "Untracked files:\n", self.current_theme.red, bold=True)
        self._add_text(cursor, "  ", self.current_theme.foreground)
        self._add_text(cursor, "modules/\n", self.current_theme.red)
        cursor.insertText("\n")

        # Success message
        self._add_prompt(cursor)
        self._add_text(cursor, "npm install\n", self.current_theme.foreground)
        self._add_text(cursor, "✓ ", self.current_theme.green, bold=True)
        self._add_text(cursor, "Successfully installed ", self.current_theme.foreground)
        self._add_text(cursor, "25 packages\n", self.current_theme.brightGreen, bold=True)
        cursor.insertText("\n")

        # Error message
        self._add_prompt(cursor)
        self._add_text(cursor, "python broken_script.py\n", self.current_theme.foreground)
        self._add_text(cursor, "Error: ", self.current_theme.brightRed, bold=True)
        self._add_text(cursor, "Module not found\n", self.current_theme.red)
        self._add_text(cursor, "  File ", self.current_theme.foreground)
        self._add_text(cursor, '"broken_script.py"', self.current_theme.yellow)
        self._add_text(cursor, ", line ", self.current_theme.foreground)
        self._add_text(cursor, "42\n", self.current_theme.cyan)
        cursor.insertText("\n")

        # ANSI color test
        self._add_prompt(cursor)
        self._add_text(cursor, "echo 'Color Test'\n", self.current_theme.foreground)

        # Normal colors
        self._add_text(cursor, "■ ", self.current_theme.black)
        self._add_text(cursor, "■ ", self.current_theme.red)
        self._add_text(cursor, "■ ", self.current_theme.green)
        self._add_text(cursor, "■ ", self.current_theme.yellow)
        self._add_text(cursor, "■ ", self.current_theme.blue)
        self._add_text(cursor, "■ ", self.current_theme.purple)
        self._add_text(cursor, "■ ", self.current_theme.cyan)
        self._add_text(cursor, "■ ", self.current_theme.white)
        self._add_text(cursor, " Normal\n", self.current_theme.foreground)

        # Bright colors
        self._add_text(cursor, "■ ", self.current_theme.brightBlack)
        self._add_text(cursor, "■ ", self.current_theme.brightRed)
        self._add_text(cursor, "■ ", self.current_theme.brightGreen)
        self._add_text(cursor, "■ ", self.current_theme.brightYellow)
        self._add_text(cursor, "■ ", self.current_theme.brightBlue)
        self._add_text(cursor, "■ ", self.current_theme.brightPurple)
        self._add_text(cursor, "■ ", self.current_theme.brightCyan)
        self._add_text(cursor, "■ ", self.current_theme.brightWhite)
        self._add_text(cursor, " Bright\n", self.current_theme.foreground)

        cursor.insertText("\n")
        self._add_prompt(cursor)

    def _add_prompt(self, cursor):
        """Add command prompt"""
        if self.current_theme:
            self._add_text(cursor, "user@host", self.current_theme.green, bold=True)
            self._add_text(cursor, ":", self.current_theme.foreground)
            self._add_text(cursor, "~/project", self.current_theme.blue, bold=True)
            self._add_text(cursor, "$ ", self.current_theme.foreground)

    def _add_text(self, cursor, text, color, bold=False):
        """
        Add colored text to terminal

        Args:
            cursor: QTextCursor
            text: Text to add
            color: Hex color string
            bold: Whether text should be bold
        """
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)

        cursor.insertText(text, fmt)
