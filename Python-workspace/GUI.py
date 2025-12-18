import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import json

# Integration pipeline import (may be heavy); handle import errors gracefully
try:
    import Integration_pipeline
except Exception as e:
    Integration_pipeline = None
    _integration_import_error = str(e)


class AI_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Image Reader Project")
        self.root.geometry("700x560")

        # Path entry + browse
        frame = tk.Frame(root)
        frame.pack(pady=10, fill="x", padx=10)

        self.path_var = tk.StringVar()
        self.entry_path = tk.Entry(frame, textvariable=self.path_var, width=60)
        self.entry_path.pack(side="left", padx=(0, 8), expand=True, fill="x")

        btn_browse = tk.Button(frame, text="Browse", command=self.open_file)
        btn_browse.pack(side="left")

        # OCR engine selector
        engine_frame = tk.Frame(root)
        engine_frame.pack(pady=6)
        tk.Label(engine_frame, text="OCR Engine:").pack(side="left")
        self.ocr_choice = tk.StringVar(value='auto')
        engine_menu = tk.OptionMenu(engine_frame, self.ocr_choice, 'auto', 'paddle', 'pytesseract', 'pytesseract_first')
        engine_menu.pack(side="left", padx=8)

        btn_run = tk.Button(root, text="Run Pipeline", command=self.on_run, bg="#1976D2", fg="white")
        btn_run.pack(pady=8)

        # Image preview
        self.lbl_image = tk.Label(root, text="No image selected")
        self.lbl_image.pack(pady=10)

        # Output area (pretty JSON)
        self.lbl_output = tk.Label(root, text="AI Output will appear here...", font=("Arial", 10, "italic"), wraplength=650, justify="left")
        self.lbl_output.pack(pady=6)

        # Raw text area (scrollable)
        raw_frame = tk.Frame(root)
        raw_frame.pack(padx=10, fill="both", expand=False)
        raw_label = tk.Label(raw_frame, text="Raw extracted text:")
        raw_label.pack(anchor="w")
        self.txt_raw = tk.Text(raw_frame, height=10, wrap="word")
        self.txt_raw.pack(side="left", fill="both", expand=True)
        raw_scroll = tk.Scrollbar(raw_frame, command=self.txt_raw.yview)
        raw_scroll.pack(side="right", fill="y")
        self.txt_raw.config(yscrollcommand=raw_scroll.set)

        # Status
        self.status = tk.Label(root, text="Ready", anchor="w")
        self.status.pack(side="bottom", fill="x")

        # Integration system instance (lazy)
        self.system = None

    def open_file(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
        if file_path:
            self.path_var.set(file_path)
            self.display_image(file_path)

    def display_image(self, path):
        try:
            img = Image.open(path)
        except Exception:
            self.lbl_image.config(text="Unable to open image")
            return

        img.thumbnail((560, 360))
        self.photo = ImageTk.PhotoImage(img)
        self.lbl_image.config(image=self.photo, text="")
        self.lbl_image.image = self.photo

    def on_run(self):
        path = self.path_var.get().strip()
        if not path:
            self.lbl_output.config(text="Please select or enter an image path.", fg="red")
            return

        # Launch processing in a background thread to keep UI responsive
        thread = threading.Thread(target=self.run_pipeline_thread, args=(path,), daemon=True)
        thread.start()

    def run_pipeline_thread(self, path):
        self.status.config(text="Processing...")
        self.lbl_output.config(text="Processing... please wait.")

        if Integration_pipeline is None:
            msg = f"Integration pipeline not available: {_integration_import_error}"
            self.lbl_output.config(text=msg, fg="red")
            self.status.config(text="Error")
            return

        try:
            if self.system is None:
                self.system = Integration_pipeline.MCORRSystem()

            result = self.system.process_receipt(path, ocr_engine=self.ocr_choice.get())
            pretty = json.dumps(result, indent=2, ensure_ascii=False)
            # Extract raw text lines (dicts with 'text' and optional 'conf')
            raw_lines = []
            if isinstance(result, dict) and "raw_text" in result and result["raw_text"]:
                for item in result["raw_text"]:
                    if isinstance(item, dict) and 'text' in item:
                        conf = item.get('conf')
                        if conf is not None:
                            raw_lines.append(f"{item['text']}  (conf={conf})")
                        else:
                            raw_lines.append(item['text'])
                    elif isinstance(item, (list, tuple)) and len(item) >= 1:
                        raw_lines.append(str(item[0]))
                    else:
                        raw_lines.append(str(item))

            raw_text_display = "\n".join(raw_lines) if raw_lines else "(no raw text extracted)"

            # Update UI on main thread
            self.root.after(0, lambda: self.lbl_output.config(text=pretty, fg="black"))
            self.root.after(0, lambda: self.txt_raw.delete("1.0", tk.END))
            self.root.after(0, lambda: self.txt_raw.insert(tk.END, raw_text_display))
            self.root.after(0, lambda: self.status.config(text="Done"))
        except Exception as e:
            self.root.after(0, lambda: self.lbl_output.config(text=f"Error: {e}", fg="red"))
            self.root.after(0, lambda: self.status.config(text="Error"))


if __name__ == "__main__":
    root = tk.Tk()
    app = AI_GUI(root)
    root.mainloop()