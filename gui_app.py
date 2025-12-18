import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class AI_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Image Reader Project")
        self.root.geometry("600x500")

        self.btn_select = tk.Button(
            root, 
            text="Select Image", 
            command=self.open_file,
            font=("Arial", 12),
            bg="#4CAF50", 
            fg="white"
        )
        self.btn_select.pack(pady=20)

        self.lbl_image = tk.Label(root, text="No image selected")
        self.lbl_image.pack(pady=10)

        self.lbl_output = tk.Label(
            root, 
            text="AI Output will appear here...", 
            font=("Arial", 10, "italic"),
            wraplength=500
        )
        self.lbl_output.pack(pady=20)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )

        if file_path:
            self.display_image(file_path)
            self.run_ai_processing(file_path)

    def display_image(self, path):
        img = Image.open(path)

        img.thumbnail((400, 300))

        self.photo = ImageTk.PhotoImage(img)

        self.lbl_image.config(image=self.photo, text="") 
        self.lbl_image.image = self.photo 

    def run_ai_processing(self, file_path):
        print(f"Processing image at: {file_path}")
        
        dummy_result = "Detected: A cat sitting on a table."
        self.lbl_output.config(text=f"Result: {dummy_result}", fg="blue")

if __name__ == "__main__":
    root = tk.Tk()
    app = AI_GUI(root)
    root.mainloop()