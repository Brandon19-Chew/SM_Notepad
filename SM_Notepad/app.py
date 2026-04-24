import tkinter as tk
from tkinter import filedialog, messagebox, font, ttk, colorchooser
import os
from datetime import datetime
import re

def run():
    root = tk.Tk()
    root.title("SM-Notepad Pro - Light Mode")
    root.geometry("1200x800")
    root.configure(bg='#f5f5f5')

    # ─── Custom Dialog Class ───────────────────────────────────────────────────
    class CustomDialog:
        @staticmethod
        def _base(parent, title, w, h):
            d = tk.Toplevel(parent)
            d.title(title); d.geometry(f"{w}x{h}")
            d.configure(bg='#f5f5f5'); d.transient(parent)
            d.grab_set(); d.resizable(False, False)
            d.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width()  - w) // 2
            y = parent.winfo_y() + (parent.winfo_height() - h) // 2
            d.geometry(f"+{x}+{y}")
            return d

        @staticmethod
        def show_info(parent, title, message, icon="ℹ️"):
            d = CustomDialog._base(parent, title, 400, 200)
            tk.Label(d, text=icon,    font=("Segoe UI", 48), bg='#f5f5f5').pack(pady=(20,5))
            tk.Label(d, text=message, font=("Segoe UI", 11), bg='#f5f5f5', wraplength=350).pack(pady=10)
            tk.Button(d, text="✓ OK", command=d.destroy,
                      bg="#4CAF50", fg="white", padx=30, pady=5,
                      cursor='hand2', font=("Segoe UI", 10, "bold"), relief='flat').pack(pady=10)

        @staticmethod
        def show_warning(parent, title, message, icon="⚠️"):
            d = CustomDialog._base(parent, title, 400, 200)
            tk.Label(d, text=icon,    font=("Segoe UI", 48), bg='#f5f5f5').pack(pady=(20,5))
            tk.Label(d, text=message, font=("Segoe UI", 11), bg='#f5f5f5',
                     wraplength=350, fg='#f57c00').pack(pady=10)
            tk.Button(d, text="✓ OK", command=d.destroy,
                      bg="#FF9800", fg="white", padx=30, pady=5,
                      cursor='hand2', font=("Segoe UI", 10, "bold"), relief='flat').pack(pady=10)

        @staticmethod
        def show_error(parent, title, message, icon="❌"):
            d = CustomDialog._base(parent, title, 400, 200)
            tk.Label(d, text=icon,    font=("Segoe UI", 48), bg='#f5f5f5').pack(pady=(20,5))
            tk.Label(d, text=message, font=("Segoe UI", 11), bg='#f5f5f5',
                     wraplength=350, fg='#d32f2f').pack(pady=10)
            tk.Button(d, text="✓ OK", command=d.destroy,
                      bg="#f44336", fg="white", padx=30, pady=5,
                      cursor='hand2', font=("Segoe UI", 10, "bold"), relief='flat').pack(pady=10)

        @staticmethod
        def show_question(parent, title, message, icon="❓"):
            result = [False]
            d = CustomDialog._base(parent, title, 450, 220)
            tk.Label(d, text=icon,    font=("Segoe UI", 48), bg='#f5f5f5').pack(pady=(20,5))
            tk.Label(d, text=message, font=("Segoe UI", 11), bg='#f5f5f5', wraplength=380).pack(pady=10)
            bf = tk.Frame(d, bg='#f5f5f5'); bf.pack(pady=15)
            def yes(): result[0]=True;  d.destroy()
            def no():  result[0]=False; d.destroy()
            tk.Button(bf, text="✓ Yes", command=yes,
                      bg="#4CAF50", fg="white", padx=25, pady=5,
                      cursor='hand2', font=("Segoe UI", 10, "bold"), relief='flat').pack(side="left", padx=10)
            tk.Button(bf, text="✗ No",  command=no,
                      bg="#757575", fg="white", padx=25, pady=5,
                      cursor='hand2', font=("Segoe UI", 10, "bold"), relief='flat').pack(side="left", padx=10)
            parent.wait_window(d)
            return result[0]

        @staticmethod
        def show_success(parent, message):
            d = CustomDialog._base(parent, "✅ Success", 400, 200)
            tk.Label(d, text="✅",     font=("Segoe UI", 48), bg='#f5f5f5').pack(pady=(20,5))
            tk.Label(d, text=message, font=("Segoe UI", 11), bg='#f5f5f5',
                     wraplength=350, fg='#4CAF50').pack(pady=10)
            tk.Button(d, text="✓ OK", command=d.destroy,
                      bg="#4CAF50", fg="white", padx=30, pady=5,
                      cursor='hand2', font=("Segoe UI", 10, "bold"), relief='flat').pack(pady=10)

    # ─── State ────────────────────────────────────────────────────────────────
    current_theme       = "light"
    current_font_family = "Segoe UI"
    current_font_size   = 12
    word_wrap           = True
    current_file        = None
    search_highlight_tag= "search_highlight"
    show_line_numbers   = False
    line_number_bar     = None
    text_color          = "#000000"
    highlight_color     = "#ffff00"

    # ─── Layout ───────────────────────────────────────────────────────────────
    main_container = tk.Frame(root, bg='#f5f5f5')
    main_container.pack(expand=True, fill="both", padx=10, pady=10)

    toolbar = tk.Frame(main_container, bg='#e0e0e0', height=52)
    toolbar.pack(fill="x", pady=(0, 2))
    toolbar.pack_propagate(False)

    fmt_toolbar = tk.Frame(main_container, bg='#ececec', height=52)
    fmt_toolbar.pack(fill="x", pady=(0, 4))
    fmt_toolbar.pack_propagate(False)

    status_frame = tk.Frame(main_container, bg='#2c3e50', height=30)
    status_frame.pack(side="bottom", fill="x", pady=(5, 0))
    status_frame.pack_propagate(False)

    text_frame = tk.Frame(main_container, bg='white')
    text_frame.pack(expand=True, fill="both")

    text_area = tk.Text(text_frame, undo=True, wrap="word",
                        font=(current_font_family, current_font_size),
                        selectbackground="#0066b8", selectforeground="white",
                        relief='flat', borderwidth=0, padx=10, pady=10)
    text_area.pack(side="left", expand=True, fill="both")

    scrollbar = tk.Scrollbar(text_frame, command=text_area.yview, width=10)
    scrollbar.pack(side="right", fill="y")
    text_area.config(yscrollcommand=scrollbar.set)

    status_bar = tk.Label(status_frame,
                          text="Ln: 1  Col: 1  |  Words: 0  |  Chars: 0  |  Zoom: 100%",
                          anchor="w", bg='#2c3e50', fg='white', font=("Segoe UI", 9))
    status_bar.pack(side="left", fill="x", padx=10, pady=5)

    file_status = tk.Label(status_frame, text="No file opened",
                           bg='#2c3e50', fg='#95a5a6', font=("Segoe UI", 9))
    file_status.pack(side="right", padx=10, pady=5)

    # ─── Helpers ──────────────────────────────────────────────────────────────
    def update_status(event=None):
        content = text_area.get(1.0, tk.END)
        words   = len(content.split())
        chars   = len(content.replace('\n', ''))
        line, col = text_area.index(tk.INSERT).split('.')
        zoom    = int((current_font_size / 12) * 100)
        status_bar.config(text=f"Ln: {line}  |  Col: {col}  |  Words: {words}  |  Chars: {chars}  |  Zoom: {zoom}%")

    def clear_highlights():
        text_area.tag_remove(search_highlight_tag, "1.0", tk.END)

    def highlight_search_pattern(pattern):
        clear_highlights()
        if not pattern:
            return 0
        count, start = 0, "1.0"
        while True:
            pos = text_area.search(pattern, start, tk.END, nocase=True)
            if not pos: break
            end = f"{pos}+{len(pattern)}c"
            text_area.tag_add(search_highlight_tag, pos, end)
            count += 1; start = end
        text_area.tag_config(search_highlight_tag,
                             background="#ffeb3b", foreground="#000000",
                             font=(current_font_family, current_font_size, "bold"))
        return count

    # ─── Formatting tag helpers ───────────────────────────────────────────────
    def apply_tag(tag_name, **kw):
        try:
            sel_start = text_area.index(tk.SEL_FIRST)
            sel_end   = text_area.index(tk.SEL_LAST)
        except tk.TclError:
            return
        text_area.tag_configure(tag_name, **kw)
        ranges = text_area.tag_ranges(tag_name)
        already = False
        for i in range(0, len(ranges), 2):
            if (text_area.compare(ranges[i],   "<=", sel_start) and
                text_area.compare(ranges[i+1], ">=", sel_end)):
                already = True; break
        if already:
            text_area.tag_remove(tag_name, sel_start, sel_end)
        else:
            text_area.tag_add(tag_name, sel_start, sel_end)

    def _font_tag(weight=None, slant=None, underline=False):
        parts = []
        if weight    == "bold":      parts.append("bold")
        if slant     == "italic":    parts.append("italic")
        if underline:                parts.append("underline")
        return "fmt_" + "_".join(parts) if parts else "fmt_normal"

    def toggle_bold():
        try:
            s, e = text_area.index(tk.SEL_FIRST), text_area.index(tk.SEL_LAST)
        except tk.TclError: return
        tag = "fmt_bold"
        text_area.tag_configure(tag, font=(current_font_family, current_font_size, "bold"))
        _toggle_range_tag(tag, s, e)

    def toggle_italic():
        try:
            s, e = text_area.index(tk.SEL_FIRST), text_area.index(tk.SEL_LAST)
        except tk.TclError: return
        tag = "fmt_italic"
        text_area.tag_configure(tag, font=(current_font_family, current_font_size, "italic"))
        _toggle_range_tag(tag, s, e)

    def toggle_underline():
        try:
            s, e = text_area.index(tk.SEL_FIRST), text_area.index(tk.SEL_LAST)
        except tk.TclError: return
        tag = "fmt_underline"
        text_area.tag_configure(tag, underline=True)
        _toggle_range_tag(tag, s, e)

    def _toggle_range_tag(tag, start, end):
        ranges = text_area.tag_ranges(tag)
        already = any(
            text_area.compare(ranges[i],   "<=", start) and
            text_area.compare(ranges[i+1], ">=", end)
            for i in range(0, len(ranges), 2)
        )
        if already:
            text_area.tag_remove(tag, start, end)
        else:
            text_area.tag_add(tag, start, end)

    def set_heading(size, label):
        try:
            s, e = text_area.index(tk.SEL_FIRST), text_area.index(tk.SEL_LAST)
        except tk.TclError: return
        tag = f"heading_{size}"
        text_area.tag_configure(tag, font=(current_font_family, size, "bold"))
        _toggle_range_tag(tag, s, e)

    def apply_text_color():
        nonlocal text_color
        color = colorchooser.askcolor(color=text_color, title="Choose Text Color")[1]
        if color:
            text_color = color
            try:
                s, e = text_area.index(tk.SEL_FIRST), text_area.index(tk.SEL_LAST)
            except tk.TclError: return
            tag = f"color_{color.replace('#','')}"
            text_area.tag_configure(tag, foreground=color)
            text_area.tag_add(tag, s, e)
            color_btn.config(fg=color)

    def apply_highlight_color():
        nonlocal highlight_color
        color = colorchooser.askcolor(color=highlight_color, title="Choose Highlight Color")[1]
        if color:
            highlight_color = color
            try:
                s, e = text_area.index(tk.SEL_FIRST), text_area.index(tk.SEL_LAST)
            except tk.TclError: return
            tag = f"bg_{color.replace('#','')}"
            text_area.tag_configure(tag, background=color)
            text_area.tag_add(tag, s, e)
            hi_btn.config(bg=color)

    def set_align(justify):
        try:
            s = text_area.index(tk.SEL_FIRST + " linestart")
            e = text_area.index(tk.SEL_LAST  + " lineend")
        except tk.TclError:
            s = text_area.index("insert linestart")
            e = text_area.index("insert lineend")
        tag = f"align_{justify}"
        text_area.tag_configure(tag, justify=justify)
        for j in ("left", "center", "right"):
            text_area.tag_remove(f"align_{j}", s, e)
        text_area.tag_add(tag, s, e)

    # ─── Live Search bar ──────────────────────────────────────────────────────
    search_bar_visible = [False]
    search_match_index = [0]

    search_bar = tk.Frame(main_container, bg='#fff9e6', height=36)

    search_var = tk.StringVar()
    tk.Label(search_bar, text="🔍 Find:", bg='#fff9e6',
             font=("Segoe UI", 9, "bold")).pack(side="left", padx=(8,4), pady=6)
    search_entry_bar = tk.Entry(search_bar, textvariable=search_var, width=30,
                                font=("Segoe UI", 10), relief='solid', bd=1)
    search_entry_bar.pack(side="left", padx=4, pady=5)
    search_count_lbl = tk.Label(search_bar, text="", bg='#fff9e6',
                                fg='#555', font=("Segoe UI", 9))
    search_count_lbl.pack(side="left", padx=6)

    def _live_search(*_):
        term = search_var.get()
        n = highlight_search_pattern(term)
        if term:
            search_count_lbl.config(text=f"{n} match{'es' if n!=1 else ''}")
        else:
            search_count_lbl.config(text="")

    search_var.trace_add("write", _live_search)

    def _search_next(direction=1):
        term = search_var.get()
        if not term: return
        positions, pos = [], "1.0"
        while True:
            p = text_area.search(term, pos, tk.END, nocase=True)
            if not p: break
            positions.append(p)
            pos = f"{p}+{len(term)}c"
        if not positions: return
        idx = search_match_index[0] % len(positions)
        if direction == -1:
            idx = (idx - 2) % len(positions)
        mp  = positions[idx]
        end = f"{mp}+{len(term)}c"
        text_area.tag_remove("sel", "1.0", tk.END)
        text_area.tag_add("sel", mp, end)
        text_area.see(mp)
        search_match_index[0] = idx + 1

    tk.Button(search_bar, text="▲", command=lambda: _search_next(-1),
              bg='#e0e0e0', relief='flat', width=2, cursor='hand2').pack(side="left")
    tk.Button(search_bar, text="▼", command=lambda: _search_next(1),
              bg='#e0e0e0', relief='flat', width=2, cursor='hand2').pack(side="left")
    tk.Button(search_bar, text="✕", command=lambda: toggle_search_bar(),
              bg='#e0e0e0', relief='flat', width=2, cursor='hand2').pack(side="left", padx=(4,0))

    def toggle_search_bar():
        if search_bar_visible[0]:
            search_bar.pack_forget()
            search_bar_visible[0] = False
            clear_highlights()
        else:
            search_bar.pack(fill="x", after=fmt_toolbar, pady=(0,2))
            search_bar_visible[0] = True
            search_entry_bar.focus_set()

    def find_and_highlight():
        toggle_search_bar()

    # ─── Font & Zoom ──────────────────────────────────────────────────────────
    def change_font_family():
        def apply_font():
            sel = font_listbox.curselection()
            if sel:
                nonlocal current_font_family
                current_font_family = font_listbox.get(sel)
                text_area.config(font=(current_font_family, current_font_size))
                CustomDialog.show_success(root, f"Font changed to {current_font_family}")
                fw.destroy()
        fw = tk.Toplevel(root); fw.title("🔤 Change Font")
        fw.geometry("400x450"); fw.configure(bg='#f5f5f5')
        fw.transient(root); fw.grab_set()
        tk.Label(fw, text="Select Font:", font=("Segoe UI", 11, "bold"), bg='#f5f5f5').pack(pady=10)
        lf = tk.Frame(fw, bg='#f5f5f5'); lf.pack(pady=5, padx=20, fill="both", expand=True)
        sc = tk.Scrollbar(lf); sc.pack(side="right", fill="y")
        font_listbox = tk.Listbox(lf, height=15, yscrollcommand=sc.set, font=("Segoe UI", 10))
        font_listbox.pack(side="left", fill="both", expand=True)
        sc.config(command=font_listbox.yview)
        for f in sorted(font.families()):
            font_listbox.insert(tk.END, f)
        tk.Button(fw, text="✓ Apply", command=apply_font,
                  bg="#4CAF50", fg="white", padx=20, pady=5,
                  cursor='hand2', font=("Segoe UI", 10)).pack(pady=15)

    def zoom_in():
        nonlocal current_font_size
        if current_font_size < 72:
            current_font_size += 1
            text_area.config(font=(current_font_family, current_font_size))
            update_status()

    def zoom_out():
        nonlocal current_font_size
        if current_font_size > 8:
            current_font_size -= 1
            text_area.config(font=(current_font_family, current_font_size))
            update_status()

    # ─── Theme ────────────────────────────────────────────────────────────────
    def toggle_theme():
        nonlocal current_theme
        if current_theme == "light":
            tb_bg  = "#3c3c3c"
            fmt_bg = "#2d2d2d"
            text_area.config(bg="#1e1e1e", fg="#d4d4d4",
                             insertbackground="white", selectbackground="#264f78")
            main_container.config(bg="#1e1e1e")
            toolbar.config(bg=tb_bg)
            fmt_toolbar.config(bg=fmt_bg)
            status_frame.config(bg="#007acc")
            status_bar.config(bg="#007acc", fg="white")
            file_status.config(bg="#007acc", fg="white")
            search_bar.config(bg="#2a2a2a")
            root.title("SM-Notepad Pro - Dark Mode")
            current_theme = "dark"
        else:
            tb_bg  = "#e0e0e0"
            fmt_bg = "#ececec"
            text_area.config(bg="white", fg="black",
                             insertbackground="black", selectbackground="#0066b8")
            main_container.config(bg="#f5f5f5")
            toolbar.config(bg=tb_bg)
            fmt_toolbar.config(bg=fmt_bg)
            status_frame.config(bg="#2c3e50")
            status_bar.config(bg="#2c3e50", fg="white")
            file_status.config(bg="#2c3e50", fg="#95a5a6")
            search_bar.config(bg="#fff9e6")
            root.title("SM-Notepad Pro - Light Mode")
            current_theme = "light"

        for (canvas, outer_frame, lbl_widget, draw_fn) in all_icon_btns:
            par_bg = outer_frame.master.cget('bg') if outer_frame.master else canvas.master.cget('bg')
            outer_frame.config(bg=par_bg)
            canvas.config(bg=par_bg)
            if lbl_widget:
                lbl_widget.config(bg=par_bg, fg=_lbl_fg())
            canvas.delete("all")
            draw_fn(canvas, _ink())

    # ─── Other features ───────────────────────────────────────────────────────
    def toggle_word_wrap():
        nonlocal word_wrap
        word_wrap = not word_wrap
        text_area.config(wrap="word" if word_wrap else "none")

    def insert_datetime():
        text_area.insert(tk.INSERT, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def show_stats():
        content = text_area.get(1.0, tk.END)
        words   = len(content.split())
        chars   = len(content.replace('\n',''))
        lines   = content.count('\n')
        sw = tk.Toplevel(root); sw.title("📊 Document Statistics")
        sw.geometry("400x320"); sw.configure(bg='#f5f5f5')
        sw.transient(root); sw.grab_set()
        sw.update_idletasks()
        sw.geometry(f"+{root.winfo_x()+(root.winfo_width()-400)//2}+{root.winfo_y()+(root.winfo_height()-320)//2}")
        sf = tk.Frame(sw, bg='white', relief='flat', bd=1)
        sf.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(sf, text="📄 DOCUMENT STATISTICS", font=("Segoe UI", 14, "bold"),
                 bg='white', fg='#2c3e50').pack(pady=(20,10))
        tk.Frame(sf, height=2, bg='#4CAF50').pack(fill="x", padx=30, pady=5)
        tk.Label(sf, text=f"\n  📝 Lines:       {lines}\n  🔤 Words:       {words}\n  🔡 Characters:  {chars}\n",
                 font=("Consolas", 11), justify="left", bg='white', fg='#555').pack(pady=10)
        tk.Button(sw, text="✓ OK", command=sw.destroy,
                  bg="#4CAF50", fg="white", padx=30, pady=5,
                  cursor='hand2', font=("Segoe UI", 10, "bold"), relief='flat').pack(pady=10)

    def convert_case(case_type):
        try:
            sel = text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            text_area.insert(tk.INSERT, {"upper": sel.upper,
                                          "lower": sel.lower,
                                          "title": sel.title}[case_type]())
        except: pass

    def search_replace():
        def replace_all():
            s, r = se.get(), re_.get()
            if s:
                c = text_area.get(1.0, tk.END)
                n = c.count(s)
                if n:
                    text_area.delete(1.0, tk.END)
                    text_area.insert(1.0, c.replace(s, r))
                    CustomDialog.show_success(root, f"Replaced {n} occurrence{'s' if n!=1 else ''}")
                    rw.destroy()
                else:
                    CustomDialog.show_warning(root, "Not Found", f"'{s}' not found")
        rw = tk.Toplevel(root); rw.title("🔄 Search & Replace")
        rw.geometry("450x200"); rw.configure(bg='#f5f5f5')
        rw.transient(root); rw.grab_set(); rw.resizable(False, False)
        tk.Label(rw, text="Find:",    font=("Segoe UI",10,"bold"), bg='#f5f5f5').grid(row=0,column=0,padx=15,pady=15,sticky='w')
        se = tk.Entry(rw, width=35, font=("Segoe UI",10)); se.grid(row=0,column=1,padx=5,pady=15)
        tk.Label(rw, text="Replace:", font=("Segoe UI",10,"bold"), bg='#f5f5f5').grid(row=1,column=0,padx=15,pady=10,sticky='w')
        re_ = tk.Entry(rw, width=35, font=("Segoe UI",10)); re_.grid(row=1,column=1,padx=5,pady=10)
        bf = tk.Frame(rw, bg='#f5f5f5'); bf.grid(row=2,column=0,columnspan=2,pady=15)
        tk.Button(bf, text="🔄 Replace All", command=replace_all,
                  bg="#FF9800", fg="white", padx=25, pady=5,
                  cursor='hand2', font=("Segoe UI",10,"bold"), relief='flat').pack()

    def remove_extra_spaces():
        c = text_area.get(1.0, tk.END)
        text_area.delete(1.0, tk.END)
        text_area.insert(1.0, re.sub(' +', ' ', c))

    def toggle_line_numbers():
        nonlocal show_line_numbers, line_number_bar
        show_line_numbers = not show_line_numbers
        if show_line_numbers:
            line_number_bar = tk.Text(text_frame, width=6, padx=5, takefocus=0,
                                      border=0, background="#e0e0e0", state="disabled",
                                      wrap="none", font=(current_font_family, current_font_size))
            line_number_bar.pack(side="left", fill="y")
            _upd_ln()
            text_area.bind("<KeyRelease>",  _upd_ln)
            text_area.bind("<MouseWheel>",  _upd_ln)
        else:
            if line_number_bar:
                line_number_bar.destroy(); line_number_bar = None

    def _upd_ln(event=None):
        if line_number_bar:
            lines = int(text_area.index('end-1c').split('.')[0])
            line_number_bar.config(state="normal",
                                   font=(current_font_family, current_font_size))
            line_number_bar.delete(1.0, tk.END)
            line_number_bar.insert(1.0, '\n'.join(str(i) for i in range(1, lines+1)))
            line_number_bar.config(state="disabled")

    # ─── File ops ─────────────────────────────────────────────────────────────
    def new_file():
        nonlocal current_file
        if CustomDialog.show_question(root, "New File", "Create new file? Unsaved changes will be lost!"):
            text_area.delete(1.0, tk.END); current_file = None
            root.title("SM-Notepad Pro - New File")
            file_status.config(text="No file opened"); update_status()

    def open_file():
        nonlocal current_file
        f = filedialog.askopenfilename(filetypes=[("Text Files","*.txt"),("All Files","*.*")])
        if f:
            try:
                with open(f, encoding="utf-8") as fh:
                    text_area.delete(1.0, tk.END); text_area.insert(tk.END, fh.read())
                current_file = f
                root.title(f"SM-Notepad Pro - {os.path.basename(f)}")
                file_status.config(text=f"📄 {os.path.basename(f)}"); update_status()
            except Exception as ex:
                CustomDialog.show_error(root, "Error", str(ex))

    def save_file():
        nonlocal current_file
        if current_file:
            try:
                with open(current_file, "w", encoding="utf-8") as fh:
                    fh.write(text_area.get(1.0, tk.END))
            except Exception as ex:
                CustomDialog.show_error(root, "Error", str(ex))
        else:
            save_as()

    def save_as():
        nonlocal current_file
        f = filedialog.asksaveasfilename(defaultextension=".txt",
                filetypes=[("Text Files","*.txt"),("All Files","*.*")])
        if f:
            try:
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(text_area.get(1.0, tk.END))
                current_file = f
                root.title(f"SM-Notepad Pro - {os.path.basename(f)}")
                file_status.config(text=f"📄 {os.path.basename(f)}")
            except Exception as ex:
                CustomDialog.show_error(root, "Error", str(ex))

    def select_all():
        text_area.tag_add(tk.SEL, "1.0", tk.END)
        text_area.mark_set(tk.INSERT, "1.0"); text_area.see(tk.INSERT)

    def clear_all():
        if CustomDialog.show_question(root, "Clear All", "⚠️ Clear all text?\nThis cannot be undone!"):
            text_area.delete(1.0, tk.END); update_status()

    def exit_app():
        if CustomDialog.show_question(root, "Exit", "Exit SM-Notepad Pro?"):
            root.quit()

    # ─── Canvas Icon Drawing System ───────────────────────────────────────────
    IC = 20
    BLUE          = '#1565C0'
    RED_          = '#c0392b'
    GREEN_        = '#27ae60'
    ORANGE_       = '#e67e22'

    def _ink():
        return '#e8e8e8' if current_theme == 'dark' else '#2c3e50'
    def _btn_hover():
        return '#4a6080' if current_theme == 'dark' else '#c8daf5'
    def _btn_press():
        return '#2a4060' if current_theme == 'dark' else '#a8c0e8'
    def _lbl_fg():
        return '#cccccc' if current_theme == 'dark' else '#2c3e50'

    all_icon_btns = []

    def icon_btn(parent, draw_fn, cmd, tooltip="", pad_x=3):
        bg = parent.cget('bg')
        frame = tk.Frame(parent, bg=bg, bd=0, highlightthickness=0)
        frame.pack(side="left", padx=pad_x, pady=4)

        c = tk.Canvas(frame, width=IC, height=IC, bg=bg,
                      bd=0, highlightthickness=0, cursor='hand2')
        c.pack()

        def draw():
            c.delete("all")
            draw_fn(c, _ink())

        def on_enter(_):
            h = _btn_hover()
            frame.config(bg=h); c.config(bg=h)
            draw()
        def on_leave(_):
            bg2 = parent.cget('bg')
            frame.config(bg=bg2); c.config(bg=bg2)
            draw()
        def on_press(_):
            p = _btn_press()
            frame.config(bg=p); c.config(bg=p)
        def on_release(_):
            on_enter(None); cmd()

        c.bind("<Enter>",          on_enter)
        c.bind("<Leave>",          on_leave)
        c.bind("<ButtonPress-1>",   on_press)
        c.bind("<ButtonRelease-1>", on_release)
        frame.bind("<Enter>",      on_enter)
        frame.bind("<Leave>",      on_leave)

        # ── Tooltip: auto-dismisses after 1 second ────────────────────────────
        tip_win   = [None]
        tip_after = [None]

        def show_tip(_):
            if not tooltip: return
            hide_tip(None)  # cancel any existing tip first
            tip_win[0] = tk.Toplevel(root)
            tip_win[0].wm_overrideredirect(True)
            tip_win[0].wm_geometry(f"+{c.winfo_rootx()+5}+{c.winfo_rooty()+25}")
            tk.Label(tip_win[0], text=tooltip, bg="#ffffe0", relief='solid',
                     bd=1, font=("Segoe UI", 8), padx=4).pack()
            tip_after[0] = root.after(1000, lambda: hide_tip(None))

        def hide_tip(_):
            if tip_after[0]:
                root.after_cancel(tip_after[0])
                tip_after[0] = None
            if tip_win[0]:
                tip_win[0].destroy()
                tip_win[0] = None

        c.bind("<Enter>", lambda e: (on_enter(e), show_tip(e)), add="+")
        c.bind("<Leave>", lambda e: (on_leave(e), hide_tip(e)), add="+")

        draw()
        all_icon_btns.append((c, frame, None, draw_fn))
        return c, frame

    def labeled_icon_btn(parent, draw_fn, cmd, label, tooltip=""):
        bg = parent.cget('bg')
        outer = tk.Frame(parent, bg=bg, bd=0, highlightthickness=0, cursor='hand2')
        outer.pack(side="left", padx=2, pady=2)

        c = tk.Canvas(outer, width=IC, height=IC, bg=bg,
                      bd=0, highlightthickness=0, cursor='hand2')
        c.pack()
        lbl = tk.Label(outer, text=label, bg=bg, fg=_lbl_fg(),
                       font=("Segoe UI", 7), cursor='hand2')
        lbl.pack()

        def draw():
            c.delete("all")
            draw_fn(c, _ink())

        def on_enter(_):
            h = _btn_hover()
            outer.config(bg=h); c.config(bg=h); lbl.config(bg=h)
            draw()
        def on_leave(_):
            bg2 = parent.cget('bg')
            outer.config(bg=bg2); c.config(bg=bg2)
            lbl.config(bg=bg2, fg=_lbl_fg())
            draw()
        def on_press(_):
            p = _btn_press()
            outer.config(bg=p); c.config(bg=p); lbl.config(bg=p)
        def on_release(_):
            on_enter(None); cmd()

        for w in (c, lbl, outer):
            w.bind("<Enter>",          on_enter)
            w.bind("<Leave>",          on_leave)
            w.bind("<ButtonPress-1>",   on_press)
            w.bind("<ButtonRelease-1>", on_release)

        # ── Tooltip: auto-dismisses after 1 second ────────────────────────────
        tip_win   = [None]
        tip_after = [None]

        def show_tip(_):
            if not tooltip: return
            hide_tip(None)  # cancel any existing tip first
            tip_win[0] = tk.Toplevel(root)
            tip_win[0].wm_overrideredirect(True)
            tip_win[0].wm_geometry(f"+{c.winfo_rootx()+5}+{c.winfo_rooty()+25}")
            tk.Label(tip_win[0], text=tooltip, bg="#ffffe0", relief='solid',
                     bd=1, font=("Segoe UI", 8), padx=4).pack()
            tip_after[0] = root.after(1000, lambda: hide_tip(None))

        def hide_tip(_):
            if tip_after[0]:
                root.after_cancel(tip_after[0])
                tip_after[0] = None
            if tip_win[0]:
                tip_win[0].destroy()
                tip_win[0] = None

        for w in (c, lbl, outer):
            w.bind("<Enter>", lambda e: show_tip(e), add="+")
            w.bind("<Leave>", lambda e: hide_tip(e), add="+")

        draw()
        all_icon_btns.append((c, outer, lbl, draw_fn))
        return c, outer

    def sep(parent):
        tk.Frame(parent, width=1, bg='#b0b0b0').pack(side="left", fill="y", pady=5, padx=4)

    # ── Icon draw functions ────────────────────────────────────────────────────
    def ic_new(c, col):
        page_fill = '#3a3a3a' if current_theme == 'dark' else 'white'
        c.create_polygon(3,1,14,1,18,5,18,19,3,19, outline=col, fill=page_fill, width=1.5)
        c.create_line(14,1,14,6,18,6, fill=col, width=1.5)

    def ic_open(c, col):
        f1 = '#5a4a2a' if current_theme == 'dark' else '#e8d5a0'
        f2 = '#8a6a20' if current_theme == 'dark' else '#e8c060'
        c.create_rectangle(2,7,18,17, outline=col, fill=f1, width=1.5)
        c.create_polygon(2,7,6,7,8,4,14,4,16,7,18,7,18,5,14,5,12,2,6,2,4,5,2,5,
                         outline=col, fill=f2, width=1.5)

    def ic_save(c, col):
        f1 = '#2a5a8a' if current_theme == 'dark' else '#5b9bd5'
        f2 = '#406080' if current_theme == 'dark' else '#d0e8ff'
        f3 = '#3a3a3a' if current_theme == 'dark' else 'white'
        c.create_rectangle(2,2,18,18, outline=col, fill=f1, width=1.5)
        c.create_rectangle(5,2,15,8,  outline=col, fill=f2, width=1)
        c.create_rectangle(5,11,15,17,outline=col, fill=f3, width=1)
        c.create_line(12,2,12,8, fill=col, width=1)

    def ic_saveas(c, col):
        f1 = '#2a5a8a' if current_theme == 'dark' else '#5b9bd5'
        f2 = '#406080' if current_theme == 'dark' else '#d0e8ff'
        f3 = '#3a3a3a' if current_theme == 'dark' else 'white'
        c.create_rectangle(2,2,15,17, outline=col, fill=f1, width=1.5)
        c.create_rectangle(4,2,12,7,  outline=col, fill=f2, width=1)
        c.create_rectangle(4,10,12,15,outline=col, fill=f3, width=1)
        c.create_line(16,11,20,11, fill=GREEN_, width=2)
        c.create_line(18,9,18,13,  fill=GREEN_, width=2)

    def ic_undo(c, col):
        c.create_arc(3,4,16,15, start=30, extent=210, outline=col, style='arc', width=2)
        c.create_polygon(3,9,3,14,8,12, fill=col, outline=col)

    def ic_redo(c, col):
        c.create_arc(4,4,17,15, start=-60, extent=-210, outline=col, style='arc', width=2)
        c.create_polygon(17,9,17,14,12,12, fill=col, outline=col)

    def ic_print(c, col):
        printer = '#666' if current_theme == 'dark' else '#aaa'
        paper   = '#3a3a3a' if current_theme == 'dark' else 'white'
        c.create_rectangle(4,7,16,15, outline=col, fill=printer, width=1.5)
        c.create_rectangle(6,2,14,8,  outline=col, fill=paper,   width=1)
        c.create_rectangle(6,12,14,19,outline=col, fill=paper,   width=1)
        c.create_line(8,15,12,15, fill=col, width=1)
        c.create_line(8,17,12,17, fill=col, width=1)

    def ic_lines(c, col):
        gutter = '#4a4a4a' if current_theme == 'dark' else '#ddd'
        c.create_rectangle(2,2,7,18, outline=col, fill=gutter, width=1)
        for y in (5,8,11,14,17):
            c.create_line(9,y,18,y, fill=col, width=1.5)
        c.create_text(4,10, text="1\n2\n3", font=("Segoe UI",4), fill=col, anchor='center')

    def ic_about(c, col):
        c.create_oval(2,2,18,18, outline=BLUE, fill='#e3f0ff', width=2)
        c.create_text(10,10, text="i", font=("Georgia",11,"bold"), fill=col)

    def ic_theme(c, col):
        c.create_oval(3,3,17,17, outline=col, fill='white', width=1.5)
        c.create_arc(3,3,17,17, start=90, extent=180, fill=col, outline=col, width=1)

    def ic_h1(c, col):
        c.create_text(10,10, text="H1", font=("Georgia",11,"bold"), fill=col, anchor='center')

    def ic_h2(c, col):
        c.create_text(10,10, text="H2", font=("Georgia",10,"bold"), fill='#1565a0', anchor='center')

    def ic_h3(c, col):
        c.create_text(10,10, text="H3", font=("Georgia",9,"bold"), fill='#1a6080', anchor='center')

    def ic_bold(c, col):
        c.create_text(10,10, text="B", font=("Georgia",13,"bold"), fill=col, anchor='center')

    def ic_italic(c, col):
        c.create_text(10,10, text="I", font=("Georgia",13,"italic"), fill=col, anchor='center')

    def ic_underline(c, col):
        c.create_text(10,8, text="U", font=("Georgia",12,"bold"), fill=col, anchor='center')
        c.create_line(4,17,16,17, fill=col, width=2)

    def ic_color(c, col):
        c.create_text(10,8, text="A", font=("Georgia",11,"bold"), fill=col, anchor='center')
        c.create_rectangle(3,14,17,18, fill=text_color, outline='#888', width=1)

    def ic_highlight(c, col):
        c.create_polygon(10,2,17,12,13,12,13,18,7,18,7,12,3,12,
                         fill=highlight_color, outline='#888', width=1)

    def ic_align_left(c, col):
        for y, w in ((5,16),(9,11),(13,16),(17,11)):
            c.create_line(2,y,2+w,y, fill=col, width=2)

    def ic_align_center(c, col):
        for y, w in ((5,16),(9,10),(13,16),(17,10)):
            x = (20-w)//2
            c.create_line(x,y,x+w,y, fill=col, width=2)

    def ic_align_right(c, col):
        for y, w in ((5,16),(9,11),(13,16),(17,11)):
            c.create_line(20-w,y,18,y, fill=col, width=2)

    def ic_find(c, col):
        c.create_oval(3,3,13,13, outline=col, width=2)
        c.create_line(11,11,17,17, fill=col, width=2.5)

    def ic_stats(c, col):
        for x,h in ((3,14),(7,9),(11,17),(15,6)):
            c.create_rectangle(x,20-h,x+3,18, fill=col, outline=col)

    def ic_date(c, col):
        c.create_rectangle(2,4,18,18, outline=col, fill='white', width=1.5)
        c.create_line(2,8,18,8, fill=col, width=1)
        c.create_line(6,2,6,6,  fill=col, width=2)
        c.create_line(14,2,14,6,fill=col, width=2)
        c.create_text(10,13, text="31", font=("Segoe UI",7,"bold"), fill=col, anchor='center')

    def ic_clean(c, col):
        c.create_line(4,16,14,6, fill=col, width=2)
        c.create_polygon(14,6,18,2,16,8,12,10, fill=col, outline=col)
        c.create_line(2,18,5,15, fill=col, width=2)
        c.create_text(16,16, text="*", font=("Segoe UI",8,"bold"), fill=col, anchor='center')

    def ic_darklight(c, col):
        c.create_arc(2,2,18,18, start=90, extent=180, fill='#333', outline='#333')
        c.create_arc(2,2,18,18, start=270,extent=180, fill='#f5c518', outline='#f5c518')
        c.create_oval(2,2,18,18, outline=col, width=1.5)

    # ─── Build Toolbar (row 1) ────────────────────────────────────────────────
    labeled_icon_btn(toolbar, ic_new,    new_file,                "New (Ctrl+N)",   "New")
    labeled_icon_btn(toolbar, ic_open,   open_file,               "Open (Ctrl+O)",  "Open")
    labeled_icon_btn(toolbar, ic_save,   save_file,               "Save (Ctrl+S)",  "Save")
    labeled_icon_btn(toolbar, ic_saveas, save_as,                 "Save As",        "Save As")
    sep(toolbar)
    labeled_icon_btn(toolbar, ic_undo,   lambda: text_area.edit_undo(), "Undo",     "Undo")
    labeled_icon_btn(toolbar, ic_redo,   lambda: text_area.edit_redo(), "Redo",     "Redo")
    sep(toolbar)
    labeled_icon_btn(toolbar, ic_print,  lambda: print_preview(), "Print Preview",  "Print")
    sep(toolbar)
    labeled_icon_btn(toolbar, ic_lines,  toggle_line_numbers,     "Line Numbers",   "Lines")
    sep(toolbar)
    labeled_icon_btn(toolbar, ic_about,  lambda: about(),         "About",          "About")
    _theme_c, _theme_f = labeled_icon_btn(toolbar, ic_theme, toggle_theme, "Toggle Theme", "Theme")
    theme_btn = _theme_c

    # ─── Build Format Toolbar (row 2) ─────────────────────────────────────────
    def fsep():
        tk.Frame(fmt_toolbar, width=1, bg='#b0b0b0').pack(side="left", fill="y", pady=4, padx=3)

    labeled_icon_btn(fmt_toolbar, ic_h1,          lambda: set_heading(24,"H1"), "Heading 1", "H1")
    labeled_icon_btn(fmt_toolbar, ic_h2,          lambda: set_heading(18,"H2"), "Heading 2", "H2")
    labeled_icon_btn(fmt_toolbar, ic_h3,          lambda: set_heading(14,"H3"), "Heading 3", "H3")
    fsep()
    labeled_icon_btn(fmt_toolbar, ic_bold,        toggle_bold,      "Bold (Ctrl+B)",      "Bold")
    labeled_icon_btn(fmt_toolbar, ic_italic,      toggle_italic,    "Italic (Ctrl+I)",    "Italic")
    labeled_icon_btn(fmt_toolbar, ic_underline,   toggle_underline, "Underline (Ctrl+U)", "Underline")
    fsep()
    color_c, _ = labeled_icon_btn(fmt_toolbar, ic_color,     apply_text_color,      "Text Color",      "Color")
    color_btn = color_c
    fsep()
    hi_c, _    = labeled_icon_btn(fmt_toolbar, ic_highlight, apply_highlight_color, "Highlight Color", "Highlight")
    hi_btn = hi_c
    fsep()
    labeled_icon_btn(fmt_toolbar, ic_align_left,   lambda: set_align("left"),   "Align Left",   "Left")
    labeled_icon_btn(fmt_toolbar, ic_align_center, lambda: set_align("center"), "Align Center", "Center")
    labeled_icon_btn(fmt_toolbar, ic_align_right,  lambda: set_align("right"),  "Align Right",  "Right")
    fsep()
    labeled_icon_btn(fmt_toolbar, ic_find,      toggle_search_bar,     "Find (Ctrl+F)", "Find")
    fsep()
    labeled_icon_btn(fmt_toolbar, ic_stats,     show_stats,            "Statistics",    "Stats")
    fsep()
    labeled_icon_btn(fmt_toolbar, ic_date,      insert_datetime,       "Insert Date",   "Date")
    fsep()
    labeled_icon_btn(fmt_toolbar, ic_clean,     remove_extra_spaces,   "Clean Spaces",  "Clean")
    fsep()
    labeled_icon_btn(fmt_toolbar, ic_darklight, toggle_theme,          "Dark/Light",    "Dark/Light")

    # ─── Print preview ────────────────────────────────────────────────────────
    def print_preview():
        content = text_area.get(1.0, tk.END)
        if not content.strip():
            CustomDialog.show_warning(root, "Empty", "Nothing to print.")
            return
        pw = tk.Toplevel(root); pw.title("🖨️ Print Preview")
        pw.geometry("600x550"); pw.configure(bg='#f5f5f5')
        tk.Label(pw, text="📄 PRINT PREVIEW", font=("Segoe UI",12,"bold"),
                 bg='#f5f5f5', fg='#2c3e50').pack(pady=10)
        td = tk.Text(pw, wrap="word", font=(current_font_family, 10), relief='solid', bd=1)
        td.pack(expand=True, fill="both", padx=20, pady=10)
        td.insert(1.0, content); td.config(state="disabled")
        tk.Button(pw, text="✓ Close", command=pw.destroy,
                  bg="#2196F3", fg="white", padx=30, pady=5,
                  cursor='hand2', font=("Segoe UI",10,"bold"), relief='flat').pack(pady=15)

    # ─── About ────────────────────────────────────────────────────────────────
    def about():
        aw = tk.Toplevel(root); aw.title("ℹ️ About SM-Notepad Pro")
        aw.geometry("500x450"); aw.configure(bg='#f5f5f5')
        aw.transient(root); aw.grab_set(); aw.resizable(False, False)
        aw.update_idletasks()
        aw.geometry(f"+{root.winfo_x()+(root.winfo_width()-500)//2}+{root.winfo_y()+(root.winfo_height()-450)//2}")
        mf = tk.Frame(aw, bg='white', relief='flat', bd=2)
        mf.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(mf, text="📝 SM-Notepad Pro", font=("Segoe UI",18,"bold"),
                 bg='white', fg='#2c3e50').pack(pady=(30,5))
        tk.Label(mf, text="Version 3.0", font=("Segoe UI",10), bg='white', fg='#7f8c8d').pack()
        tk.Frame(mf, height=2, bg='#4CAF50').pack(fill="x", padx=40, pady=15)
        features = (
            "\n  ✨ Rich Text Formatting (Bold, Italic, Underline)\n"
            "  🔤 Headings H1 / H2 / H3\n"
            "  🎨 Text Color & Highlight Color\n"
            "  ≡ ≣ ▭ Paragraph Alignment\n"
            "  🔍 Live Search with match counter\n"
            "  📊 Document Statistics\n"
            "  📅 Insert Date/Time\n"
            "  ✨ Remove Extra Spaces\n"
            "  🌓 Dark / Light Theme\n"
            "  💾 Open / Save / Save As\n"
        )
        tk.Label(mf, text=features, font=("Segoe UI",10), justify="left",
                 bg='white', fg='#555').pack(pady=5)
        tk.Frame(mf, height=1, bg='#e0e0e0').pack(fill="x", padx=40, pady=5)
        tk.Label(mf, text="🐍 Created with Python & Tkinter",
                 font=("Segoe UI",9), bg='white', fg='#95a5a6').pack(pady=5)
        tk.Button(mf, text="✓ OK", command=aw.destroy,
                  bg="#4CAF50", fg="white", padx=30, pady=5,
                  cursor='hand2', font=("Segoe UI",10,"bold"), relief='flat').pack(pady=(5,20))

    # ─── Menu bar ─────────────────────────────────────────────────────────────
    menu = tk.Menu(root); root.config(menu=menu)

    fm = tk.Menu(menu, tearoff=0); menu.add_cascade(label="File", menu=fm)
    fm.add_command(label="📄 New",         command=new_file,     accelerator="Ctrl+N")
    fm.add_command(label="📂 Open",        command=open_file,    accelerator="Ctrl+O")
    fm.add_command(label="💾 Save",        command=save_file,    accelerator="Ctrl+S")
    fm.add_command(label="💿 Save As",     command=save_as,      accelerator="Ctrl+Shift+S")
    fm.add_separator()
    fm.add_command(label="🖨️ Print Preview",command=print_preview)
    fm.add_separator()
    fm.add_command(label="🚪 Exit",        command=exit_app)

    em = tk.Menu(menu, tearoff=0); menu.add_cascade(label="Edit", menu=em)
    em.add_command(label="🔍 Find",        command=toggle_search_bar, accelerator="Ctrl+F")
    em.add_command(label="🔄 Replace",     command=search_replace,    accelerator="Ctrl+H")
    em.add_separator()
    em.add_command(label="✨ Select All",  command=select_all,        accelerator="Ctrl+A")
    em.add_command(label="🗑️ Clear All",   command=clear_all)
    em.add_separator()
    em.add_command(label="📅 Date/Time",   command=insert_datetime,   accelerator="Ctrl+T")

    frm = tk.Menu(menu, tearoff=0); menu.add_cascade(label="Format", menu=frm)
    frm.add_command(label="H1 Heading",    command=lambda: set_heading(24,"H1"))
    frm.add_command(label="H2 Heading",    command=lambda: set_heading(18,"H2"))
    frm.add_command(label="H3 Heading",    command=lambda: set_heading(14,"H3"))
    frm.add_separator()
    frm.add_command(label="Bold",          command=toggle_bold,        accelerator="Ctrl+B")
    frm.add_command(label="Italic",        command=toggle_italic,      accelerator="Ctrl+I")
    frm.add_command(label="Underline",     command=toggle_underline,   accelerator="Ctrl+U")
    frm.add_separator()
    frm.add_command(label="🎨 Text Color", command=apply_text_color)
    frm.add_command(label="⊕ Highlight",   command=apply_highlight_color)
    frm.add_separator()
    frm.add_command(label="🔤 Change Font",command=change_font_family)
    frm.add_command(label="🔍 Zoom In",    command=zoom_in,  accelerator="Ctrl++")
    frm.add_command(label="🔍 Zoom Out",   command=zoom_out, accelerator="Ctrl+-")
    frm.add_separator()
    frm.add_command(label="🔠 UPPERCASE",  command=lambda: convert_case("upper"))
    frm.add_command(label="🔡 lowercase",  command=lambda: convert_case("lower"))
    frm.add_command(label="📝 Title Case", command=lambda: convert_case("title"))
    frm.add_separator()
    frm.add_command(label="✨ Remove Extra Spaces", command=remove_extra_spaces)

    vm = tk.Menu(menu, tearoff=0); menu.add_cascade(label="View", menu=vm)
    vm.add_command(label="🌓 Dark/Light",  command=toggle_theme,       accelerator="Ctrl+D")
    vm.add_command(label="📏 Word Wrap",   command=toggle_word_wrap,   accelerator="Ctrl+W")
    vm.add_command(label="#️⃣ Line Numbers",command=toggle_line_numbers)
    vm.add_command(label="📊 Statistics",  command=show_stats,         accelerator="Ctrl+I")

    hm = tk.Menu(menu, tearoff=0); menu.add_cascade(label="Help", menu=hm)
    hm.add_command(label="ℹ️ About", command=about)

    # ─── Keyboard shortcuts ───────────────────────────────────────────────────
    root.bind("<Control-n>",       lambda e: new_file())
    root.bind("<Control-o>",       lambda e: open_file())
    root.bind("<Control-s>",       lambda e: save_file())
    root.bind("<Control-Shift-S>", lambda e: save_as())
    root.bind("<Control-f>",       lambda e: toggle_search_bar())
    root.bind("<Control-h>",       lambda e: search_replace())
    root.bind("<Control-a>",       lambda e: select_all())
    root.bind("<Control-t>",       lambda e: insert_datetime())
    root.bind("<Control-plus>",    lambda e: zoom_in())
    root.bind("<Control-equal>",   lambda e: zoom_in())
    root.bind("<Control-minus>",   lambda e: zoom_out())
    root.bind("<Control-d>",       lambda e: toggle_theme())
    root.bind("<Control-w>",       lambda e: toggle_word_wrap())
    root.bind("<Control-b>",       lambda e: toggle_bold())
    root.bind("<Control-i>",       lambda e: toggle_italic())
    root.bind("<Control-u>",       lambda e: toggle_underline())
    root.bind("<Escape>",          lambda e: (clear_highlights(),
                                              search_bar.pack_forget()) if search_bar_visible[0] else None)

    text_area.bind("<KeyRelease>",    update_status)
    text_area.bind("<ButtonRelease-1>", update_status)

    update_status()
    root.mainloop()

if __name__ == "__main__":
    run()
