# AudiobooksQT: Automatically Convert EPUBs to Audiobooks
[![Installing via pip and running](https://github.com/plusuncold/autiobooks/actions/workflows/pip-install.yaml/badge.svg)](https://github.com/plusuncold/autiobooks/actions/workflows/pip-install.yaml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/autiobooks)
![PyPI - Version](https://img.shields.io/pypi/v/autiobooks)

AudiobooksQT generates `.m4b` audiobooks from regular `.epub` e-books, using Kokoro's high-quality speech synthesis. This is a PyQt6-based port of the original Autiobooks application, offering an enhanced user interface and additional features.

![AudiobooksQT Interface](https://raw.githubusercontent.com/scottpeterman/autiobooksqta/refs/heads/main/screenshots/Screenshot%202025-03-16%20133103.png)

## Features

- Modern, responsive user interface built with PyQt6
- Live audio previews of chapters before conversion
- Voice speed adjustment with real-time controls
- Easy chapter selection with word count and content preview
- GPU acceleration support for faster processing (when available)
- Clean, intuitive design with improved visual feedback
- Maintains all the functionality of the original Autiobooks

## About the TTS Engine

[Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) is an open-weight text-to-speech model with 82 million parameters. It yields natural sounding output while being able to run on consumer hardware.

It supports American, British English, French, Korean, Japanese and Mandarin (though we only support English for now) and a wide range of different [voices](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) with different accents and prosody.

## How to Install and Run

If you have Python 3 on your computer, you can install it with pip.
Be aware that it won't work with Python 3.13.

```bash
pip install autiobooksqt
```

### Dependencies

You will require `ffmpeg` installed:

**Linux:**
```bash
sudo apt install ffmpeg
```

**MacOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [FFmpeg's official site](https://ffmpeg.org/download.html) or install via package managers like Chocolatey or Scoop.

Also recommended is `espeak-ng` for better processing of unknown words.

### Running the Application

To start the program, run:

```bash
python3 -m autiobooksqt
```

The program creates .wav files for each chapter, then combines them into a .m4b file for playing using an audiobook player.

## Differences from Original Autiobooks

- Complete rewrite of the UI using PyQt6 instead of Tkinter
- Added real-time audio preview functionality
- Improved chapter selection interface with content previews
- Enhanced visual design with modern styling
- Better error handling and feedback
- More responsive UI during long operations
- Maintains compatibility with the original Kokoro TTS backend

## Changelog

#### 0.1.0
- Initial release of PyQt6 port
- Added chapter preview functionality
- Redesigned UI for better user experience
- Improved error handling and user feedback

## Contributing

PRs are welcome! This project is open to contributions and improvements.

GitHub Repository: [github.com/scottpeterman/autiobooksqta](https://github.com/scottpeterman/autiobooksqta)

## Credits

Original Autiobooks by David Nesbitt (distributed under MIT license).
PyQt6 port by Scott Peterman.

Distributed under GPLv3 license due to PyQt6 licensing requirements.