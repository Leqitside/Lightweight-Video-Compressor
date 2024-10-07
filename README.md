# Lightweight-Video-Compressor

This is a simple drag-and-drop video processing tool built using Python and `Tkinter` that allows you to cut, compress, and mute video files in `.mp4` format. The application takes user inputs for the start and end times, target file size, audio muting, and whether to delete the original video file after processing. It uses the `moviepy` library for video processing and `TkinterDnD2` for drag-and-drop functionality.

## Features
- **Drag and Drop Support**: Drop `.mp4` files directly into the interface for easy processing.
- **Video Cutting**: Specify start and end times to trim videos.
- **File Compression**: Compress videos to a user-defined target size.
- **Mute Audio Option**: Remove the audio track from videos if desired.
- **Delete Original File**: Option to delete the original video after successful processing.
- **Retry Mechanism**: The tool attempts multiple compressions to achieve the desired target size.

## Requirements

Ensure you have Python 3.x installed along with the following Python libraries:

- `Tkinter`
- `moviepy`
- `TkinterDnD2`

You can install the dependencies via `pip`:

```bash
pip install moviepy tkinterdnd2
