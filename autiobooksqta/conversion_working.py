from pathlib import Path
import os
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

from autiobooksqta.engine_pyqt import set_gpu_acceleration, get_title, get_author, convert_text_to_wav_file, \
    create_index_file, \
    get_cover_image, create_m4b


class ConversionWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    conversion_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, book, chapters_selected, voice, speed, use_gpu, file_path,
                 output_folder=None, create_m4b=True, create_mp3=False,
                 mp3_quality="Medium (128 kbps)", keep_wav=False, debug_mode=False):
        super().__init__()
        self.book = book
        self.chapters_selected = chapters_selected
        self.voice = voice
        self.speed = speed
        self.use_gpu = use_gpu
        self.file_path = file_path
        self.output_folder = output_folder or os.path.dirname(file_path)
        self.create_m4b = create_m4b
        self.create_mp3 = create_mp3
        self.mp3_quality = mp3_quality
        self.keep_wav = keep_wav or create_mp3  # Always keep WAVs if MP3 creation is requested
        self.running = True
        self.debug_mode = debug_mode

        # Create subfolder paths
        self.wav_folder = os.path.join(self.output_folder, "wav")
        self.mp3_folder = os.path.join(self.output_folder, "mp3")
        self.m4b_folder = os.path.join(self.output_folder, "m4b")

    def run(self):
        try:
            # Ensure output directory exists
            os.makedirs(self.output_folder, exist_ok=True)

            # Create subfolders as needed
            if self.keep_wav or self.create_mp3:
                os.makedirs(self.wav_folder, exist_ok=True)
            if self.create_mp3:
                os.makedirs(self.mp3_folder, exist_ok=True)
            if self.create_m4b:
                os.makedirs(self.m4b_folder, exist_ok=True)

            set_gpu_acceleration(self.use_gpu)
            filename = Path(self.file_path).name
            title = get_title(self.book)
            creator = get_author(self.book)
            base_filename = filename.replace('.epub', '')

            # Calculate total steps
            base_steps = len(self.chapters_selected)
            m4b_steps = 2 if self.create_m4b else 0  # Index + M4B creation
            mp3_steps = len(self.chapters_selected) if self.create_mp3 else 0
            total_steps = base_steps + m4b_steps + mp3_steps
            current_step = 0

            wav_files = []
            for i, chapter in enumerate(self.chapters_selected, start=1):
                if not self.running:
                    return

                text = chapter.extracted_text
                if i == 1:
                    text = f"{title} by {creator}.\n{text}"

                # Create WAV filename in the wav subfolder
                wav_filename = os.path.join(
                    self.wav_folder,
                    f"{base_filename}_chapter_{i}.wav"
                )

                current_step += 1
                self.progress_updated.emit(
                    int((current_step / total_steps) * 100),
                    f"Converting chapter {i} of {len(self.chapters_selected)}"
                )

                # Make sure we're storing the full path as created
                if convert_text_to_wav_file(text, self.voice, self.speed, wav_filename):
                    # Ensure we have the absolute path with correct directory
                    full_path = os.path.abspath(wav_filename)
                    wav_files.append(full_path)
                    print(f"Created WAV file: {full_path}")

            if not wav_files:
                self.error_occurred.emit("No chapters were converted.")
                return

            # Create M4B if requested
            if self.create_m4b:
                current_step += 1
                self.progress_updated.emit(
                    int((current_step / total_steps) * 100),
                    "Creating index file"
                )

                # Create index file in the output folder
                index_file = os.path.join(self.m4b_folder, "audiobook_index.txt")
                create_index_file(title, creator, wav_files)

                current_step += 1
                self.progress_updated.emit(
                    int((current_step / total_steps) * 100),
                    "Creating m4b file"
                )

                # Get cover image
                cover_image_full = get_cover_image(self.book, False)

                # Create M4B in the m4b subfolder
                m4b_path = os.path.join(self.m4b_folder, f"{base_filename}.m4b")
                create_m4b(wav_files, m4b_path, cover_image_full)

            # Create MP3 files if requested
            if self.create_mp3:
                self.convert_to_mp3(wav_files, total_steps, current_step, base_filename)
                current_step += len(wav_files)

            # Clean up WAV files if not keeping them
            if not self.keep_wav:
                print(f"Cleaning up temporary files from: {self.wav_folder}")
                print(f"Files to clean: {wav_files}")
                self.progress_updated.emit(100, "Cleaning up temporary files...")

                for wav_file in wav_files:
                    try:
                        # Ensure we have the absolute path
                        full_path = os.path.abspath(wav_file)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            print(f"Deleted WAV file: {full_path}")
                        else:
                            print(f"WAV file not found for deletion: {full_path}")
                    except Exception as e:
                        print(f"Warning: Could not delete WAV file {wav_file}: {str(e)}")

                # Remove WAV folder if it's empty
                try:
                    if os.path.exists(self.wav_folder) and not os.listdir(self.wav_folder):
                        os.rmdir(self.wav_folder)
                        print(f"Removed empty WAV folder: {self.wav_folder}")
                except Exception as e:
                    print(f"Warning: Could not remove WAV folder: {str(e)}")

            self.progress_updated.emit(100, "Conversion complete")
            self.conversion_complete.emit()

        except Exception as e:
            self.error_occurred.emit(f"Error during conversion: {str(e)}")

    def convert_to_mp3(self, wav_files, total_steps, current_step, base_filename):
        """Convert WAV files to MP3 using ffmpeg"""
        # Map quality setting to bitrate
        quality_map = {
            "Low (64 kbps)": "64k",
            "Medium (128 kbps)": "128k",
            "High (192 kbps)": "192k",
            "Very High (256 kbps)": "256k"
        }
        bitrate = quality_map.get(self.mp3_quality, "128k")

        for i, wav_file in enumerate(wav_files, start=1):
            if not self.running:
                return

            # Update progress
            step = current_step + i
            self.progress_updated.emit(
                int((step / total_steps) * 100),
                f"Creating MP3 {i} of {len(wav_files)}"
            )

            # Extract chapter number from wav filename
            chapter_num = i  # Default chapter number
            try:
                # Extract chapter number from the filename
                wav_filename = os.path.basename(wav_file)
                if "_chapter_" in wav_filename:
                    chapter_num = int(wav_filename.split("_chapter_")[1].split(".")[0])
            except:
                print(f"Could not extract chapter number from {wav_file}, using {i}")

            # Create MP3 filename in mp3 subfolder
            mp3_file = os.path.join(
                self.mp3_folder,
                f"{base_filename}_chapter_{chapter_num}.mp3"
            )

            # Use subprocess to call ffmpeg for conversion
            try:
                subprocess.run([
                    "ffmpeg",
                    "-i", wav_file,
                    "-codec:a", "libmp3lame",
                    "-b:a", bitrate,
                    "-y",  # Overwrite output file if it exists
                    mp3_file
                ], check=True, capture_output=True)
                print(f"Created MP3 file: {mp3_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting {wav_file} to MP3: {e}")
                raise Exception(f"MP3 conversion failed: {e}")

    def stop(self):
        """Stop the conversion process"""
        self.running = False
