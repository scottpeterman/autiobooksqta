# FFmpeg Installation Guide for AudioBooks Creator

AudioBooks Creator requires FFmpeg to convert text to audiobooks. This guide explains how to install FFmpeg when prompted.

## Automatic Installation (Recommended)

When you first start AudioBooks Creator, if FFmpeg is not installed, you'll see a prompt like this:

1. In the popup dialog, keep the "Download FFmpeg automatically (recommended)" option checked
2. Click the "Download & Install FFmpeg" button
3. Wait while the application downloads and extracts FFmpeg (approximately 150MB)
4. Once complete, click "Continue" to proceed with the application

This will automatically install:
- ffmpeg.exe (approximately 148 MB)
- ffplay.exe (approximately 148 MB)
- ffprobe.exe (approximately 148 MB)

These files will be placed in the same folder as the AudioBooks Creator application.

## Manual Installation

If you prefer to install FFmpeg manually, or if automatic installation fails:

1. Uncheck the "Download FFmpeg automatically" option
2. Click one of the provided download links:
   - [Download FFmpeg from Github](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip) (recommended)
   - [Official FFmpeg Download Page](https://ffmpeg.org/download.html)
3. Save the ZIP file to your computer
4. Extract the ZIP file using any extraction tool (like Windows Explorer or 7-Zip)
5. Locate these three files in the extracted folders:
   - ffmpeg.exe
   - ffplay.exe
   - ffprobe.exe
6. Copy these files to the same folder where your AudioBooks Creator application is installed
7. Restart AudioBooks Creator

## Troubleshooting

If you encounter issues with FFmpeg installation:

1. **Download fails**: Try the manual installation method instead
2. **Application doesn't recognize FFmpeg after installation**: Make sure all three files are in the same folder as the application
3. **"Access denied" errors**: Try running AudioBooks Creator as administrator
4. **Files seem too large**: The FFmpeg executables are approximately 148MB each, which is normal

## Alternative Downloads

If the provided links aren't working, you can also download FFmpeg from these sources:

- [FFmpeg Builds by BtbN](https://github.com/BtbN/FFmpeg-Builds/releases)
- [Gyan.dev FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/)
- [FFmpeg Zeranoe Builds Archive](https://ffmpeg.zeranoe.com/builds/)

Make sure to download the "shared" or "shared-win64" version, which includes the necessary executable files.