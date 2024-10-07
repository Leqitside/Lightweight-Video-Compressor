import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from moviepy.editor import VideoFileClip
import threading
import os


def format_time(seconds):
    """Converts seconds into MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"


def parse_time(time_str):
    """Parses a time string formatted as HH:MM:SS, MM:SS, or SS into seconds."""
    if not time_str:
        return None  # None signifies full duration for end time.
    parts = list(map(int, time_str.split(":")))
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]


def process_video(path, start_time, end_time, target_size, mute_audio, delete_original, attempt=1,
                  initial_bitrate=None):
    try:
        clip = VideoFileClip(path)
        start_seconds = parse_time(start_time) if start_time else 0
        end_seconds = parse_time(end_time) if end_time else clip.duration

        clip = clip.subclip(start_seconds, end_seconds)
        if mute_audio:
            clip = clip.without_audio()

        target_size_bytes = int((target_size - 1) * 1024 * 1024 * 0.95)
        if attempt == 1:
            bitrate = int(target_size_bytes * 8 / clip.duration)
            initial_bitrate = bitrate
        else:
            current_size = os.path.getsize(os.path.splitext(path)[0] + "_cut.mp4")
            size_ratio = current_size / target_size_bytes
            bitrate = int(initial_bitrate / size_ratio * 0.95)

        output_filename = os.path.splitext(path)[0] + "_cut.mp4"
        clip.write_videofile(output_filename, bitrate=str(bitrate), preset='fast', threads=4)

        current_size = os.path.getsize(output_filename)
        print(f"Attempt {attempt}: Output file size is {current_size / 1024 / 1024:.2f} MB.")
        if current_size > target_size_bytes and attempt < 5:
            print(f"File too large. Retrying with adjusted bitrate...")
            return process_video(path, start_time, end_time, target_size, mute_audio, delete_original, attempt + 1,
                                 initial_bitrate)
        elif attempt >= 5:
            print("Failed to compress to the desired size after multiple attempts.")
            return None

        if delete_original:
            os.remove(path)  # Delete the original video file
            print(f"Deleted original video: {path}")

        return output_filename
    except Exception as e:
        print(f"Error processing video: {e}")
        return None


class TimeInputDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Start Time (HH:MM:SS or MM:SS or SS):").grid(row=0)
        tk.Label(master, text="End Time (HH:MM:SS or MM:SS or SS):").grid(row=1)
        tk.Label(master, text="Target Size in MB:").grid(row=2)
        tk.Label(master, text="Mute Audio:").grid(row=3)
        tk.Label(master, text="Delete Original Video:").grid(row=4)

        self.start_entry = tk.Entry(master)
        self.end_entry = tk.Entry(master)
        self.size_entry = tk.Entry(master)
        self.mute_audio = tk.BooleanVar()
        self.delete_video = tk.BooleanVar()

        self.start_entry.grid(row=0, column=1)
        self.end_entry.grid(row=1, column=1)
        self.size_entry.grid(row=2, column=1)
        self.size_entry.insert(0, "25")  # Set default size to 25MB
        tk.Checkbutton(master, variable=self.mute_audio).grid(row=3, column=1)
        tk.Checkbutton(master, text="", variable=self.delete_video).grid(row=4, column=1)
        return self.start_entry  # initial focus

    def apply(self):
        self.start_time = self.start_entry.get()
        self.end_time = self.end_entry.get()
        self.target_size = float(self.size_entry.get())
        self.mute_audio = self.mute_audio.get()
        self.delete_video = self.delete_video.get()


def on_drop(event):
    file_path = event.data.strip('\'" {}')
    if file_path.lower().endswith('.mp4'):
        root.withdraw()  # Hide the main window
        dialog = TimeInputDialog(root, title="Video Processing Options")
        if hasattr(dialog, 'start_time'):
            threading.Thread(target=lambda: process_and_feedback(file_path, dialog), daemon=True).start()
        else:
            root.destroy()  # Exit the program if the dialog is cancelled
    else:
        messagebox.showerror("Error", "Please drop an MP4 file.")



def process_and_feedback(file_path, dialog):
    output_path = process_video(file_path, dialog.start_time, dialog.end_time, dialog.target_size, dialog.mute_audio,
                                dialog.delete_video)
    if output_path:
        messagebox.showinfo("Success", f"Video processing complete. File saved successfully at {output_path}")
    else:
        messagebox.showerror("Failure", "Failed to achieve target size or process video.")
    os._exit(0)  # Ensures all threads close when the main operation is done


def main():
    global root
    root = TkinterDnD.Tk()
    root.title("Drag and drop an MP4 file here")
    label = tk.Label(root, text="Drag and drop an MP4 file here", pady=100, padx=100)
    label.pack(expand=True, fill=tk.BOTH)
    label.drop_target_register(DND_FILES)
    label.dnd_bind('<<Drop>>', on_drop)
    root.mainloop()


if __name__ == "__main__":
    main()