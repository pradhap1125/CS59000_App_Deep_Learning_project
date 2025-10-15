import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from extract_audio import extract_all_audios 

def browse_source():
    folder = filedialog.askdirectory(title="Select Source Folder (Videos)")
    if folder:
        src_entry.delete(0, tk.END)
        src_entry.insert(0, folder)

def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Folder")
    if folder:
        dst_entry.delete(0, tk.END)
        dst_entry.insert(0, folder)

def submit():
    src = src_entry.get().strip()
    dst = dst_entry.get().strip()
    if not src or not dst:
        messagebox.showerror("Missing Information", "Please select both source and destination folders.")
        return

    # Disable to prevent double-clicks
    submit_btn.config(state="disabled")

    # Optional confirmation
    messagebox.showinfo("Paths Selected", f" Source:\n{src}\n\n Destination:\n{dst}")

    
    def run_extraction():
        try:
            outputs = extract_all_audios(Path(src), Path(dst))
            out_dir = Path(dst) / "audios"

            def on_done():
                if len(outputs) == 0:
                    messagebox.showwarning(
                        "No Videos Found",
                        "I didn’t find any supported video files in the source folder.\n\n"
                        "Supported: .mp4 .mkv .avi .mov .m4v"
                    )
                    submit_btn.config(state="normal")
                else:
                    messagebox.showinfo(
                        "Audio Extraction Complete",
                        f"Extracted {len(outputs)} audio file(s).\n\nSaved to:\n{out_dir}"
                    )
                    # auto-close after success
                    root.destroy()

            root.after(0, on_done)

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Audio Extraction Error", str(e)))
            root.after(0, lambda: submit_btn.config(state="normal"))


    threading.Thread(target=run_extraction, daemon=True).start()


root = tk.Tk()
root.title("Video Transcript Generator")
root.geometry("500x250")
root.resizable(False, False)

# Heading
heading = tk.Label(root, text="Video Transcript Generator", font=("Arial", 16, "bold"))
heading.pack(pady=10)

# Frame for Source Path
frame_src = tk.Frame(root)
frame_src.pack(pady=10, fill="x", padx=30)
tk.Label(frame_src, text="Source Folder:").pack(anchor="w")
src_entry = tk.Entry(frame_src, width=50)
src_entry.pack(side="left", padx=(0, 10))
tk.Button(frame_src, text="Browse", command=browse_source).pack(side="left")

# Frame for Destination Path
frame_dst = tk.Frame(root)
frame_dst.pack(pady=10, fill="x", padx=30)
tk.Label(frame_dst, text="Destination Folder:").pack(anchor="w")
dst_entry = tk.Entry(frame_dst, width=50)
dst_entry.pack(side="left", padx=(0, 10))
tk.Button(frame_dst, text="Browse", command=browse_destination).pack(side="left")

# Submit button
submit_btn = tk.Button(root, text="Submit", width=15, font=("Arial", 12), command=submit)
submit_btn.pack(pady=20)

root.mainloop()
