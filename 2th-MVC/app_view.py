# app_view.py
from tkinter import (Tk, Frame, Label, Button, Listbox, Scrollbar, Entry, messagebox,
                     END, VERTICAL, BOTH, X, Y, LEFT, RIGHT, BOTTOM, NORMAL, DISABLED, TclError)
from tkinter.filedialog import askopenfilenames, asksaveasfilename
import tkinter.font as tkFont

# 导入样式和配置常量
from styles import COLORS, FONTS, LAYOUT, BUTTON_STYLE, LABEL_STYLE, FRAME_STYLE
from config import FILE_SOURCE_GUI, FILE_SOURCE_BROWSER

class ModernButton(Button):
    def __init__(self, master=None, cnf={}, **kw):
        passed_bg = kw.get("bg", cnf.get("bg"))
        passed_activebg = kw.get("activebackground", cnf.get("activebackground"))
        default_button_style = BUTTON_STYLE.get("primary", {})
        self.original_bg = passed_bg if passed_bg is not None else default_button_style.get("bg", COLORS.get("primary"))
        self.hover_bg = passed_activebg if passed_activebg is not None else default_button_style.get("activebackground", COLORS.get("primary_dark"))
        if 'relief' not in kw and 'relief' not in cnf: kw['relief'] = 'flat'
        if 'borderwidth' not in kw and 'borderwidth' not in cnf: kw['borderwidth'] = 0
        super().__init__(master, cnf, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        if self['state'] == NORMAL: self.config(bg=self.hover_bg)
    def on_leave(self, event):
        if self['state'] == NORMAL: self.config(bg=self.original_bg)
    def config(self, cnf=None, **kw):
        if cnf: kw.update(cnf)
        if 'bg' in kw: self.original_bg = kw['bg']
        if 'activebackground' in kw: self.hover_bg = kw['activebackground']
        super().config(cnf, **kw)
    configure = config

class AppView:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller

        master.configure(bg=COLORS["background"])
        master.title("本地文件分享")
        master.geometry("800x700"); master.minsize(700, 650)

        self.fonts = {}
        for name, definition in FONTS.items():
            font_config = {"family": definition[0], "size": definition[1]}
            if len(definition) > 2:
                for style_attr in definition[2:]:
                    if isinstance(style_attr, str):
                        attr_lower = style_attr.lower()
                        if attr_lower == "bold": font_config["weight"] = "bold"
                        elif attr_lower == "italic": font_config["slant"] = "italic"
                        elif attr_lower == "underline": font_config["underline"] = True
                        elif attr_lower == "overstrike": font_config["overstrike"] = True
            self.fonts[name] = tkFont.Font(**font_config)

        self._setup_ui()
        self.master.protocol("WM_DELETE_WINDOW", self.controller.handle_window_close)

    def _setup_ui(self):
        self.main_frame = Frame(self.master, **FRAME_STYLE["main"]); self.main_frame.pack(fill=BOTH, expand=True)
        
        self.title_label = Label(self.main_frame, text="本地文件分享", font=self.fonts["title"], **{k:v for k,v in LABEL_STYLE["title"].items() if k !='font'})
        self.title_label.pack(pady=(0, LAYOUT["small_spacing"]))
        self.subtitle_label = Label(self.main_frame, text="简单、快速地分享文件到同一网络的设备", font=self.fonts["subtitle"], **{k:v for k,v in LABEL_STYLE["subtitle"].items() if k !='font'})
        self.subtitle_label.pack(pady=(0, LAYOUT["padding"]))

        self.content_card = Frame(self.main_frame, **FRAME_STYLE["content_card"]); self.content_card.pack(fill=BOTH, expand=True)

        self.file_info_section = Frame(self.content_card, **FRAME_STYLE["section"]); self.file_info_section.pack(fill=X, pady=(0, LAYOUT["small_spacing"]))
        Label(self.file_info_section, text="共享文件列表:", bg=COLORS["white"], font=self.fonts["body_bold"], fg=COLORS["text"]).pack(side=LEFT)
        self.file_count_label = Label(self.file_info_section, text="0 个文件", bg=COLORS["white"], font=self.fonts["body"], fg=COLORS["text_light"]); self.file_count_label.pack(side=RIGHT)

        self.list_container = Frame(self.content_card, **FRAME_STYLE["file_list_container"]); self.list_container.pack(fill=BOTH, expand=True, pady=LAYOUT["small_spacing"])
        self.scrollbar = Scrollbar(self.list_container, orient=VERTICAL)
        self.files_listbox = Listbox(self.list_container, yscrollcommand=self.scrollbar.set, height=10, font=self.fonts["body"], exportselection=False, **{k:v for k,v in LABEL_STYLE["listbox"].items() if k != 'font'})
        self.scrollbar.config(command=self.files_listbox.yview); self.scrollbar.pack(side=RIGHT, fill=Y)
        self.files_listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=LAYOUT["small_padding"], pady=LAYOUT["small_padding"])

        self.action_buttons_frame = Frame(self.content_card, **FRAME_STYLE["section"]); self.action_buttons_frame.pack(fill=X, pady=(LAYOUT["small_spacing"], LAYOUT["small_spacing"]))
        
        btn_secondary_style = {k:v for k,v in BUTTON_STYLE["secondary"].items() if k!='font'}
        btn_primary_style = {k:v for k,v in BUTTON_STYLE["primary"].items() if k!='font'}
        btn_danger_small_style = {**{k:v for k,v in BUTTON_STYLE["danger"].items() if k!='font'}, "padx": 10, "pady": 8}

        self.select_files_button = ModernButton(self.action_buttons_frame, text="选择文件", command=self.controller.handle_gui_select_files, font=self.fonts["button"], **btn_secondary_style)
        self.select_files_button.pack(side=LEFT, padx=(0, LAYOUT["small_spacing"]))

        self.save_as_button = ModernButton(self.action_buttons_frame, text="另存选中...", command=self.controller.handle_gui_save_selected_as, font=self.fonts["button"], **btn_secondary_style)
        self.save_as_button.pack(side=LEFT, padx=(0, LAYOUT["small_spacing"]))
        
        self.delete_button = ModernButton(self.action_buttons_frame, text="删除选中", command=self.controller.handle_gui_delete_selected, font=self.fonts["button"], **btn_danger_small_style)
        self.delete_button.pack(side=LEFT, padx=(0, LAYOUT["small_spacing"]))
        
        self.server_toggle_button = ModernButton(self.action_buttons_frame, text="开始分享", command=self.controller.handle_toggle_server, font=self.fonts["button"], **btn_primary_style)
        self.server_toggle_button.pack(side=LEFT)

        self.info_frame = Frame(self.content_card, **FRAME_STYLE["section"]); self.info_frame.pack(fill=X, pady=(LAYOUT["small_spacing"], 0))
        self.status_label = Label(self.info_frame, text="服务器: 未启动", font=self.fonts["body_bold"], **{k:v for k,v in LABEL_STYLE["status"].items() if k!='font'})
        self.status_label.pack(side=LEFT, pady=(0, LAYOUT["small_spacing"]))

        self.url_container = Frame(self.info_frame, **FRAME_STYLE["section"]); self.url_container.pack(side=RIGHT, fill=X, expand=True, pady=(0, LAYOUT["small_spacing"]), padx=(LAYOUT["small_spacing"], 0))
        self.url_display_entry = Entry(self.url_container, font=self.fonts["body"], **{k:v for k,v in LABEL_STYLE["url_entry"].items() if k!='font'})
        self.url_display_entry.pack(side=LEFT, fill=X, expand=True)
        self.url_display_entry.insert(0, "服务器未运行或IP不可用")
        
        copy_btn_style = {k:v for k,v in BUTTON_STYLE["secondary"].items() if k not in ['font', 'padx', 'pady']}
        self.copy_url_button = ModernButton(self.url_container, text="复制", command=self.controller.handle_copy_url, font=self.fonts["small_bold"], padx=10, pady=4, state=DISABLED, **copy_btn_style)
        self.copy_url_button.pack(side=LEFT, padx=(LAYOUT["small_spacing"], 0))

        self.footer_frame = Frame(self.main_frame, **FRAME_STYLE["footer_bar"]); self.footer_frame.pack(fill=X, side=BOTTOM)
        self.footer_label = Label(self.footer_frame, text="确保设备连接到同一WiFi网络。", font=self.fonts["small"], **{k:v for k,v in LABEL_STYLE["hint"].items() if k!='font'}); self.footer_label.pack()
        
        self.update_server_stopped_gui()

    def update_file_list(self, files_data):
        self.files_listbox.delete(0, END)
        if not files_data:
            self.files_listbox.insert(END, "  没有共享文件")
            self.files_listbox.config(fg=COLORS["text_light"])
            self.file_count_label.config(text="0 个文件")
            self.delete_button.config(state=DISABLED)
            self.save_as_button.config(state=DISABLED)
            return

        self.files_listbox.config(fg=COLORS["text"])
        file_count = len(files_data)
        self.file_count_label.config(text=f"{file_count} 个文件")
        self.delete_button.config(state=NORMAL if file_count > 0 else DISABLED)
        self.save_as_button.config(state=NORMAL if file_count > 0 else DISABLED)

        for item in files_data:
            source_tag = ""
            if item['source'] == FILE_SOURCE_GUI: source_tag = "[应用]"
            elif item['source'] == FILE_SOURCE_BROWSER: source_tag = "[网页]"
            listbox_entry = f"  {item['name']} ({item['size_str']}) {source_tag}"
            self.files_listbox.insert(END, listbox_entry)
            
    def get_selected_listbox_index(self):
        selected_indices = self.files_listbox.curselection()
        return selected_indices[0] if selected_indices else None

    def update_status_label(self, text, color_key="text_light"):
        self.status_label.config(text=text, fg=COLORS[color_key])

    def update_url_display(self, url_text, is_running=False):
        self.url_display_entry.config(state=NORMAL)
        self.url_display_entry.delete(0, END)
        self.url_display_entry.insert(0, url_text)
        self.url_display_entry.config(state="readonly", fg=COLORS["primary"] if is_running else COLORS["text_light"])
        self.copy_url_button.config(state=NORMAL if is_running else DISABLED)

    def update_server_running_gui(self, url):
        self.update_status_label("服务器: 运行中", "success")
        self.server_toggle_button.config(text="停止分享", **{k:v for k,v in BUTTON_STYLE["danger"].items() if k!='font'})
        self.server_toggle_button.config(state=NORMAL)
        self.update_url_display(url, is_running=True)
    
    def update_server_stopped_gui(self):
        self.update_status_label("服务器: 已停止")
        self.server_toggle_button.config(text="开始分享", **{k:v for k,v in BUTTON_STYLE["primary"].items() if k!='font'})
        self.server_toggle_button.config(state=NORMAL)
        self.update_url_display("服务器未运行或URL无效", is_running=False)

    def update_server_starting_gui(self):
        self.update_status_label("服务器: 启动中...", "accent")
        self.server_toggle_button.config(text="启动中...", state=DISABLED)
    
    def update_server_stopping_gui(self):
        self.update_status_label("服务器: 停止中...", "accent")
        self.server_toggle_button.config(text="停止中...", state=DISABLED)

    def show_message(self, title, message, type="info"):
        if type == "error": messagebox.showerror(title, message, master=self.master)
        elif type == "warning": messagebox.showwarning(title, message, master=self.master)
        else: messagebox.showinfo(title, message, master=self.master)

    def ask_yes_no(self, title, question):
        return messagebox.askyesno(title, question, master=self.master)

    def ask_for_filenames(self, title, filetypes):
        return askopenfilenames(master=self.master, multiple=True, title=title, filetypes=filetypes)

    def ask_for_save_as_filename(self, initial_file, title, default_ext, filetypes):
        return asksaveasfilename(master=self.master, initialfile=initial_file, title=title, defaultextension=default_ext, filetypes=filetypes)

    def flash_button_visual(self, button_widget, color_key1, color_key2, count=2):
        if not self.master.winfo_exists() or not button_widget.winfo_exists(): return
        
        original_style = BUTTON_STYLE["secondary"]
        if button_widget == self.select_files_button: original_style = BUTTON_STYLE["secondary"]
        elif button_widget == self.server_toggle_button and button_widget.cget('text') == "开始分享":
            original_style = BUTTON_STYLE["primary"]
        
        flash_bg = COLORS.get(color_key1, original_style["bg"])
        original_bg = COLORS.get(color_key2, original_style["bg"])
        
        if count <= 0:
            if button_widget.winfo_exists(): button_widget.config(bg=original_bg)
            return
        try:
            button_widget.config(bg=flash_bg)
            self.master.after(150, lambda: button_widget.config(bg=original_bg) if button_widget.winfo_exists() else None)
            self.master.after(300, lambda: self.flash_button_visual(button_widget, color_key1, color_key2, count - 1) if button_widget.winfo_exists() else None)
        except TclError: pass

    def copy_to_clipboard(self, text_to_copy):
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(text_to_copy)
            
            original_text = self.copy_url_button.cget("text")
            btn_orig_bg = BUTTON_STYLE["secondary"]["bg"] 
            btn_hover_bg = BUTTON_STYLE["secondary"]["activebackground"]
            btn_orig_fg = BUTTON_STYLE["secondary"]["fg"]

            self.copy_url_button.config(text="已复制!", bg=COLORS["success"], activebackground=COLORS["success_dark"], fg=COLORS["white"], activeforeground=COLORS["white"])
            if self.copy_url_button.winfo_exists():
                self.master.after(1500, lambda:
                    self.copy_url_button.config(text=original_text, bg=btn_orig_bg, activebackground=btn_hover_bg, fg=btn_orig_fg, activeforeground=btn_orig_fg)
                    if self.copy_url_button.winfo_exists() else None )
            return True
        except Exception as e:
            print(f"View Error: 剪贴板复制失败: {e}")
            self.show_message("复制失败", f"无法复制到剪贴板: {e}", type="error")
            return False