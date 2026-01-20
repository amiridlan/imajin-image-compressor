"""
ProcessingLog - Real-time log widget for Imajin Image Processor

Displays per-file processing results with timestamps, icons, and statistics.
Supports auto-scroll, export to file, and color-coded entries.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from ui.styles.theme import Theme
import qtawesome as qta


class ProcessingLog(QWidget):
    """
    Scrollable log widget showing real-time processing updates

    Features:
    - Timestamp for each entry
    - Color-coded status icons (✓ success, ✗ error, ⚠ warning)
    - Rich text formatting
    - Auto-scroll to bottom
    - Export to text file
    - Clear log button
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(Theme.SPACING_SM)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Log text edit
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL))
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.WHITE};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                font-family: '{Theme.FONT_FAMILY}';
                padding: {Theme.SPACING_SM}px;
                color: {Theme.TEXT};
            }}
        """)

        main_layout.addWidget(self.log_text)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(Theme.SPACING_SM)

        # Clear button
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_log)
        self.clear_button.setToolTip("Clear all log entries")
        self._apply_button_style(self.clear_button)

        # Export button
        self.export_button = QPushButton("Export Log")
        self.export_button.clicked.connect(self.export_log)
        self.export_button.setToolTip("Export log to text file")
        self._apply_button_style(self.export_button)

        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # Entry counter
        self.entry_count = 0

    def _apply_button_style(self, button):
        """Apply styling to log buttons"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_SM}px;
                padding: {Theme.SPACING_XS}px {Theme.SPACING_SM}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-size: {Theme.FONT_SIZE_SMALL}px;
            }}

            QPushButton:hover {{
                background-color: {Theme.ACCENT};
            }}

            QPushButton:pressed {{
                background-color: {Theme.TEXT};
                color: {Theme.BG_PRIMARY};
            }}
        """)

    def add_entry(self, success, filename, message, stats=None):
        """
        Add a log entry

        Args:
            success: True for success, False for error, None for warning
            filename: Name of the file being processed
            message: Status message
            stats: Optional dict with 'original_size', 'new_size', 'reduction'
        """
        # Get current time
        timestamp = QTime.currentTime().toString("HH:mm:ss")

        # Choose icon and color based on status
        if success is True:
            icon = "✓"
            color = Theme.SUCCESS
        elif success is False:
            icon = "✗"
            color = Theme.ERROR
        else:  # Warning/info
            icon = "⚠"
            color = Theme.WARNING

        # Build entry text
        entry_parts = [f"[{timestamp}]", icon, filename, "→", message]

        # Add statistics if provided
        if stats and 'reduction' in stats:
            orig_mb = stats.get('original_size', 0) / (1024 * 1024)
            new_mb = stats.get('new_size', 0) / (1024 * 1024)
            reduction = stats.get('reduction', 0)
            stats_text = f"({orig_mb:.2f}MB → {new_mb:.2f}MB, {reduction:.1f}% reduction)"
            entry_parts.append(stats_text)

        entry_text = " ".join(entry_parts)

        # Get cursor at end of document
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Create format for colored text
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        format.setFont(QFont(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL))

        # Insert entry with formatting
        cursor.insertText(entry_text + "\n", format)

        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        self.entry_count += 1

    def add_success(self, filename, message, stats=None):
        """Add a success entry"""
        self.add_entry(True, filename, message, stats)

    def add_error(self, filename, error_message):
        """Add an error entry"""
        self.add_entry(False, filename, f"Error: {error_message}")

    def add_warning(self, filename, warning_message):
        """Add a warning entry"""
        self.add_entry(None, filename, warning_message)

    def add_info(self, message):
        """Add a general info message (no filename)"""
        timestamp = QTime.currentTime().toString("HH:mm:ss")
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        format = QTextCharFormat()
        format.setForeground(QColor(Theme.INFO))
        format.setFont(QFont(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL))

        cursor.insertText(f"[{timestamp}] ℹ {message}\n", format)

        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """Clear all log entries"""
        self.log_text.clear()
        self.entry_count = 0

    def export_log(self):
        """Export log to a text file"""
        if self.entry_count == 0:
            return

        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            "processing_log.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.add_info(f"Log exported to {file_path}")
            except Exception as e:
                self.add_error("Export", str(e))

    def get_entry_count(self):
        """Get number of log entries"""
        return self.entry_count

    def is_empty(self):
        """Check if log is empty"""
        return self.entry_count == 0
