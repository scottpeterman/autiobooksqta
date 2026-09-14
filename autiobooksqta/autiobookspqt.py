import sys
import threading
import os
from pathlib import Path
import numpy as np
import shutil
import soundfile
import time

# https://ffmpeg.org/download.html
# https://github.com/BtbN/FFmpeg-Builds
# https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QCheckBox, QComboBox, QProgressBar,
                             QFileDialog, QScrollArea, QFrame, QMessageBox, QLineEdit,
                             QGridLayout, QSizePolicy, QStatusBar, QSlider, QSplitter, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QEvent, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor, QPalette

from autiobooksqta.audio_monitor_worker import AudioMonitorWorker
from autiobooksqta.output_options import OutputOptionsDialog
# Import from the engine module
from autiobooksqta.engine_pyqt import (get_gpu_acceleration_available, gen_audio_segments,

                                       get_book, get_title, get_author)
from autiobooksqta.voices_lang import voices, voices_emojified, deemojify_voice

from autiobooksqta.conversion_working import ConversionWorker
from autiobooksqta.light_theme import LIGHT_THEME
from autiobooksqta.add_on import get_cover_image, StatusUpdateEvent
from autiobooksqta.ffmpeg_downloader import check_ffmpeg

import pygame.mixer

pygame.mixer.init()
pygame.mixer.music.set_volume(0.7)

class PlayButtonUpdateEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, chapter_id):
        super().__init__(PlayButtonUpdateEvent.EVENT_TYPE)
        self.chapter_id = chapter_id


class BookLoadedEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, book, chapters, cover):
        super().__init__(BookLoadedEvent.EVENT_TYPE)
        self.book = book
        self.chapters = chapters
        self.cover = cover


class BookErrorEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, error_msg):
        super().__init__(BookErrorEvent.EVENT_TYPE)
        self.error_msg = error_msg


