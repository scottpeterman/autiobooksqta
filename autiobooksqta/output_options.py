import os

from PyQt6.QtWidgets import QVBoxLayout, QDialog, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QCheckBox, \
    QGridLayout, QLabel, QComboBox, QDialogButtonBox, QFileDialog


class OutputOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Output Options")
        self.setMinimumWidth(450)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Destination folder selection
        folder_group = QGroupBox("Output Destination")
        folder_layout = QVBoxLayout(folder_group)

        folder_select_layout = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        self.folder_path.setPlaceholderText("Select destination folder...")

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.select_folder)

        folder_select_layout.addWidget(self.folder_path, 1)
        folder_select_layout.addWidget(browse_button)
        folder_layout.addLayout(folder_select_layout)

        # Format options
        format_group = QGroupBox("Output Format")
        format_layout = QVBoxLayout(format_group)

        # M4B creation (default to checked)
        self.create_m4b_checkbox = QCheckBox("Create M4B audiobook file")
        self.create_m4b_checkbox.setChecked(True)
        format_layout.addWidget(self.create_m4b_checkbox)

        # MP3 option
        self.create_mp3_checkbox = QCheckBox("Also create MP3 files")
        self.create_mp3_checkbox.setChecked(True)
        format_layout.addWidget(self.create_mp3_checkbox)

        # MP3 options (only enabled if MP3 is selected)
        mp3_options_layout = QGridLayout()
        mp3_options_layout.setContentsMargins(20, 0, 0, 0)

        # Bitrate selection
        mp3_options_layout.addWidget(QLabel("MP3 Quality:"), 0, 0)
        self.mp3_quality_combo = QComboBox()
        self.mp3_quality_combo.addItems(
            ["Low (64 kbps)", "Medium (128 kbps)", "High (192 kbps)", "Very High (256 kbps)"])
        self.mp3_quality_combo.setCurrentIndex(1)  # Default to medium
        mp3_options_layout.addWidget(self.mp3_quality_combo, 0, 1)

        format_layout.addLayout(mp3_options_layout)

        # Connect checkbox state to enable/disable MP3 options
        self.create_mp3_checkbox.stateChanged.connect(self.toggle_mp3_options)

        # Keep WAV files option
        self.keep_wav_checkbox = QCheckBox("Keep WAV files after conversion")
        self.keep_wav_checkbox.setChecked(False)
        self.keep_wav_checkbox.setVisible(False)
        format_layout.addWidget(self.keep_wav_checkbox)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Add all components to main layout
        layout.addWidget(folder_group)
        layout.addWidget(format_group)
        layout.addWidget(button_box)

        # Set default destination folder (current working directory)
        self.folder_path.setText(
            os.path.dirname(os.path.abspath(self.file_path)) if hasattr(self, 'file_path') else os.getcwd())

        # Initial state of MP3 options
        self.toggle_mp3_options()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.folder_path.setText(folder)

    def toggle_mp3_options(self):
        enabled = self.create_mp3_checkbox.isChecked()
        self.mp3_quality_combo.setEnabled(enabled)

    def get_options(self):
        return {
            'output_folder': self.folder_path.text(),
            'create_m4b': self.create_m4b_checkbox.isChecked(),
            'create_mp3': self.create_mp3_checkbox.isChecked(),
            'mp3_quality': self.mp3_quality_combo.currentText(),
            'keep_wav': self.keep_wav_checkbox.isChecked()
        }