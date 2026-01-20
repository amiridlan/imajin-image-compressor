"""
ConflictDialog - File conflict resolution dialog for Imajin Image Processor

Allows users to choose how to handle existing files in the output folder.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QRadioButton, QCheckBox, QPushButton,
                              QScrollArea, QWidget, QButtonGroup)
from PyQt6.QtCore import Qt
from ui.styles.theme import Theme
from core.conflict_checker import format_file_size, format_modified_date


class ConflictDialog(QDialog):
    """
    Dialog for resolving file conflicts

    Shows list of conflicting files and allows user to choose strategy:
    - Replace: Overwrite existing files
    - Skip: Skip files that already exist
    - Auto-rename: Create new files with suffix (_1, _2, etc.)
    """

    def __init__(self, conflicts, parent=None):
        """
        Initialize the conflict dialog

        Args:
            conflicts: List of conflict dicts from conflict_checker
            parent: Parent widget
        """
        super().__init__(parent)
        self.conflicts = conflicts
        self.selected_strategy = 'replace'  # Default
        self.remember_choice = False

        self.setWindowTitle("File Conflicts Detected")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.init_ui()
        self._apply_style()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING_MD)
        layout.setContentsMargins(Theme.SPACING_LG, Theme.SPACING_LG,
                                  Theme.SPACING_LG, Theme.SPACING_LG)

        # Header
        header = QLabel(f"⚠ {len(self.conflicts)} file(s) already exist in output folder")
        header.setFont(Theme.get_qfont(Theme.FONT_SIZE_LARGE, bold=True))
        header.setStyleSheet(f"""
            color: {Theme.WARNING};
            padding: {Theme.SPACING_SM}px;
            background-color: {Theme.lighten_color(Theme.WARNING, 0.8)};
            border-radius: {Theme.RADIUS_MD}px;
        """)
        layout.addWidget(header)

        # Conflict list (scrollable)
        self.create_conflict_list(layout)

        # Strategy selection
        self.create_strategy_selection(layout)

        # Remember choice checkbox
        self.remember_checkbox = QCheckBox("Remember choice for this session")
        self.remember_checkbox.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL))
        self.remember_checkbox.setStyleSheet(f"color: {Theme.TEXT};")
        layout.addWidget(self.remember_checkbox)

        # Buttons
        self.create_buttons(layout)

    def create_conflict_list(self, parent_layout):
        """Create scrollable list of conflicts"""
        scroll_label = QLabel("The following files will be affected:")
        scroll_label.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL, bold=True))
        scroll_label.setStyleSheet(f"color: {Theme.TEXT};")
        parent_layout.addWidget(scroll_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {Theme.WHITE};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
            }}
        """)

        conflict_widget = QWidget()
        conflict_layout = QVBoxLayout(conflict_widget)
        conflict_layout.setSpacing(Theme.SPACING_SM)
        conflict_layout.setContentsMargins(Theme.SPACING_SM, Theme.SPACING_SM,
                                          Theme.SPACING_SM, Theme.SPACING_SM)

        for conflict in self.conflicts:
            item = self._create_conflict_item(conflict)
            conflict_layout.addWidget(item)

        conflict_layout.addStretch()

        scroll.setWidget(conflict_widget)
        parent_layout.addWidget(scroll)

    def _create_conflict_item(self, conflict):
        """Create a single conflict item widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(Theme.SPACING_SM, Theme.SPACING_SM,
                                  Theme.SPACING_SM, Theme.SPACING_SM)
        layout.setSpacing(2)

        # Filename
        filename = conflict.get('output_filename', os.path.basename(conflict['output']))
        filename_label = QLabel(f"• {filename}")
        filename_label.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL, bold=True))
        filename_label.setStyleSheet(f"color: {Theme.TEXT};")

        # Modified date and size
        modified = format_modified_date(conflict.get('existing_modified', 0))
        size = format_file_size(conflict.get('existing_size', 0))
        info_label = QLabel(f"  Modified: {modified}  |  Size: {size}")
        info_label.setFont(Theme.get_qfont(Theme.FONT_SIZE_SMALL))
        info_label.setStyleSheet(f"color: {Theme.darken_color(Theme.TEXT, 0.3)};")

        layout.addWidget(filename_label)
        layout.addWidget(info_label)

        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.BG_PRIMARY};
                border-radius: {Theme.RADIUS_SM}px;
            }}
        """)

        return widget

    def create_strategy_selection(self, parent_layout):
        """Create strategy radio buttons"""
        strategy_label = QLabel("Choose action:")
        strategy_label.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL, bold=True))
        strategy_label.setStyleSheet(f"color: {Theme.TEXT}; margin-top: {Theme.SPACING_SM}px;")
        parent_layout.addWidget(strategy_label)

        self.strategy_group = QButtonGroup(self)

        # Replace option
        self.replace_radio = QRadioButton("Replace all existing files")
        self.replace_radio.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL))
        self.replace_radio.setStyleSheet(f"color: {Theme.TEXT};")
        self.replace_radio.setChecked(True)  # Default
        self.strategy_group.addButton(self.replace_radio, 0)

        # Skip option
        self.skip_radio = QRadioButton("Skip existing files")
        self.skip_radio.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL))
        self.skip_radio.setStyleSheet(f"color: {Theme.TEXT};")
        self.strategy_group.addButton(self.skip_radio, 1)

        # Auto-rename option
        self.rename_radio = QRadioButton("Auto-rename (file_1.jpg, file_2.jpg, ...)")
        self.rename_radio.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL))
        self.rename_radio.setStyleSheet(f"color: {Theme.TEXT};")
        self.strategy_group.addButton(self.rename_radio, 2)

        parent_layout.addWidget(self.replace_radio)
        parent_layout.addWidget(self.skip_radio)
        parent_layout.addWidget(self.rename_radio)

    def create_buttons(self, parent_layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(Theme.SPACING_SM)
        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL, bold=True))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.SPACING_SM}px {Theme.SPACING_LG}px;
                font-family: '{Theme.FONT_FAMILY}';
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
            }}
        """)

        # Continue button
        continue_btn = QPushButton("Continue Processing")
        continue_btn.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL, bold=True))
        continue_btn.clicked.connect(self.accept)
        continue_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: {Theme.TEXT};
                border: {Theme.BORDER_THICK}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.SPACING_SM}px {Theme.SPACING_LG}px;
                font-family: '{Theme.FONT_FAMILY}';
            }}
            QPushButton:hover {{
                background-color: {Theme.TEXT};
                color: {Theme.ACCENT};
            }}
        """)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(continue_btn)

        parent_layout.addLayout(button_layout)

    def _apply_style(self):
        """Apply dialog styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BG_PRIMARY};
                font-family: '{Theme.FONT_FAMILY}';
            }}
        """)

    def get_strategy(self):
        """
        Get selected conflict resolution strategy

        Returns:
            'replace', 'skip', or 'auto_rename'
        """
        if self.skip_radio.isChecked():
            return 'skip'
        elif self.rename_radio.isChecked():
            return 'auto_rename'
        else:
            return 'replace'

    def should_remember(self):
        """
        Check if user wants to remember choice

        Returns:
            bool
        """
        return self.remember_checkbox.isChecked()