class AudiobooksApp(QMainWindow):
    def __init__(self):
        super().__init__()


        ffmpeg_available = check_ffmpeg()


        # Initialize application state
        self.book = None
        self.chapters = []
        self.playing_sample = False
        self.current_playing_chapter = None
        self.chapter_checkboxes = {}

        # Dictionary to track chapter play buttons
        self.chapter_play_buttons = {}

        # Debug mode - set to True to see additional debug info in console
        self.debug_mode = True

        # Initialize audio system
        try:
            pygame.mixer.init(frequency=44100)
            pygame.mixer.music.set_volume(0.7)
        except Exception as e:
            print(f"Warning: Failed to initialize audio system: {str(e)}")

        # Create temp directory
        self.temp_dir = os.path.join(os.path.expanduser("~"), ".audiobooks_temp")
        os.makedirs(self.temp_dir, exist_ok=True)

        # Audio monitor will be created in init_ui
        self.audio_monitor = None

        # Setup rotating temp files
        self.temp_file_count = 3  # Number of rotating temp files
        self.temp_file_index = 0  # Current index in rotation
        self.temp_files = []

        # Initialize the temp files list
        for i in range(self.temp_file_count):
            self.temp_files.append(os.path.join(self.temp_dir, f"temp_audio_{i}.wav"))

        # Initialize the UI
        self.init_ui()

        # Create and start the audio monitor thread
        self.init_audio_monitor()

    def init_ui(self):
        self.setWindowTitle('Audiobooks Creator')
        self.setMinimumSize(1000, 700)  # Slightly wider for the unified layout

        # Apply the light theme stylesheet
        self.setStyleSheet(LIGHT_THEME)

        # Create the main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        self.setCentralWidget(main_widget)

        # Set application font
        app_font = QFont("Segoe UI", 9)
        QApplication.setFont(app_font)

        # File selection header
        file_section = QWidget()
        file_layout = QHBoxLayout(file_section)
        file_layout.setContentsMargins(0, 0, 0, 0)

        file_button = QPushButton("Select epub file")
        file_button.setIcon(QIcon.fromTheme("document-open"))
        file_button.setStyleSheet(
            "QPushButton { background-color: #6b8e23; color: white; padding: 12px 20px; "
            "border-radius: 4px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #7aa329; }"
        )
        file_button.setMinimumHeight(40)
        file_button.clicked.connect(self.select_file)

        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("color: #777777; padding-left: 10px;")

        file_layout.addWidget(file_button)
        file_layout.addWidget(self.file_path_label, 1)

        main_layout.addWidget(file_section)

        # Create a splitter for the main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # LEFT SIDE - Book info and voice settings
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Book info frame
        book_info_frame = QFrame()
        book_info_frame.setProperty("class", "SectionPanel")
        book_info_layout = QVBoxLayout(book_info_frame)

        # Book info header
        book_info_header = QLabel("Book Info")
        book_info_header.setProperty("class", "HeaderLabel")
        book_info_layout.addWidget(book_info_header)

        # Cover and details
        cover_details_layout = QHBoxLayout()

        # Cover image
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(180, 250)
        self.cover_label.setStyleSheet("background-color: #f0f0e8; border-radius: 4px; border: 1px solid #d0d0d0;")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setText("No cover available")

        # Book details
        book_details_widget = QWidget()
        book_details_layout = QVBoxLayout(book_details_widget)
        book_details_layout.setContentsMargins(10, 0, 0, 0)

        self.title_label = QLabel("Title: ")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
        self.author_label = QLabel("Author: ")
        self.author_label.setStyleSheet("font-size: 14px; color: #555555;")

        book_details_layout.addWidget(self.title_label)
        book_details_layout.addWidget(self.author_label)
        book_details_layout.addStretch()

        cover_details_layout.addWidget(self.cover_label)
        cover_details_layout.addWidget(book_details_widget, 1)

        book_info_layout.addLayout(cover_details_layout)

        # Voice settings frame
        voice_frame = QFrame()
        voice_frame.setProperty("class", "SectionPanel")
        voice_layout = QVBoxLayout(voice_frame)


        # Voice selector
        voice_combo_layout = QHBoxLayout()
        voice_label = QLabel("Voice:")
        voice_label.setMinimumWidth(50)
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(voices_emojified)
        self.voice_combo.setCurrentText(voices[0])

        voice_combo_layout.addWidget(voice_label)
        voice_combo_layout.addWidget(self.voice_combo)

        voice_layout.addLayout(voice_combo_layout)

        # Speed control
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        speed_label.setMinimumWidth(50)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(100)
        self.speed_slider.setTickInterval(25)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.valueChanged.connect(self.update_speed_from_slider)

        self.speed_entry = QLineEdit("1.0")
        self.speed_entry.setMaximumWidth(60)
        self.speed_entry.textChanged.connect(self.update_slider_from_speed)

        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_entry)

        voice_layout.addLayout(speed_layout)

        # GPU acceleration checkbox (if available)
        if get_gpu_acceleration_available():
            self.gpu_acceleration = QCheckBox("GPU Acceleration")
            self.gpu_acceleration.setChecked(False)
            voice_layout.addWidget(self.gpu_acceleration)

        # Add panels to left layout with stretch
        left_layout.addWidget(book_info_frame, 6)
        left_layout.addWidget(voice_frame, 4)

        # RIGHT SIDE - Chapters section
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Chapters frame
        chapters_frame = QFrame()
        chapters_frame.setProperty("class", "SectionPanel")
        chapters_layout = QVBoxLayout(chapters_frame)

        # Chapters header with controls
        chapters_header_layout = QHBoxLayout()

        chapters_header = QLabel("Chapters")
        chapters_header.setProperty("class", "HeaderLabel")

        check_all_button = QPushButton("Check All")
        check_all_button.clicked.connect(self.check_all_chapters)
        check_all_button.setMaximumWidth(100)

        uncheck_all_button = QPushButton("Uncheck All")
        uncheck_all_button.clicked.connect(self.uncheck_all_chapters)
        uncheck_all_button.setMaximumWidth(100)

        chapters_header_layout.addWidget(chapters_header)
        chapters_header_layout.addStretch()
        chapters_header_layout.addWidget(check_all_button)
        chapters_header_layout.addWidget(uncheck_all_button)

        chapters_layout.addLayout(chapters_header_layout)

        # Scrollable chapters area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: transparent;")

        self.chapters_container = QWidget()
        self.chapters_container.setStyleSheet("background-color: transparent;")
        self.chapters_container_layout = QVBoxLayout(self.chapters_container)
        self.chapters_container_layout.setSpacing(4)
        self.chapters_container_layout.setContentsMargins(0, 0, 10, 0)
        self.chapters_container_layout.addStretch()

        scroll_area.setWidget(self.chapters_container)
        chapters_layout.addWidget(scroll_area)

        right_layout.addWidget(chapters_frame)

        # Add panels to splitter
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)

        # Set initial sizes for the splitter (30% left, 70% right)
        content_splitter.setSizes([300, 700])

        # Add splitter to main layout
        main_layout.addWidget(content_splitter, 1)  # 1 = stretch factor

        # Conversion section
        conversion_panel = QFrame()
        conversion_layout = QVBoxLayout(conversion_panel)
        conversion_layout.setContentsMargins(10, 10, 10, 10)

        # Convert button
        self.convert_button = QPushButton("Convert to Audiobook")
        self.convert_button.setStyleSheet(
            "QPushButton { background-color: #8b9c52; color: white; padding: 15px; "
            "font-size: 16px; font-weight: bold; border-radius: 4px; }"
            "QPushButton:hover { background-color: #9bac62; }"
            "QPushButton:pressed { background-color: #7b8c42; }"
            "QPushButton:disabled { background-color: #c0c0b8; }"
        )
        self.convert_button.setMinimumHeight(50)
        self.convert_button.clicked.connect(self.convert)

        # Progress bar layout
        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(0, 10, 0, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(24)

        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet("color: #777777;")

        progress_layout.addWidget(self.progress_bar, 4)
        progress_layout.addWidget(self.progress_label, 1)

        conversion_layout.addWidget(self.convert_button)
        conversion_layout.addLayout(progress_layout)

        main_layout.addWidget(conversion_panel)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def init_audio_monitor(self):
        """Initialize and start the audio monitor thread"""
        # Create and configure the monitor thread
        self.audio_monitor = AudioMonitorWorker(self)
        self.audio_monitor.debug_mode = self.debug_mode
        self.audio_monitor.playback_finished.connect(self.on_playback_complete)
        self.audio_monitor.start()

    def get_next_temp_file(self):
        """Get the next temp file in the rotation"""
        # Get the next file
        temp_file = self.temp_files[self.temp_file_index]

        # Update the index for next time
        self.temp_file_index = (self.temp_file_index + 1) % self.temp_file_count

        # Try to ensure the file isn't in use
        if os.path.exists(temp_file):
            try:
                # On Windows, we can't delete a file that's in use, so this
                # will fail if the file is still locked by another process
                os.remove(temp_file)
            except PermissionError:
                # If we can't delete it, try the next one in the rotation
                return self.get_next_temp_file()
            except Exception as e:
                print(f"Non-critical error removing temp file: {e}")
                # We can still try to use the file even if delete failed
                pass

        return temp_file

    def update_speed_from_slider(self):
        """Update speed entry field when slider is moved"""
        speed_value = self.speed_slider.value() / 100.0
        self.speed_entry.setText(f"{speed_value:.1f}")

    def update_slider_from_speed(self):
        """Update slider position when speed is manually entered"""
        try:
            speed_value = float(self.speed_entry.text())
            if 0.5 <= speed_value <= 2.0:
                self.speed_slider.setValue(int(speed_value * 100))
                self.speed_entry.setStyleSheet("")
            else:
                self.speed_entry.setStyleSheet("color: #cc0000; border: 1px solid #cc0000;")
        except ValueError:
            self.speed_entry.setStyleSheet("color: #cc0000; border: 1px solid #cc0000;")

    def check_all_chapters(self):
        """Select all chapters"""
        for checkbox in self.chapter_checkboxes.values():
            checkbox.setChecked(True)

    def uncheck_all_chapters(self):
        """Deselect all chapters"""
        for checkbox in self.chapter_checkboxes.values():
            checkbox.setChecked(False)

    def select_file(self):
        """Open file dialog to select epub file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select an epub file',
            '',
            'EPUB Files (*.epub)'
        )

        if file_path:
            self.file_path_label.setText(file_path)

            # Show loading indicator in the status bar
            self.status_bar.showMessage("Loading book, please wait...")
            QApplication.instance().postEvent(
                self,
                StatusUpdateEvent(f"Loading book, please wait...",
                                  "Loading book, please wait...")
            )
            QApplication.processEvents()  # Process events to update UI

            # Load the book in a thread to keep UI responsive
            load_thread = threading.Thread(target=lambda: self.load_book_thread(file_path))
            load_thread.daemon = True
            load_thread.start()

    def load_book_thread(self, file_path):
        """Thread function to load book data"""
        try:
            # Wrap the get_book call in a more robust error handler
            book, chapters_from_book, book_cover = None, [], None
            try:
                book, chapters_from_book, book_cover = get_book(file_path, True)
            except Exception as inner_e:
                print(f"Initial load error: {str(inner_e)}")
                # Try a fallback approach - load without cover image first
                try:
                    book, chapters_from_book, book_cover = get_book(file_path, False)
                    # If this works, try to get the cover separately
                    if book:
                        try:
                            book_cover = get_cover_image(book, True)
                        except:
                            book_cover = None
                except:
                    # If still failing, re-raise the original error
                    raise inner_e

            # Process the loaded book in the main thread
            QApplication.instance().postEvent(
                self,
                BookLoadedEvent(book, chapters_from_book, book_cover)
            )
        except Exception as e:
            # Handle any exceptions during loading
            QApplication.instance().postEvent(
                self,
                BookErrorEvent(str(e))
            )

    def event(self, event):
        """Handle custom events"""
        if isinstance(event, BookLoadedEvent):
            self.process_loaded_book(event.book, event.chapters, event.cover)
            return True
        elif isinstance(event, BookErrorEvent):
            self.handle_book_loading_error(event.error_msg)
            return True
        elif isinstance(event, StatusUpdateEvent):
            self.status_bar.showMessage(event.status_message)
            self.progress_label.setText(event.status_message)
            return True
        return super().event(event)

    def process_loaded_book(self, book, chapters, cover):
        """Process loaded book data and update UI"""
        if not book:
            self.handle_book_loading_error("Failed to load the book: Unknown error")
            return

        # Store the book
        self.book = book

        try:
            # Update book info
            self.title_label.setText(f"Title: {get_title(self.book)}")
            self.author_label.setText(f"Author: {get_author(self.book)}")

            # Update cover image
            if cover:
                try:
                    # Try different methods to load the image
                    pixmap = QPixmap()
                    if isinstance(cover, bytes):
                        pixmap.loadFromData(cover)
                    elif isinstance(cover, str) and os.path.exists(cover):
                        pixmap.load(cover)
                    elif hasattr(cover, "data") and callable(cover.data):
                        pixmap.loadFromData(cover.data())

                    if not pixmap.isNull():
                        self.cover_label.setPixmap(pixmap.scaled(
                            self.cover_label.size(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        ))
                        self.cover_label.setText("")
                    else:
                        # Fall back to no cover if pixmap couldn't be loaded
                        self.cover_label.setText("No cover available")
                        self.cover_label.setPixmap(QPixmap())
                except Exception as img_e:
                    print(f"Error loading cover image: {str(img_e)}")
                    self.cover_label.setText("No cover available")
                    self.cover_label.setPixmap(QPixmap())
            else:
                self.cover_label.setText("No cover available")
                self.cover_label.setPixmap(QPixmap())

            # Update chapters list
            self.chapters = chapters
            self.populate_chapters()

            # Update status bar
            self.status_bar.showMessage(f"Loaded book: {get_title(self.book)} with {len(self.chapters)} chapters")
            self.progress_label.setText("Ready")
        except Exception as e:
            self.handle_book_loading_error(f"Error updating UI after loading book: {str(e)}")

    def handle_book_loading_error(self, error_msg):
        """Display error message when book loading fails"""
        # Custom error dialog
        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle("Error Loading Book")
        error_dialog.setIcon(QMessageBox.Icon.Critical)

        # Detailed error message
        detailed_error = error_msg
        if "no default root window" in error_msg.lower():
            detailed_error = (
                "Failed to load the book due to an error in the ebook's structure. "
                "This usually happens with books that have formatting issues.\n\n"
                "Try opening the epub file in an ebook editor like Calibre and "
                "saving it again to fix formatting issues."
            )

        error_dialog.setText(detailed_error)
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Set a fixed width to ensure readable text
        error_dialog.setMinimumWidth(400)

        # Update status bar and show error dialog
        self.status_bar.showMessage(f"Error: {error_msg}")
        error_dialog.exec()

    def populate_chapters(self):
        """Populate the chapters list in the UI"""
        # Clear previous state
        self.chapter_checkboxes.clear()
        self.chapter_play_buttons.clear()

        # Remove all existing widgets from the layout
        while self.chapters_container_layout.count() > 0:
            item = self.chapters_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add chapters with checkboxes
        for chapter in self.chapters:
            word_count = len(chapter.extracted_text.split())

            if word_count == 0:
                continue

            # Create chapter item frame
            chapter_frame = QFrame()
            chapter_frame.setObjectName(f"chapter_frame_{chapter.file_name}")
            chapter_frame.setStyleSheet(
                "QFrame { background-color: #f9f9f4; border: 1px solid #e0e0d6; "
                "border-radius: 3px; padding: 2px; margin: 1px 0; }"
                "QFrame:hover { background-color: #f0f0e6; }"
            )

            # Use a more efficient layout
            chapter_layout = QHBoxLayout(chapter_frame)
            chapter_layout.setContentsMargins(8, 6, 8, 6)
            chapter_layout.setSpacing(8)

            # Checkbox for selection - UNCHECKED by default
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox.setMinimumWidth(15)
            self.chapter_checkboxes[chapter] = checkbox

            # Create a unique ID for this chapter
            chapter_id = id(chapter)

            # Play button with consistent styling
            play_button = QPushButton("▶")
            play_button.setObjectName(f"play_button_{chapter_id}")
            play_button.setFixedSize(24, 24)
            play_button.setStyleSheet(
                "QPushButton { background-color: #6b8e23; border-radius: 12px; font-size: 10px; "
                "padding: 0; margin: 0; text-align: center; }"
                "QPushButton:hover { background-color: #7aa329; }"
            )

            # Store the button in our tracking dictionary
            self.chapter_play_buttons[chapter_id] = {
                'button': play_button,
                'chapter': chapter,
                'is_playing': False
            }

            # Connect with chapter ID for better tracking
            play_button.clicked.connect(
                lambda checked=False, ch_id=chapter_id:
                self.handle_chapter_click(ch_id)
            )

            # Chapter info with better formatting
            chapter_info = QLabel(f"{chapter.file_name}")
            chapter_info.setStyleSheet("font-weight: bold; color: #333333; font-size: 11px;")
            chapter_info.setMinimumWidth(120)

            # Word count display
            word_string = "words" if word_count != 1 else "word"
            word_count_label = QLabel(f"({word_count} {word_string})")
            word_count_label.setStyleSheet("color: #777777; font-size: 10px;")
            word_count_label.setFixedWidth(80)

            # Preview text - with improved readability
            preview_text = QLabel(self.get_limited_text(chapter.extracted_text))
            preview_text.setStyleSheet("color: #555555; font-style: italic; font-size: 10px;")
            preview_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            preview_text.setWordWrap(True)
            preview_text.setTextFormat(Qt.TextFormat.PlainText)  # Ensure proper rendering

            # Add widgets to layout
            chapter_layout.addWidget(checkbox)
            chapter_layout.addWidget(play_button)
            chapter_layout.addWidget(chapter_info)
            chapter_layout.addWidget(word_count_label)
            chapter_layout.addWidget(preview_text, 1)

            # Add the chapter frame to the container
            self.chapters_container_layout.insertWidget(self.chapters_container_layout.count() - 1, chapter_frame)

    def get_limited_text(self, text):
        """Limit text to a manageable length for display"""
        max_length = 25  # limit to 25 words
        text = text.replace("\n", " ")
        words = text.split()
        if len(words) > max_length:
            return ' '.join(words[:max_length]) + "..."
        return text

    def handle_chapter_click(self, chapter_id):
        """Handle play/stop button click for chapter audio preview"""
        if self.debug_mode:
            print(f"Clicked on chapter {chapter_id}")

        # Get chapter info from our tracking dictionary
        chapter_info = self.chapter_play_buttons.get(chapter_id)
        if not chapter_info:
            print(f"Error: Chapter ID {chapter_id} not found in tracking dictionary")
            return

        chapter = chapter_info['chapter']
        play_button = chapter_info['button']

        # If this is the currently playing chapter, stop it
        if chapter_info['is_playing']:
            if self.debug_mode:
                print(f"Stopping playback of chapter {chapter_id}")

            # Stop playback
            pygame.mixer.music.stop()
            self.audio_monitor.set_playing(False)

            # Reset button state
            play_button.setText("▶")
            play_button.setStyleSheet(
                "QPushButton { background-color: #6b8e23; border-radius: 12px; font-size: 10px; "
                "padding: 0; margin: 0; text-align: center; }"
                "QPushButton:hover { background-color: #7aa329; }"
            )

            # Reset state tracking
            chapter_info['is_playing'] = False
            self.playing_sample = False
            self.current_playing_chapter = None

            self.status_bar.showMessage("Ready")
            self.progress_label.setText("Ready")
            return

        # If another chapter is playing, stop it first
        if self.playing_sample and self.current_playing_chapter:
            curr_chapter_info = self.chapter_play_buttons.get(self.current_playing_chapter)
            if curr_chapter_info:
                # Stop current playback
                pygame.mixer.music.stop()
                self.audio_monitor.set_playing(False)

                # Reset button state for previous chapter
                curr_button = curr_chapter_info['button']
                curr_button.setText("▶")
                curr_button.setStyleSheet(
                    "QPushButton { background-color: #6b8e23; border-radius: 12px; font-size: 10px; "
                    "padding: 0; margin: 0; text-align: center; }"
                    "QPushButton:hover { background-color: #7aa329; }"
                )

                # Reset state tracking for previous chapter
                curr_chapter_info['is_playing'] = False

        # Now play the new chapter
        text = self.get_limited_text(chapter.extracted_text)
        if not text:
            return

        # Update UI to show this button is preparing
        play_button.setText("⌛")  # Hourglass symbol for "preparing"
        play_button.setStyleSheet(
            "QPushButton { background-color: #f0ad4e; border-radius: 12px; font-size: 10px; "
            "padding: 0; margin: 0; text-align: center; }"
            "QPushButton:hover { background-color: #ec971f; }"
        )

        # Update state tracking
        chapter_info['is_playing'] = True
        self.playing_sample = True
        self.current_playing_chapter = chapter_id

        # Initial status update to show that we're generating
        self.status_bar.showMessage(f"Generating audio for: {chapter.file_name}...")
        self.progress_label.setText("Preparing voice sample...")
        QApplication.processEvents()  # Update UI immediately

        # Get voice and speed settings
        voice = deemojify_voice(self.voice_combo.currentText())
        try:
            speed = float(self.speed_entry.text())
        except ValueError:
            speed = 1.0

        def update_button_directly():
            print(f"updating button directly...")
            chapter_info = self.chapter_play_buttons.get(chapter_id)
            if chapter_info:
                button = chapter_info['button']
                button.setText("⏹")
                button.setStyleSheet(
                    "QPushButton { background-color: #d04030; border-radius: 12px; font-size: 10px; "
                    "padding: 0; margin: 0; text-align: center; }"
                    "QPushButton:hover { background-color: #e05040; }"
                )
                if self.debug_mode:
                    print("Button directly updated to stop symbol")
            else:
                if self.debug_mode:
                    print(f"Chapter info not found for ID {chapter_id}")

        # Generate and play audio in a separate thread
        def generate_and_play_sample():
            try:
                if self.debug_mode:
                    print(f"Generating audio for chapter {chapter_id}")


                # Generate audio
                audio_segments = gen_audio_segments(text, voice, speed, split_pattern=r"")
                QApplication.processEvents()

                # Post status update from thread
                QApplication.instance().postEvent(
                    self,
                    StatusUpdateEvent(f"Processing audio for: {chapter.file_name}...",
                                      "Converting to audio file...")
                )

                final_audio = np.concatenate(audio_segments)
                sample_rate = 24000

                # Get the next temp file in rotation
                temp_file = self.get_next_temp_file()

                if self.debug_mode:
                    print(f"Using temp file: {temp_file}")

                # Write audio to file
                soundfile.write(temp_file, final_audio, sample_rate)



                # Check if we should still play this chapter
                if not self.playing_sample or self.current_playing_chapter != chapter_id:
                    if self.debug_mode:
                        print(f"Playback cancelled for chapter {chapter_id}")
                    return

                # Post status update from thread
                QApplication.instance().postEvent(
                    self,
                    StatusUpdateEvent(f"Playing sample of: {chapter.file_name}",
                                      "Playing audio sample...")
                )
                # Update button to show it's now playing
                QApplication.instance().postEvent(
                    self,
                    PlayButtonUpdateEvent(chapter_id)
                )
                QApplication.processEvents()

                if self.debug_mode:
                    update_button_directly()
                    print(f"Starting playback for chapter {chapter_id}")
                    QTimer.singleShot(1500, update_button_directly)

                time.sleep(0.5)

                # Make sure any previous playback is fully stopped
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()

                # Small delay to ensure system resources are released
                time.sleep(0.1)

                # Play the audio
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()

                # Set the monitor thread to watch this playback
                self.audio_monitor.set_playing(True)

            except Exception as e:
                print(f"Error playing sample: {str(e)}")
                # Reset UI state on error
                self.playing_sample = False
                self.current_playing_chapter = None
                chapter_info['is_playing'] = False

                # Update UI in the main thread
                QApplication.instance().postEvent(
                    self,
                    BookErrorEvent(f"Error playing sample: {str(e)}")
                )

        # Start the audio generation thread
        audio_thread = threading.Thread(target=generate_and_play_sample)
        audio_thread.daemon = True
        audio_thread.start()

    def on_playback_complete(self):
        """Reset playback state when audio finishes"""
        if self.debug_mode:
            print(f"Playback complete, resetting UI for chapter {self.current_playing_chapter}")

        # Reset state flags
        self.playing_sample = False

        # Reset UI for the current playing chapter
        if self.current_playing_chapter is not None:
            chapter_info = self.chapter_play_buttons.get(self.current_playing_chapter)
            if chapter_info:
                button = chapter_info['button']
                button.setText("▶")
                button.setStyleSheet(
                    "QPushButton { background-color: #6b8e23; border-radius: 12px; font-size: 10px; "
                    "padding: 0; margin: 0; text-align: center; }"
                    "QPushButton:hover { background-color: #7aa329; }"
                )
                chapter_info['is_playing'] = False

        # Reset tracking
        self.current_playing_chapter = None
        self.status_bar.showMessage("Ready")
        QApplication.instance().postEvent(
            self,
            StatusUpdateEvent(f"Ready",
                              "Ready")
        )

    def check_speed_range(self):
        """Validate speed entry is within acceptable range"""
        try:
            value = float(self.speed_entry.text())
            if 0.5 <= value <= 2.0:
                self.speed_entry.setStyleSheet("")
                return True
            else:
                self.speed_entry.setStyleSheet("color: #ff5555; border: 1px solid #ff5555;")
        except ValueError:
            self.speed_entry.setStyleSheet("color: #ff5555; border: 1px solid #ff5555;")
        return False

    def convert(self):
        """Start the conversion process"""
        if not self.check_speed_range():
            QMessageBox.warning(
                self,
                "Warning",
                "Please enter a speed value between 0.5 and 2.0."
            )
            return

        file_path = self.file_path_label.text()
        if file_path == "No file selected" or not os.path.exists(file_path):
            QMessageBox.warning(
                self,
                "Warning",
                "Please select an epub file first."
            )
            return

        # Get selected chapters
        chapters_selected = [chapter for chapter, checkbox in self.chapter_checkboxes.items()
                             if checkbox.isChecked()]

        if not chapters_selected:
            # Select all chapters if none selected
            for chapter, checkbox in self.chapter_checkboxes.items():
                checkbox.setChecked(True)
            chapters_selected = list(self.chapter_checkboxes.keys())

        # Show the output options dialog
        output_dialog = OutputOptionsDialog(self)
        # Set the file path so the dialog can use it for default output location
        output_dialog.file_path = file_path

        if output_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Get the user's output options
        output_options = output_dialog.get_options()

        # Disable controls during conversion
        self.speed_entry.setEnabled(False)
        self.speed_slider.setEnabled(False)
        self.voice_combo.setEnabled(False)
        self.convert_button.setEnabled(False)

        # Update status
        self.status_bar.showMessage("Starting conversion...")

        # Create and start worker thread
        voice = deemojify_voice(self.voice_combo.currentText())
        speed = float(self.speed_entry.text())
        use_gpu = self.gpu_acceleration.isChecked() if hasattr(self, "gpu_acceleration") else False

        self.conversion_worker = ConversionWorker(
            self.book,
            chapters_selected,
            voice,
            speed,
            use_gpu,
            file_path,
            output_folder=output_options['output_folder'],
            create_m4b=output_options['create_m4b'],
            create_mp3=output_options['create_mp3'],
            mp3_quality=output_options['mp3_quality'],
            keep_wav=output_options['keep_wav']
        )
        self.conversion_worker.progress_updated.connect(self.update_progress)
        self.conversion_worker.conversion_complete.connect(self.on_conversion_complete)
        self.conversion_worker.error_occurred.connect(self.on_conversion_error)
        self.conversion_worker.start()

    def update_progress(self, value, text):
        """Update progress bar and label during conversion"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(text)
        self.status_bar.showMessage(text)

    def on_conversion_complete(self):
        """Handle successful completion of conversion"""
        self.speed_entry.setEnabled(True)
        self.speed_slider.setEnabled(True)
        self.voice_combo.setEnabled(True)
        self.convert_button.setEnabled(True)
        self.status_bar.showMessage("Conversion completed successfully!")
        QMessageBox.information(
            self,
            "Success",
            "Audiobook conversion completed successfully!"
        )

    def on_conversion_error(self, error_message):
        """Handle error during conversion"""
        self.speed_entry.setEnabled(True)
        self.speed_slider.setEnabled(True)
        self.voice_combo.setEnabled(True)
        self.convert_button.setEnabled(True)
        self.status_bar.showMessage(f"Error: {error_message}")
        QMessageBox.critical(
            self,
            "Error",
            error_message
        )

    def closeEvent(self, event):
        """Clean up resources when closing the application"""
        # Stop the audio monitor thread
        if self.audio_monitor:
            self.audio_monitor.stop()

        # Stop any playing audio
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except:
            pass

        # Clean up temp files
        try:
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        except:
            pass

        # Accept the close event
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Set app style
    app.setStyle("Fusion")

    # Enable high DPI scaling - using the correct PyQt6 attributes
    # These were renamed in Qt6 compared to Qt5
    # app.setAttribute(Qt.ApplicationAttribute.HighDpiScaleFactorRoundingPolicy, True)

    # Create and show the main window
    window = AudiobooksApp()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()