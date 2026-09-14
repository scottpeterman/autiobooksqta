import os
import sys
import shutil
import urllib.request
import zipfile
import tempfile
import requests
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QProgressBar, QMessageBox, QCheckBox,
                             QHBoxLayout, QApplication)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class DownloadThread(QThread):
    """Thread for downloading files without blocking UI"""
    progress_updated = pyqtSignal(int)
    download_complete = pyqtSignal(str)
    download_error = pyqtSignal(str)

    def __init__(self, url, destination):
        super().__init__()
        self.url = url
        self.destination = destination

    def run(self):
        try:
            # Create a temporary file for download
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_file.close()

            def progress_callback(count, block_size, total_size):
                percent = int(count * block_size * 100 / total_size)
                self.progress_updated.emit(percent)

            # Download the file
            urllib.request.urlretrieve(self.url, temp_file.name, progress_callback)

            # Signal completion with temp file path
            self.download_complete.emit(temp_file.name)

        except Exception as e:
            self.download_error.emit(str(e))


class ExtractThread(QThread):
    """Thread for extracting ZIP files without blocking UI"""
    progress_updated = pyqtSignal(int)
    extraction_complete = pyqtSignal()
    extraction_error = pyqtSignal(str)

    def __init__(self, zip_path, extract_to):
        super().__init__()
        self.zip_path = zip_path
        self.extract_to = extract_to

    def run(self):
        try:
            # Open the zip file
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                # Get total file count for progress
                total_files = len(zip_ref.infolist())
                extracted = 0

                # Extract each file
                for file in zip_ref.infolist():
                    extracted += 1
                    percent = int(extracted * 100 / total_files)
                    self.progress_updated.emit(percent)

                    # Extract the file
                    zip_ref.extract(file, self.extract_to)

            self.extraction_complete.emit()

        except Exception as e:
            self.extraction_error.emit(str(e))
        finally:
            # Clean up the temp zip file
            try:
                os.unlink(self.zip_path)
            except:
                pass


