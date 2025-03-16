from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from autiobooks.engine_pyqt import set_gpu_acceleration, get_title, get_author, convert_text_to_wav_file, create_index_file, \
    get_cover_image, create_m4b


class ConversionWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    conversion_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, book, chapters_selected, voice, speed, use_gpu, file_path):
        super().__init__()
        self.book = book
        self.chapters_selected = chapters_selected
        self.voice = voice
        self.speed = speed
        self.use_gpu = use_gpu
        self.file_path = file_path

    def run(self):
        try:
            set_gpu_acceleration(self.use_gpu)
            filename = Path(self.file_path).name
            title = get_title(self.book)
            creator = get_author(self.book)
            steps = len(self.chapters_selected) + 2
            current_step = 1

            wav_files = []
            for i, chapter in enumerate(self.chapters_selected, start=1):
                text = chapter.extracted_text
                if i == 1:
                    text = f"{title} by {creator}.\n{text}"
                wav_filename = filename.replace('.epub', f'_chapter_{i}.wav')

                self.progress_updated.emit(
                    int((current_step / steps) * 100),
                    f"Converting chapter {i} of {len(self.chapters_selected)}"
                )

                if convert_text_to_wav_file(text, self.voice, self.speed, wav_filename):
                    wav_files.append(wav_filename)

                current_step += 1

            if not wav_files:
                self.error_occurred.emit("No chapters were converted.")
                return

            self.progress_updated.emit(
                int((current_step / steps) * 100),
                "Creating index file"
            )
            create_index_file(title, creator, wav_files)
            current_step += 1

            self.progress_updated.emit(
                int((current_step / steps) * 100),
                "Creating m4b file"
            )
            cover_image_full = get_cover_image(self.book, False)
            create_m4b(wav_files, filename, cover_image_full)

            self.progress_updated.emit(100, "Conversion complete")
            self.conversion_complete.emit()

        except Exception as e:
            self.error_occurred.emit(f"Error during conversion: {str(e)}")
