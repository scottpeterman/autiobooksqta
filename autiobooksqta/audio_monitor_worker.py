import pygame
from PyQt6.QtCore import QThread, pyqtSignal


class AudioMonitorWorker(QThread):
    """Worker thread to monitor audio playback status"""
    playback_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.is_playing = False
        self.debug_mode = False

    def set_playing(self, status):
        """Set current playback status"""
        self.is_playing = status

    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        self.wait()

    def run(self):
        """Thread's main method"""
        if self.debug_mode:
            print("Audio monitor thread started")

        while self.running:
            # Check if we think audio is playing but pygame says it's not
            if self.is_playing and not pygame.mixer.music.get_busy():
                if self.debug_mode:
                    print("Detected playback finished")
                self.is_playing = False
                self.playback_finished.emit()

            # Sleep to prevent high CPU usage
            self.msleep(100)

