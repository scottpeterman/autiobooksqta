# AutiobooksQTa: Automatically Convert EPUBs to Autiobooks

AutiobooksQTa generates `.m4b` audiobooks from regular `.epub` e-books, using Kokoro's high-quality speech synthesis. This is a PyQt6-based port of the original Autiobooks application, offering an enhanced user interface and additional features.

![AutiobooksQT Interface](https://raw.githubusercontent.com/scottpeterman/autiobooksqta/refs/heads/main/screenshots/app.png)

![AutiobooksQT Interface](https://raw.githubusercontent.com/scottpeterman/autiobooksqta/refs/heads/main/screenshots/options.png)

## Features

- Convert EPUB books to high-quality audio files
- Create M4B audiobooks with chapters
- Export to MP3 with customizable quality settings
- Multiple voice options and speed control
- GPU acceleration support
- Simple and intuitive user interface
- Automatic FFmpeg installation assistant

## Installation

You can install AutiobooksQTa directly from PyPI:

```bash
pip install autiobooksqta
```

## Usage

After installation, you can run the application with:

```bash
autiobooksqta
```

### Converting a Book

1. Open an EPUB file using the file selector
2. Choose your voice preferences and output settings
3. Select which chapters to convert
4. Click "Convert" to start the process
5. Find your audiobook files in organized subfolders:
   - `m4b/` - Contains the complete audiobook in M4B format
   - `mp3/` - Contains individual MP3 files for each chapter
   - `wav/` - Contains raw WAV files (if selected to keep)

## FFmpeg Installation Assistant

AutiobooksQTa requires FFmpeg to create audiobooks. If FFmpeg is not found on your system, the application will automatically detect this and offer to download and install it for you:

![FFmpeg Installation Assistant](https://raw.githubusercontent.com/scottpeterman/autiobooksqta/refs/heads/main/screenshots/ffmpeg.png)

### Features of the FFmpeg Assistant:

- Automatic detection of missing FFmpeg installation
- One-click download and installation option (recommended)
- Links to official FFmpeg sources if you prefer manual installation
- Clear instructions for manual installation
- Option to continue without FFmpeg (with limited functionality)

The assistant ensures you can get up and running quickly without having to manually configure FFmpeg.

## Requirements

- Python 3.8+
- FFmpeg (automatically installed if missing)
- PyQt6
- Additional dependencies will be installed automatically

## Development

To contribute to this project:

```bash
git clone https://github.com/scottpeterman/autiobooksqta.git
cd autiobooksqta
pip install -e .
```

## License

[GNU General Public License v3.0 (GPLv3)](LICENSE)

## Links

- GitHub: [https://github.com/scottpeterman/autiobooksqta](https://github.com/scottpeterman/autiobooksqta)
- PyPI: [https://pypi.org/project/autiobooksqta/](https://pypi.org/project/autiobooksqta/)
- Original Project: [autiobooks](https://github.com/plusuncold/autiobooks)