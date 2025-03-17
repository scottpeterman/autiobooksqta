# AudiobooksQTa: Automatically Convert EPUBs to Audiobooks

AudiobooksQTa generates `.m4b` audiobooks from regular `.epub` e-books, using Kokoro's high-quality speech synthesis. This is a PyQt6-based port of the original Autiobooks application, offering an enhanced user interface and additional features.

![AudiobooksQT Interface](https://raw.githubusercontent.com/scottpeterman/autiobooksqta/refs/heads/main/screenshots/app.png)

![AudiobooksQT Interface](https://raw.githubusercontent.com/scottpeterman/autiobooksqta/refs/heads/main/screenshots/options.png)

# AutobooksQTA

A PyQt6-based application for converting EPUB books to audiobooks in multiple formats.

## Features

- Convert EPUB books to high-quality audio files
- Create M4B audiobooks with chapters
- Export to MP3 with customizable quality settings
- Multiple voice options and speed control
- GPU acceleration support
- Simple and intuitive user interface

## Installation

You can install AutobooksQTA directly from PyPI:

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

## Requirements

- Python 3.8+
- FFmpeg (must be installed and available in your system PATH)
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
- Original Project: autiobooks https://github.com/plusuncold/autiobooks