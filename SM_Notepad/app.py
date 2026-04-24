import tkinter as tk
from tkinter import filedialog, messagebox, font, colorchooser
from tkinter import ttk
import os
from datetime import datetime
import re

def run():
    root = tk.Tk()
    root.title("SM-Notepad Pro - Light Mode")
    root.geometry("1000x700")

    # Variables
    current_theme = "light"
    current_font_family = "Consolas"
    current_font_size = 12
    word_wrap = True
    current_file = None
    search_highlight_tag = "search_highlight"
    
    # Text widget with scrollbar
    text_frame = tk.Frame(root)
    text_frame.pack(expand=True, fill="both")
    
    text_area = tk.Text(text_frame, undo=True, wrap="word", 
                        font=(current_font_family, current_font_size),
                        selectbackground="#0066b8", selectforeground="white")
    text_area.pack(side="left", expand=True, fill="both")
    
    scrollbar = tk.Scrollbar(text_frame, command=text_area.yview)
    scrollbar.pack(side="right", fill="y")
    text_area.config(yscrollcommand=scrollbar.set)
    
    # Status bar
    status_bar = tk.Label(root, text="Ln: 1  Col: 1  |  Words: 0  |  Chars: 0  |  Zoom: 100%", 
                          anchor="w", relief="sunken", bd=1, font=("Segoe UI", 9))
    status_bar.pack(side="bottom", fill="x")
    
    def update_status(event=None):
        """Update line, column, word, character count"""
        content = text_area.get(1.0, tk.END)
        words = len(content.split())
        chars = len(content.replace('\n', ''))
        
        # Get cursor position
        cursor_pos = text_area.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        
        zoom_percent = int((current_font_size / 12) * 100)
        status_bar.config(text=f"Ln: {line}  Col: {col}  |  Words: {words}  |  Chars: {chars}  |  Zoom: {zoom_percent}%")
    
    # Search highlight functions
    def clear_highlights():
        text_area.tag_remove(search_highlight_tag, "1.0", tk.END)
    
    def highlight_search_pattern(pattern):
        """Highlight all occurrences of search pattern"""
        clear_highlights()
        if not pattern:
            return 0
        
        count = 0
        start_pos = "1.0"
        while True:
            start_pos = text_area.search(pattern, start_pos, tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(pattern)}c"
            text_area.tag_add(search_highlight_tag, start_pos, end_pos)
            count += 1
            start_pos = end_pos
        
        text_area.tag_config(search_highlight_tag, background="yellow", foreground="black")
        return count
    
    def find_and_highlight():
        """Find text and highlight all occurrences"""
        def find_next():
            search_term = search_entry.get()
            if search_term:
                # Clear previous highlights
                clear_highlights()
                
                # Highlight all matches
                count = highlight_search_pattern(search_term)
                
                # Jump to first match
                start_pos = text_area.search(search_term, "1.0", tk.END, nocase=True)
                if start_pos:
                    end_pos = f"{start_pos}+{len(search_term)}c"
                    text_area.see(start_pos)
                    text_area.tag_add("sel", start_pos, end_pos)
                    status_label.config(text=f"Found {count} matches")
                else:
                    status_label.config(text="No matches found")
            else:
                status_label.config(text="Enter search term")
        
        find_window = tk.Toplevel(root)
        find_window.title("Find & Highlight")
        find_window.geometry("400x150")
        find_window.transient(root)
        find_window.grab_set()
        
        tk.Label(find_window, text="Search:").pack(pady=(10,0))
        search_entry = tk.Entry(find_window, width=40)
        search_entry.pack(pady=5)
        search_entry.bind("<Return>", lambda e: find_next())
        
        button_frame = tk.Frame(find_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Find All & Highlight", command=find_next, 
                 bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear Highlights", command=clear_highlights,
                 bg="#f44336", fg="white", padx=10).pack(side="left", padx=5)
        
        status_label = tk.Label(find_window, text="", fg="blue")
        status_label.pack()
        
        search_entry.focus()
    
    # Tool 1: Change Font Family
    def change_font_family():
        font_window = tk.Toplevel(root)
        font_window.title("Change Font")
        font_window.geometry("300x200")
        font_window.transient(root)
        font_window.grab_set()
        
        tk.Label(font_window, text="Select Font:").pack(pady=10)
        
        font_listbox = tk.Listbox(font_window, height=8)
        font_listbox.pack(pady=5, padx=20, fill="both", expand=True)
        
        # Get system fonts
        available_fonts = list(font.families())
        for f in available_fonts[:50]:  # Show first 50 fonts
            font_listbox.insert(tk.END, f)
        
        def apply_font():
            nonlocal current_font_family
            selection = font_listbox.curselection()
            if selection:
                current_font_family = font_listbox.get(selection)
                text_area.config(font=(current_font_family, current_font_size))
                font_window.destroy()
        
        tk.Button(font_window, text="Apply", command=apply_font, bg="#4CAF50", fg="white").pack(pady=10)
    
    # Tool 2: Font Size
    def change_font_size(delta):
        nonlocal current_font_size
        current_font_size += delta
        current_font_size = max(8, min(72, current_font_size))
        text_area.config(font=(current_font_family, current_font_size))
        update_status()
    
    # Tool 3: Toggle Theme
    def toggle_theme():
        nonlocal current_theme
        if current_theme == "light":
            text_area.config(bg="#1e1e1e", fg="#d4d4d4", insertbackground="white",
                            selectbackground="#264f78")
            root.config(bg="#1e1e1e")
            status_bar.config(bg="#007acc", fg="white")
            root.title("SM-Notepad Pro - Dark Mode")
            current_theme = "dark"
        else:
            text_area.config(bg="white", fg="black", insertbackground="black",
                            selectbackground="#0066b8")
            root.config(bg="white")
            status_bar.config(bg="white", fg="black")
            root.title("SM-Notepad Pro - Light Mode")
            current_theme = "light"
    
    # Tool 4: Word Wrap
    def toggle_word_wrap():
        nonlocal word_wrap
        word_wrap = not word_wrap
        text_area.config(wrap="word" if word_wrap else "none")
    
    # Tool 5: Insert Date/Time
    def insert_datetime():
        now = datetime.now()
        text_area.insert(tk.INSERT, now.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Tool 6: Character/Word Count
    def show_stats():
        content = text_area.get(1.0, tk.END)
        words = len(content.split())
        chars = len(content.replace('\n', ''))
        chars_with_spaces = len(content)
        lines = content.count('\n')
        
        stats_window = tk.Toplevel(root)
        stats_window.title("Document Statistics")
        stats_window.geometry("300x200")
        stats_window.transient(root)
        
        stats_text = f"""
        📊 Document Statistics:
        
        Lines: {lines}
        Words: {words}
        Characters (no spaces): {chars}
        Characters (with spaces): {chars_with_spaces}
        """
        
        tk.Label(stats_window, text=stats_text, font=("Consolas", 10), 
                justify="left").pack(pady=20)
        tk.Button(stats_window, text="OK", command=stats_window.destroy).pack()
    
    # Tool 7: Text Case Conversion
    def convert_case(case_type):
        selected = text_area.get(tk.SEL_FIRST, tk.SEL_LAST) if text_area.tag_ranges("sel") else None
        if selected:
            if case_type == "upper":
                text_area.insert(tk.INSERT, selected.upper())
            elif case_type == "lower":
                text_area.insert(tk.INSERT, selected.lower())
            elif case_type == "title":
                text_area.insert(tk.INSERT, selected.title())
            text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            messagebox.showinfo("No Selection", "Please select text first")
    
    # Tool 8: Search and Replace with Highlight
    def search_replace():
        def replace_all():
            search_term = search_entry.get()
            replace_term = replace_entry.get()
            if search_term:
                content = text_area.get(1.0, tk.END)
                new_content = content.replace(search_term, replace_term)
                text_area.delete(1.0, tk.END)
                text_area.insert(1.0, new_content)
                messagebox.showinfo("Replace", "Replace completed!")
                replace_window.destroy()
            else:
                messagebox.showwarning("Warning", "Enter search term")
        
        replace_window = tk.Toplevel(root)
        replace_window.title("Search & Replace")
        replace_window.geometry("400x160")
        replace_window.transient(root)
        replace_window.grab_set()
        
        tk.Label(replace_window, text="Find:").grid(row=0, column=0, padx=10, pady=10)
        search_entry = tk.Entry(replace_window, width=35)
        search_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(replace_window, text="Replace:").grid(row=1, column=0, padx=10, pady=10)
        replace_entry = tk.Entry(replace_window, width=35)
        replace_entry.grid(row=1, column=1, padx=10, pady=10)
        
        button_frame = tk.Frame(replace_window)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, text="Replace All", command=replace_all,
                 bg="#FF9800", fg="white", padx=15).pack(side="left", padx=5)
    
    # Tool 9: Remove Extra Spaces
    def remove_extra_spaces():
        content = text_area.get(1.0, tk.END)
        cleaned = re.sub(' +', ' ', content)
        text_area.delete(1.0, tk.END)
        text_area.insert(1.0, cleaned)
    
    # Tool 10: Line Numbers (Toggle)
    show_line_numbers = False
    line_number_bar = None
    
    def toggle_line_numbers():
        nonlocal show_line_numbers, line_number_bar
        show_line_numbers = not show_line_numbers
        if show_line_numbers:
            line_number_bar = tk.Text(text_frame, width=5, padx=3, takefocus=0, border=0,
                                     background="#f0f0f0", state="disabled", wrap="none")
            line_number_bar.pack(side="left", fill="y")
            update_line_numbers()
            text_area.bind("<KeyRelease>", update_line_numbers)
            text_area.bind("<MouseWheel>", update_line_numbers)
        else:
            if line_number_bar:
                line_number_bar.destroy()
                line_number_bar = None
    
    def update_line_numbers(event=None):
        if line_number_bar:
            line_number_bar.config(state="normal")
            line_number_bar.delete(1.0, tk.END)
            lines = int(text_area.index('end-1c').split('.')[0])
            line_numbers = '\n'.join(str(i) for i in range(1, lines+1))
            line_number_bar.insert(1.0, line_numbers)
            line_number_bar.config(state="disabled")
    
    # Tool 11: Save As
    def save_as():
        nonlocal current_file
        file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file:
            current_file = file
            with open(file, "w", encoding="utf-8") as f:
                f.write(text_area.get(1.0, tk.END))
            root.title(f"SM-Notepad Pro - {os.path.basename(file)}")
            messagebox.showinfo("Saved", f"File saved as {os.path.basename(file)}")
    
    # Tool 12: Print
    def print_text():
        content = text_area.get(1.0, tk.END)
        print_window = tk.Toplevel(root)
        print_window.title("Print Preview")
        print_window.geometry("500x400")
        
        text_display = tk.Text(print_window, wrap="word")
        text_display.pack(expand=True, fill="both", padx=10, pady=10)
        text_display.insert(1.0, content)
        text_display.config(state="disabled")
        
        tk.Button(print_window, text="Close", command=print_window.destroy).pack(pady=5)
    
    # Tool 13: Select All
    def select_all():
        text_area.tag_add(tk.SEL, "1.0", tk.END)
        text_area.mark_set(tk.INSERT, "1.0")
        text_area.see(tk.INSERT)
    
    # Tool 14: Clear All
    def clear_all():
        if messagebox.askyesno("Clear All", "Clear all text? This cannot be undone!"):
            text_area.delete(1.0, tk.END)
    
    # Tool 15: About
    def about():
        about_text = """
        📝 SM-Notepad Pro v1.0
        
        A powerful text editor with:
        • 15+ Professional Tools
        • Search & Highlight
        • Dark/Light Theme
        • Custom Fonts
        • Line Numbers
        • Document Statistics
        • And much more!
        
        Created with Python & Tkinter
        """
        messagebox.showinfo("About SM-Notepad Pro", about_text)
    
    # File operations
    def new_file():
        nonlocal current_file
        text_area.delete(1.0, tk.END)
        current_file = None
        root.title("SM-Notepad Pro - New File")
        update_status()
    
    def open_file():
        nonlocal current_file
        file = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file:
            current_file = file
            with open(file, "r", encoding="utf-8") as f:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, f.read())
            root.title(f"SM-Notepad Pro - {os.path.basename(file)}")
            update_status()
    
    def save_file():
        nonlocal current_file
        if current_file:
            with open(current_file, "w", encoding="utf-8") as f:
                f.write(text_area.get(1.0, tk.END))
            messagebox.showinfo("Saved", "File saved successfully!")
        else:
            save_as()
    
    def exit_app():
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            root.quit()
    
    # Bind events
    text_area.bind("<KeyRelease>", update_status)
    text_area.bind("<ButtonRelease-1>", update_status)
    
    # Create menu bar
    menu = tk.Menu(root)
    root.config(menu=menu)
    
    # File Menu
    file_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New", command=new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Open", command=open_file, accelerator="Ctrl+O")
    file_menu.add_command(label="Save", command=save_file, accelerator="Ctrl+S")
    file_menu.add_command(label="Save As", command=save_as, accelerator="Ctrl+Shift+S")
    file_menu.add_separator()
    file_menu.add_command(label="Print Preview", command=print_text)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=exit_app)
    
    # Edit Menu
    edit_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Find & Highlight", command=find_and_highlight, accelerator="Ctrl+F")
    edit_menu.add_command(label="Search & Replace", command=search_replace, accelerator="Ctrl+H")
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=select_all, accelerator="Ctrl+A")
    edit_menu.add_command(label="Clear All", command=clear_all)
    edit_menu.add_separator()
    edit_menu.add_command(label="Insert Date/Time", command=insert_datetime, accelerator="Ctrl+T")
    
    # Format Menu
    format_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Format", menu=format_menu)
    format_menu.add_command(label="Change Font", command=change_font_family)
    format_menu.add_command(label="Increase Font Size", command=lambda: change_font_size(1), accelerator="Ctrl++")
    format_menu.add_command(label="Decrease Font Size", command=lambda: change_font_size(-1), accelerator="Ctrl+-")
    format_menu.add_separator()
    format_menu.add_command(label="UPPERCASE", command=lambda: convert_case("upper"))
    format_menu.add_command(label="lowercase", command=lambda: convert_case("lower"))
    format_menu.add_command(label="Title Case", command=lambda: convert_case("title"))
    format_menu.add_separator()
    format_menu.add_command(label="Remove Extra Spaces", command=remove_extra_spaces)
    
    # View Menu
    view_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Dark Mode", command=toggle_theme, accelerator="Ctrl+D")
    view_menu.add_command(label="Toggle Word Wrap", command=toggle_word_wrap, accelerator="Ctrl+W")
    view_menu.add_command(label="Show Line Numbers", command=toggle_line_numbers)
    view_menu.add_command(label="Document Statistics", command=show_stats, accelerator="Ctrl+I")
    
    # Tools Menu
    tools_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Tools", menu=tools_menu)
    tools_menu.add_command(label="Word Count", command=show_stats)
    tools_menu.add_command(label="Remove Extra Spaces", command=remove_extra_spaces)
    
    # Help Menu
    help_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=about)
    
    # Keyboard shortcuts
    root.bind("<Control-n>", lambda e: new_file())
    root.bind("<Control-o>", lambda e: open_file())
    root.bind("<Control-s>", lambda e: save_file())
    root.bind("<Control-Shift-S>", lambda e: save_as())
    root.bind("<Control-f>", lambda e: find_and_highlight())
    root.bind("<Control-h>", lambda e: search_replace())
    root.bind("<Control-a>", lambda e: select_all())
    root.bind("<Control-t>", lambda e: insert_datetime())
    root.bind("<Control-plus>", lambda e: change_font_size(1))
    root.bind("<Control-minus>", lambda e: change_font_size(-1))
    root.bind("<Control-d>", lambda e: toggle_theme())
    root.bind("<Control-w>", lambda e: toggle_word_wrap())
    root.bind("<Control-i>", lambda e: show_stats())
    
    update_status()
    root.mainloop()

if __name__ == "__main__":
    run()