class FFmpegPromptDialog(QDialog):
    """Dialog to prompt user about FFmpeg installation"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FFmpeg Required")
        self.setMinimumWidth(450)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Explanation text
        explanation = QLabel(
            "This application requires FFmpeg to create audiobooks. "
            "FFmpeg was not found on your system."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        # Options heading
        options_label = QLabel("Would you like to:")
        options_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(options_label)

        # Download option checkbox
        self.download_checkbox = QCheckBox("Download FFmpeg automatically (recommended)")
        self.download_checkbox.setChecked(True)
        layout.addWidget(self.download_checkbox)

        # Manual download info
        manual_label = QLabel(
            "Alternatively, you can download FFmpeg from the official sources:"
        )
        manual_label.setWordWrap(True)
        layout.addWidget(manual_label)

        # Links with better formatting
        links_label = QLabel(
            "• <a href='https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip'>Download FFmpeg from Github (recommended)</a><br>"
            "• <a href='https://ffmpeg.org/download.html'>Official FFmpeg Download Page</a>"
        )
        links_label.setOpenExternalLinks(True)
        links_label.setTextFormat(Qt.TextFormat.RichText)
        links_label.setWordWrap(True)
        layout.addWidget(links_label)

        # Manual instructions
        manual_instructions = QLabel(
            "If downloading manually, extract the zip file and ensure these files "
            "are in the same folder as this application:"
        )
        manual_instructions.setWordWrap(True)
        layout.addWidget(manual_instructions)

        # Required files
        files_label = QLabel("• ffmpeg.exe\n• ffplay.exe\n• ffprobe.exe")
        layout.addWidget(files_label)

        # Status for download process
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Button layout
        button_layout = QHBoxLayout()

        # Continue without FFmpeg
        self.skip_button = QPushButton("Continue Without FFmpeg")
        self.skip_button.setStyleSheet("color: #777;")
        button_layout.addWidget(self.skip_button)
        button_layout.addStretch()

        # Download or close buttons
        self.download_button = QPushButton("Download & Install FFmpeg")
        self.download_button.setStyleSheet(
            "background-color: #6b8e23; color: white; font-weight: bold; padding: 6px 12px;"
        )
        button_layout.addWidget(self.download_button)

        layout.addLayout(button_layout)

        # Connect signals
        self.download_button.clicked.connect(self.start_download)
        self.skip_button.clicked.connect(self.reject)
        self.download_checkbox.toggled.connect(self.update_button_text)

        # Initialize button text
        self.update_button_text(self.download_checkbox.isChecked())

    def update_button_text(self, checked):
        if checked:
            self.download_button.setText("Download & Install FFmpeg")
            self.download_button.setStyleSheet(
                "background-color: #6b8e23; color: white; font-weight: bold; padding: 6px 12px;"
            )
        else:
            self.download_button.setText("Close & Continue")
            self.download_button.setStyleSheet(
                "background-color: #4472C4; color: white; font-weight: bold; padding: 6px 12px;"
            )

    def start_download(self):
        # If checkbox is unchecked, just accept the dialog
        if not self.download_checkbox.isChecked():
            self.accept()
            return

        # Prepare UI for download
        self.status_label.setText("Downloading FFmpeg...")
        self.status_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.download_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.download_checkbox.setEnabled(False)

        # Start download thread
        # Use current working directory instead of script directory
        self.download_thread = DownloadThread(
            "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip",
            os.getcwd()
        )
        self.download_thread.progress_updated.connect(self.update_download_progress)
        self.download_thread.download_complete.connect(self.handle_download_complete)
        self.download_thread.download_error.connect(self.handle_download_error)
        self.download_thread.start()

    def update_download_progress(self, percent):
        self.progress_bar.setValue(percent)

    def handle_download_complete(self, zip_path):
        # Update UI for extraction
        self.status_label.setText("Extracting FFmpeg...")
        self.progress_bar.setValue(0)

        # Start extraction thread
        # Use current working directory instead of script directory
        self.extract_thread = ExtractThread(
            zip_path,
            os.getcwd()
        )
        self.extract_thread.progress_updated.connect(self.update_extract_progress)
        self.extract_thread.extraction_complete.connect(self.handle_extraction_complete)
        self.extract_thread.extraction_error.connect(self.handle_extraction_error)
        self.extract_thread.start()

    def update_extract_progress(self, percent):
        self.progress_bar.setValue(percent)

    def handle_extraction_complete(self):
        # Move required files if they're in a subfolder
        self.status_label.setText("Finalizing installation...")

        app_dir = os.getcwd()

        # Find the bin directory that contains the executables
        bin_dir = None
        for root, dirs, files in os.walk(app_dir):
            if "ffmpeg.exe" in files:
                bin_dir = root
                break

        # If bin directory found and it's not the app directory, move files
        if bin_dir and bin_dir != app_dir:
            # 1. Copy executables
            for exe_file in ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]:
                src_path = os.path.join(bin_dir, exe_file)
                dst_path = os.path.join(app_dir, exe_file)

                if os.path.exists(src_path):
                    # If destination already exists, replace it
                    if os.path.exists(dst_path):
                        os.unlink(dst_path)
                    shutil.copy2(src_path, dst_path)  # Using copy instead of move

            # 2. Find and copy required DLLs
            for root, dirs, files in os.walk(os.path.dirname(bin_dir)):
                for file in files:
                    if file.endswith('.dll') or file.endswith('.dll.a'):
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(app_dir, file)

                        # Copy DLL if it doesn't already exist
                        if not os.path.exists(dst_path):
                            shutil.copy2(src_path, dst_path)

        # Update UI to show success
        self.status_label.setText("FFmpeg successfully installed!")
        self.download_button.setText("Continue")
        self.download_button.setEnabled(True)
        self.skip_button.setVisible(False)

        # Disconnect download handler and connect to accept
        self.download_button.clicked.disconnect()
        self.download_button.clicked.connect(self.accept)
    def handle_download_error(self, error_msg):
        # Show error and return to initial state
        QMessageBox.critical(
            self,
            "Download Error",
            f"Failed to download FFmpeg: {error_msg}\n\nPlease try downloading manually."
        )
        self.status_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.download_button.setEnabled(True)
        self.skip_button.setEnabled(True)
        self.download_checkbox.setEnabled(True)

    def handle_extraction_error(self, error_msg):
        # Show error and return to initial state
        QMessageBox.critical(
            self,
            "Extraction Error",
            f"Failed to extract FFmpeg: {error_msg}\n\nPlease try downloading manually."
        )
        self.status_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.download_button.setEnabled(True)
        self.skip_button.setEnabled(True)
        self.download_checkbox.setEnabled(True)


def check_ffmpeg():
    """Check if FFmpeg is available and prompt user if not"""
    # First check in PATH
    if shutil.which('ffmpeg'):
        return True

    # Then check in current working directory
    current_dir = os.getcwd()
    ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path) and os.path.isfile(ffmpeg_path):
        # Add current directory to PATH temporarily so shutil.which will find it next time
        os.environ["PATH"] += os.pathsep + current_dir
        return True

    # Create and show dialog
    app = QApplication.instance()
    dialog = FFmpegPromptDialog()
    result = dialog.exec()

    # Check again after dialog closes
    return shutil.which('ffmpeg') is not None


if __name__ == "__main__":
    # Test the dialog
    app = QApplication(sys.argv)
    check_ffmpeg()
    sys.exit(app.exec())