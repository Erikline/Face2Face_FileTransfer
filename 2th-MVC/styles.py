# styles.py

# (这里是你之前定义的 COLORS, FONTS, LAYOUT, BUTTON_STYLE, LABEL_STYLE, FRAME_STYLE 字典)
# 例如:
COLORS = {
    "primary": "#4a6fa5", "primary_dark": "#3d5d8a", "secondary": "#6b8cae",
    "accent": "#47b8e0", "accent_light": "#7dcff0", "background": "#f5f7fa",
    "text": "#333333", "text_light": "#666666", "success": "#5cb85c",
    "success_dark": "#4cae4c", "warning": "#f0ad4e", "warning_dark": "#eea236",
    "error": "#d9534f", "error_dark": "#c9302c", "light_gray": "#e9ecef",
    "medium_gray": "#d1d7e0", "white": "#ffffff", "shadow": "#222222"
}
FONTS = {
    "title": ("Helvetica", 18, "bold"), "subtitle": ("Helvetica", 14, "bold"),
    "body": ("Helvetica", 12), "body_bold": ("Helvetica", 12, "bold"),
    "small": ("Helvetica", 10), "small_bold": ("Helvetica", 10, "bold"),
    "button": ("Helvetica", 12, "bold"), "url": ("Helvetica", 12, "underline")
}
LAYOUT = {
    "padding": 20, "small_padding": 10, "button_width": 15, "button_height": 2,
    "border_radius": 5, "spacing": 10, "small_spacing": 5, "border_width": 1,
    "hover_thickness": 2, "content_width": 600, "icon_size": 16
}
BUTTON_STYLE = {
    "primary": {"bg": COLORS["primary"], "fg": COLORS["text"], "activebackground": COLORS["primary_dark"], "activeforeground": COLORS["text"], "relief": "flat", "borderwidth": 0, "padx": 15, "pady": 8, "cursor": "hand2", "font": FONTS["button"]},
    "secondary": {"bg": COLORS["light_gray"], "fg": COLORS["text"], "activebackground": COLORS["medium_gray"], "activeforeground": COLORS["text"], "relief": "flat", "borderwidth": 0, "padx": 15, "pady": 8, "cursor": "hand2", "font": FONTS["button"]},
    "accent": {"bg": COLORS["accent"], "fg": COLORS["white"], "activebackground": COLORS["accent_light"], "activeforeground": COLORS["white"], "relief": "flat", "borderwidth": 0, "padx": 15, "pady": 8, "cursor": "hand2", "font": FONTS["button"]},
    "danger": {"bg": COLORS["error"], "fg": COLORS["white"], "activebackground": COLORS["error_dark"], "activeforeground": COLORS["white"], "relief": "flat", "borderwidth": 0, "padx": 15, "pady": 8, "cursor": "hand2", "font": FONTS["button"]},
    "text_button": {"bg": COLORS["background"], "fg": COLORS["primary"], "activebackground": COLORS["background"], "activeforeground": COLORS["primary_dark"], "relief": "flat", "borderwidth": 0, "padx": 5, "pady": 2, "cursor": "hand2", "font": FONTS["body_bold"]}
}
LABEL_STYLE = {
    "title": {"font": FONTS["title"], "fg": COLORS["text"], "bg": COLORS["background"], "pady": 10, "anchor": "center"},
    "subtitle": {"font": FONTS["subtitle"], "fg": COLORS["text_light"], "bg": COLORS["background"], "pady": 8, "anchor": "center"},
    "info": {"font": FONTS["body"], "fg": COLORS["text"], "bg": COLORS["white"], "pady": 5, "anchor": "w"},
    "url_entry": {"font": FONTS["body"], "fg": COLORS["primary"], "readonlybackground": COLORS["white"], "relief":"solid", "borderwidth":1, "highlightthickness":1, "highlightcolor":COLORS["light_gray"], "highlightbackground":COLORS["light_gray"], "state":"readonly"},
    "status": {"font": FONTS["body_bold"], "fg": COLORS["text_light"], "bg": COLORS["white"], "pady": 5, "anchor": "w"},
    "listbox": {"font": FONTS["body"], "fg": COLORS["text"], "bg": COLORS["white"], "selectbackground": COLORS["accent"], "selectforeground": COLORS["white"], "activestyle": "none", "relief": "flat", "borderwidth": 0, "highlightthickness": 0},
    "hint": {"font": FONTS["small"], "fg": COLORS["text_light"], "bg": COLORS["background"], "pady": 2, "anchor": "center"}
}
FRAME_STYLE = {
    "main": {"bg": COLORS["background"], "padx": LAYOUT["padding"], "pady": LAYOUT["padding"]},
    "content_card": {"bg": COLORS["white"], "padx": LAYOUT["padding"], "pady": LAYOUT["padding"], "relief": "solid", "borderwidth": 0, "highlightbackground": COLORS["light_gray"], "highlightthickness": 1},
    "section": {"bg": COLORS["white"], "padx": 0, "pady": 0},
    "file_list_container": {"bg": COLORS["light_gray"], "relief": "sunken", "borderwidth": 1, "highlightbackground": COLORS["medium_gray"], "highlightthickness": 0},
    "footer_bar": {"bg": COLORS["background"], "pady": LAYOUT["small_padding"]}
}