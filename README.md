# Video File Manipulation Utilities

### Use Cases
- Merge SRT files with corresponding video files
- Extract subtitles from multiple video files
- Shift subtitles within multiple video files
- Display video info for multiple video files

### Prerequisites
  - [Python 3](https://www.python.org/downloads/)
  - [FFmpeg](https://www.ffmpeg.org/download.html)
  - [MediaInfo](https://mediaarea.net/en/MediaInfo)

### Usage: `python -u .\cli.py`

### Notes
  - This application is kind of crappy, it's meant for my personal use. But it's here in case others can find a use for it. If you do, please star this repo!
  - Options 6 & 7 are in beta, and should not be used
  - Option 4 requires [FFsubsync](https://github.com/smacke/ffsubsync). To install it on Windows, follow these steps:
    1. Download [Build Tools for Visual Studio 2022](https://aka.ms/vs/17/release/vs_BuildTools.exe)
    2. Install "Desktop development with C++"
    3. Add this to the system path `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin`
    4. Run `pip install ffsubsync`

### To Do
  - Write unit tests
