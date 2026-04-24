import tkinter as tk
from tkinter import filedialog, messagebox

def run():
    root = tk.Tk()
    root.title("SM-Notepad")
    root.geometry("800x500")

    text_area = tk.Text(root, undo=True, wrap="word")
    text_area.pack(expand=True, fill="both")

    def new_file():
        text_area.delete(1.0, tk.END)

    def open_file():
        file = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file:
            with open(file, "r", encoding="utf-8") as f:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, f.read())

    def save_file():
        file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(text_area.get(1.0, tk.END))

    menu = tk.Menu(root)
    root.config(menu=menu)

    file_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New", command=new_file)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    root.mainloop()
