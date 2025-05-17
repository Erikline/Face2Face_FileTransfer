from http.server import HTTPServer, BaseHTTPRequestHandler
from tkinter import *
from tkinter.filedialog import askopenfilenames, asksaveasfilename # 添加了 asksaveasfilename
from tkinter import messagebox # 用于确认对话框
import time
from threading import Thread
import tkinter.font as tkFont
import os
from urllib.parse import unquote, quote, parse_qs
import socket # 用于获取 IP 地址
import sys # 用于判断 Python 版本
import shutil # 用于剪贴板和文件复制
import mimetypes # 用于更好的 MIME 类型检测
import cgi # 用于解析 multipart/form-data

# --- 开始：配置 ---
UPLOAD_FOLDER = "uploads" # 存储通过浏览器上传的文件的文件夹
# --- 结束：配置 ---

# --- 开始：文件来源常量 ---
FILE_SOURCE_GUI = "gui" # 文件来自Tkinter GUI选择
FILE_SOURCE_BROWSER = "browser" # 文件来自浏览器上传
# --- 结束：文件来源常量 ---

# --- 开始：嵌入式 ip.py 内容 ---
def get_ip_addr():
    s = None
    ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80)) # 连接到外部地址以确定出口IP
        ip = s.getsockname()[0]
    except Exception:
        try:
            # 备用方法：获取主机名对应的IP
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            if ip_address and not ip_address.startswith("127."):
                ip = ip_address
            else:
                 # 尝试获取所有IP地址，并排除环回地址
                 ip_list = socket.gethostbyname_ex(hostname)[2]
                 non_loopback_ips = [i for i in ip_list if not i.startswith("127.")]
                 if non_loopback_ips:
                    ip = non_loopback_ips[0]
        except socket.gaierror:
            print("警告: 无法通过 gethostbyname/gethostbyname_ex 解析主机名。")
        except Exception as e:
             print(f"警告: IP解析回退期间发生意外错误: {e}")
    finally:
        if s:
            s.close()
    print(f"最终获取到的IP地址: {ip}")
    return ip
# --- 结束：嵌入式 ip.py 内容 ---


# --- 开始：嵌入式 styles.py 内容 (使用您提供的第二版颜色主题和样式) ---
# 定义应用程序的颜色主题和样式
COLORS = {
    "primary": "#4a6fa5",      # 主色调 - 蓝色
    "primary_dark": "#3d5d8a", # 主色调深色版 - 用于悬停效果
    "secondary": "#6b8cae",   # 次要色调
    "accent": "#47b8e0",      # 强调色
    "accent_light": "#7dcff0", # 强调色浅色版
    "background": "#f5f7fa",  # 背景色 - 浅灰
    "text": "#333333",        # 文本色 - 深灰 (这是按钮文本的新颜色)
    "text_light": "#666666",  # 浅色文本 - 用于次要信息
    "success": "#5cb85c",     # 成功色 - 绿色
    "success_dark": "#4cae4c", # 成功色深色版
    "warning": "#f0ad4e",     # 警告色 - 黄色
    "warning_dark": "#eea236", # 警告色深色版
    "error": "#d9534f",       # 错误色 - 红色
    "error_dark": "#c9302c",  # 错误色深色版
    "light_gray": "#e9ecef",  # 浅灰色 - 用于边框和分隔线
    "medium_gray": "#d1d7e0", # 中灰色 - 用于悬停效果
    "white": "#ffffff",       # 白色
    "shadow": "#222222"     # 阴影色 (注意：Tkinter 原生不支持真阴影)
}
FONTS = { # 字体定义
    "title": ("Helvetica", 18, "bold"),
    "subtitle": ("Helvetica", 14, "bold"),
    "body": ("Helvetica", 12),
    "body_bold": ("Helvetica", 12, "bold"),
    "small": ("Helvetica", 10),
    "small_bold": ("Helvetica", 10, "bold"),
    "button": ("Helvetica", 12, "bold"),
    "url": ("Helvetica", 12, "underline") # URL输入框字体
}
LAYOUT = { # 布局参数
    "padding": 20, "small_padding": 10, "button_width": 15, "button_height": 2,
    "border_radius": 5, "spacing": 10, "small_spacing": 5, "border_width": 1,
    "hover_thickness": 2, "content_width": 600, "icon_size": 16
}
BUTTON_STYLE = { # 按钮样式
    "primary": {
        "bg": COLORS["primary"], "fg": COLORS["text"], "activebackground": COLORS["primary_dark"],
        "activeforeground": COLORS["text"], "relief": "flat", "borderwidth": 0, "padx": 15, "pady": 8,
        "cursor": "hand2", "font": FONTS["button"]
    },
    "secondary": {
        "bg": COLORS["light_gray"], "fg": COLORS["text"], "activebackground": COLORS["medium_gray"],
        "activeforeground": COLORS["text"], "relief": "flat", "borderwidth": 0, "padx": 15, "pady": 8,
        "cursor": "hand2", "font": FONTS["button"]
    },
    "accent": {
        "bg": COLORS["accent"], "fg": COLORS["white"], "activebackground": COLORS["accent_light"],
        "activeforeground": COLORS["white"], "relief": "flat", "borderwidth": 0, "padx": 15, "pady": 8,
        "cursor": "hand2", "font": FONTS["button"]
    },
    "danger": { # 用于停止按钮和删除按钮
        "bg": COLORS["error"], "fg": COLORS["white"], "activebackground": COLORS["error_dark"],
        "activeforeground": COLORS["white"], "relief": "flat", "borderwidth": 0, "padx": 15, "pady": 8,
        "cursor": "hand2", "font": FONTS["button"]
    },
     "text_button": { # 文本按钮样式
        "bg": COLORS["background"], "fg": COLORS["primary"], "activebackground": COLORS["background"],
        "activeforeground": COLORS["primary_dark"], "relief": "flat", "borderwidth": 0, "padx": 5, "pady": 2,
        "cursor": "hand2", "font": FONTS["body_bold"]
    }
}
LABEL_STYLE = { # 标签样式
    "title": {"font": FONTS["title"], "fg": COLORS["text"], "bg": COLORS["background"], "pady": 10, "anchor": "center"},
    "subtitle": {"font": FONTS["subtitle"], "fg": COLORS["text_light"], "bg": COLORS["background"], "pady": 8, "anchor": "center"},
    "info": {"font": FONTS["body"], "fg": COLORS["text"], "bg": COLORS["white"], "pady": 5, "anchor": "w"},
    "url_entry": { # URL 输入框样式
        "font": FONTS["body"], "fg": COLORS["primary"], "readonlybackground": COLORS["white"], "relief":"solid",
        "borderwidth":1, "highlightthickness":1, "highlightcolor":COLORS["light_gray"],
        "highlightbackground":COLORS["light_gray"], "state":"readonly"
    },
    "status": {"font": FONTS["body_bold"], "fg": COLORS["text_light"], "bg": COLORS["white"], "pady": 5, "anchor": "w"},
    "listbox": { # 列表框样式
         "font": FONTS["body"], "fg": COLORS["text"], "bg": COLORS["white"], "selectbackground": COLORS["accent"],
         "selectforeground": COLORS["white"], "activestyle": "none", "relief": "flat", "borderwidth": 0,
         "highlightthickness": 0
    },
    "hint": {"font": FONTS["small"], "fg": COLORS["text_light"], "bg": COLORS["background"], "pady": 2, "anchor": "center"}
}
FRAME_STYLE = { # 框架样式
    "main": {"bg": COLORS["background"], "padx": LAYOUT["padding"], "pady": LAYOUT["padding"]},
    "content_card": {
        "bg": COLORS["white"], "padx": LAYOUT["padding"], "pady": LAYOUT["padding"], "relief": "solid",
        "borderwidth": 0, "highlightbackground": COLORS["light_gray"], "highlightthickness": 1
    },
    "section": {"bg": COLORS["white"], "padx": 0, "pady": 0},
    "file_list_container": { # 文件列表容器样式
        "bg": COLORS["light_gray"], "relief": "sunken", "borderwidth": 1,
        "highlightbackground": COLORS["medium_gray"], "highlightthickness": 0
    },
     "footer_bar": {"bg": COLORS["background"], "pady": LAYOUT["small_padding"]}
}
# --- 结束：嵌入式 styles.py 内容 ---

# --- ModernButton 自定义组件 ---
class ModernButton(Button):
    def __init__(self, master=None, cnf={}, **kw):
        passed_bg = kw.get("bg", cnf.get("bg"))
        passed_activebg = kw.get("activebackground", cnf.get("activebackground"))
        default_button_style = BUTTON_STYLE.get("primary", {}) # 获取默认样式
        # 初始化原始背景色和悬停背景色
        self.original_bg = passed_bg if passed_bg is not None else default_button_style.get("bg", COLORS.get("primary"))
        self.hover_bg = passed_activebg if passed_activebg is not None else default_button_style.get("activebackground", COLORS.get("primary_dark"))
        # 设置默认浮雕和边框宽度
        if 'relief' not in kw and 'relief' not in cnf: kw['relief'] = 'flat'
        if 'borderwidth' not in kw and 'borderwidth' not in cnf: kw['borderwidth'] = 0
        super().__init__(master, cnf, **kw)
        self.bind("<Enter>", self.on_enter) # 鼠标进入事件
        self.bind("<Leave>", self.on_leave) # 鼠标离开事件

    def on_enter(self, event): # 鼠标进入时改变背景色
        if self['state'] == NORMAL: self.config(bg=self.hover_bg)
    def on_leave(self, event): # 鼠标离开时恢复背景色
        if self['state'] == NORMAL: self.config(bg=self.original_bg)
    def config(self, cnf=None, **kw): # 重写 config/configure 方法以更新颜色
        if cnf: kw.update(cnf)
        if 'bg' in kw: self.original_bg = kw['bg']
        if 'activebackground' in kw: self.hover_bg = kw['activebackground']
        super().config(cnf, **kw)
    configure = config


class MyHandler(BaseHTTPRequestHandler):
    def _headers_sent(self): # 检查头部是否已发送
         return hasattr(self, '_headers_buffer') and self._headers_buffer is not None and len(self._headers_buffer) > 0

    def do_HEAD(s): # 处理 HEAD 请求
        s.send_response(200)
        s.send_header("Content-type", "text/html; charset=utf-8")
        s.end_headers()

    def do_GET(s): # 处理 GET 请求
        global filepaths # 使用全局 filepaths 列表 (现在是字典列表)
        global app_instance # 用于调用 app_instance.showUploadedFile() 等
        try:
            # 解码路径，移除查询参数和片段标识符
            decoded_path = unquote(s.path, encoding='utf-8', errors='replace')
            decoded_path = decoded_path.split('?', 1)[0].split('#', 1)[0]
        except Exception as e:
            print(f"处理程序错误: 解码路径 '{s.path}' 时出错: {e}")
            if not s._headers_sent(): s.send_error(400, "错误请求: 无效的URL路径格式")
            return

        if decoded_path == '/' or decoded_path == '': # 如果是根路径，显示文件列表HTML页面
             s.send_response(200)
             s.send_header("Content-type", "text/html; charset=utf-8")
             s.end_headers()
             html_page_font_family = FONTS["body"][0] if "body" in FONTS and isinstance(FONTS["body"], tuple) and len(FONTS["body"]) > 0 else "sans-serif"
             # --- 带有上传表单和删除按钮的 HTML 模板 ---
             html_page_template = f"""
            <!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>本地文件分享</title><style>
                body {{ font-family: "{html_page_font_family}", sans-serif; background-color: {COLORS["background"]}; color: {COLORS["text"]}; margin: 0; padding: 20px; line-height: 1.6; }}
                .container {{ max-width: 800px; margin: 30px auto; background-color: {COLORS["white"]}; padding: 30px; border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,0.07); }}
                h1 {{ color: {COLORS["primary"]}; margin-top: 0; font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 20px;}}
                h3 {{ color: {COLORS["secondary"]}; font-size: 18px; font-weight: 500; margin-bottom: 20px; border-bottom: 1px solid {COLORS["light_gray"]}; padding-bottom: 10px; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin-bottom: 12px; background-color: {COLORS["white"]}; border: 1px solid {COLORS["light_gray"]}; border-radius: 6px; transition: all 0.2s ease-in-out; display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);}}
                li:hover {{ border-color: {COLORS["accent"]}; transform: translateY(-1px); box-shadow: 0 3px 7px rgba(0,0,0,0.05);}}
                .file-info-container {{ display: flex; flex-direction: column; flex-grow: 1; margin-right: 15px; overflow: hidden; }}
                .file-name-link {{ color: {COLORS["primary"]}; text-decoration: none; font-weight: bold; font-size: 15px; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
                .file-name-link:hover {{ text-decoration: underline; color: {COLORS["primary_dark"]}; }}
                .file-size-span {{ font-size: 12px; color: {COLORS["text_light"]}; margin-top: 3px; }}
                .file-source-tag {{ font-size: 0.85em; color: {COLORS["text_light"]}; margin-left: 8px; font-style: italic; opacity: 0.8; }} /* 新增来源标签样式 */
                .action-buttons-group {{ display: flex; align-items: center; }}
                .download-button {{ padding: 7px 15px; background-color: {COLORS["success"]}; color: white; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: bold; white-space: nowrap; border: none; cursor: pointer; transition: background-color 0.2s ease; margin-right: 8px; }}
                .download-button:hover {{ background-color: {COLORS["success_dark"]}; }}
                .delete-button {{ padding: 7px 15px; background-color: {COLORS["error"]}; color: white; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: bold; white-space: nowrap; border: none; cursor: pointer; transition: background-color 0.2s ease; }}
                .delete-button:hover {{ background-color: {COLORS["error_dark"]}; }}
                .upload-form-container {{ margin: 25px 0; padding: 20px; background-color: {COLORS["light_gray"]}; border-radius: 6px; }}
                .upload-form-container h4 {{ margin-top:0; color: {COLORS["primary"]}; }}
                .upload-form-container input[type="file"] {{ margin-bottom: 10px; display: block; }}
                .upload-form-container input[type="submit"] {{ background-color: {COLORS["accent"]}; color:white; border:none; padding: 10px 20px; border-radius:5px; cursor:pointer; font-weight:bold; }}
                .upload-form-container input[type="submit"]:hover {{ background-color: {COLORS["accent_light"]}; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: {COLORS["text_light"]}; }}
                .no-files-message {{ padding: 25px; text-align: center; color: {COLORS["text_light"]}; background-color: {COLORS["light_gray"]}; border-radius: 6px; font-size: 15px; }}
            </style></head><body><div class="container"><h1>本地文件分享</h1>
            <div class="upload-form-container">
                <h4>上传文件到服务器</h4>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="files_to_upload" multiple required>
                    <input type="submit" value="上传选定文件">
                </form>
            </div>
            <h3>可供下载的文件列表</h3><ul>
            """
             s.wfile.write(html_page_template.encode('utf-8')) # 写入HTML头部（字节串）
             
             # 按文件名排序以获得一致的显示
             sorted_items_for_web = sorted(filepaths, key=lambda item: item['name'].lower())

             if sorted_items_for_web:
                 for item_data in sorted_items_for_web: # 遍历排序后的文件信息字典
                     full_path = item_data['path']
                     display_file_name = item_data['name']
                     size_str = item_data['size_str'] # 从字典中获取格式化后的大小
                     source_tag_web = "" # 文件来源标签
                     if item_data['source'] == FILE_SOURCE_GUI:
                         source_tag_web = "<span class='file-source-tag'>(来自应用)</span>"
                     elif item_data['source'] == FILE_SOURCE_BROWSER:
                         source_tag_web = "<span class='file-source-tag'>(来自浏览器)</span>"

                     # 检查文件是否存在，如果不存在，则安排从GUI中移除
                     if not os.path.exists(full_path):
                         if app_instance and app_instance.master.winfo_exists(): # 确保GUI实例存在
                            app_instance.master.after_idle(lambda itm_dict=item_data: app_instance.remove_item_if_not_exists(itm_dict))
                         continue # 跳过不存在的文件
                     
                     try:
                         # 正确编码文件名用于URL和HTTP头
                         encoded_link_fn = quote(display_file_name, safe='')
                         encoded_delete_fn_param = quote(display_file_name, safe='') # 用于删除表单的查询参数

                         # Escape filename for JavaScript confirm dialog
                         escaped_display_file_name = display_file_name.replace("'", "\'").replace('"', '\"')

                         item_html = f"""
                         <li>
                             <div class="file-info-container">
                                 <a href="/{encoded_link_fn}" download="{encoded_link_fn}" class="file-name-link" title="下载 {display_file_name}">{display_file_name}</a>
                                 <span class="file-size-span">({size_str}) {source_tag_web}</span>
                             </div>
                             <div class="action-buttons-group">
                                 <a href="/{encoded_link_fn}" download="{encoded_link_fn}" class="download-button">下载</a>
                                 <form action="/delete" method="post" style="display: inline;">
                                     <input type="hidden" name="filename_to_delete" value="{encoded_delete_fn_param}">
                                     <button type="submit" class="delete-button" onclick="return confirm('确定要删除 {escaped_display_file_name} 吗？');">删除</button>
                                 </form>
                             </div>
                         </li>"""
                         s.wfile.write(item_html.encode('utf-8')) # 写入每个文件项的HTML（字节串）
                     except Exception as e_item:
                         # 写入错误信息（字节串）
                         s.wfile.write(f"<li>错误显示文件: {display_file_name} ({e_item})</li>".encode('utf-8'))
             else:
                 # 没有文件时显示的消息（字节串）
                 s.wfile.write("<li class='no-files-message'>当前没有文件可供下载。请在应用程序中或通过上面的表单添加文件。</li>".encode('utf-8'))
             s.wfile.write("</ul><div class='footer'>通过本地WiFi网络分享的文件</div></div></body></html>".encode('utf-8')) # 写入HTML尾部（字节串）
             return

        # 如果路径与共享文件匹配，则提供文件下载
        requested_file_name = os.path.basename(decoded_path) # 从解码路径获取基础文件名
        matched_item_dict = None # 用于存储匹配的文件信息字典
        for item_d in filepaths: # 遍历全局文件信息列表
            if item_d['name'].lower() == requested_file_name.lower(): # 不区分大小写匹配文件名
                matched_item_dict = item_d
                break

        if matched_item_dict:
             matched_filepath = matched_item_dict['path'] # 获取完整路径
             actual_display_name_for_header = matched_item_dict['name'] # 获取用于HTTP头的文件名

             # 再次检查文件是否存在
             if not os.path.exists(matched_filepath):
                 if not s._headers_sent(): s.send_error(404, f"文件 '{actual_display_name_for_header}' 在服务器上未找到。")
                 # 如果文件不存在，也尝试从 filepaths 中移除
                 if app_instance and app_instance.master.winfo_exists():
                    app_instance.master.after_idle(lambda itm=matched_item_dict: app_instance.remove_item_if_not_exists(itm))
                 return
             try:
                 file_size = os.path.getsize(matched_filepath)
                 content_type, _ = mimetypes.guess_type(matched_filepath) #猜测MIME类型
                 if content_type is None: content_type = "application/octet-stream" # 默认为二进制流
                 if content_type.startswith("text/"): content_type = f"{content_type}; charset=utf-8" # 文本文件指定UTF-8

                 s.send_response(200)
                 s.send_header("Content-Type", content_type)

                 # 正确编码文件名用于 Content-Disposition 头
                 encoded_fn_for_header_star = quote(actual_display_name_for_header, encoding='utf-8', safe='')
                 safe_filename_for_header_equals = actual_display_name_for_header # 回退机制
                 try:
                     safe_filename_for_header_equals.encode('latin-1') # 尝试直接编码
                 except UnicodeEncodeError:
                      # 创建一个安全的 ASCII 表示
                      safe_filename_for_header_equals = "".join(
                          c if ord(c) < 128 else '_' for c in os.path.splitext(actual_display_name_for_header)[0]
                      ) + os.path.splitext(actual_display_name_for_header)[1]
                      if not safe_filename_for_header_equals.strip("_-."): # 如果只有不安全字符
                          safe_filename_for_header_equals = "downloaded_file" + os.path.splitext(actual_display_name_for_header)[1]
                 
                 disposition_value = f'attachment; filename="{safe_filename_for_header_equals}"; filename*=UTF-8\'\'{encoded_fn_for_header_star}'
                 s.send_header("Content-Disposition", disposition_value)
                 s.send_header("Content-Length", str(file_size))
                 s.send_header("Cache-Control", "no-cache, no-store, must-revalidate") # 禁用缓存
                 s.send_header("Pragma", "no-cache"); s.send_header("Expires", "0")
                 s.end_headers()

                 try:
                     with open(matched_filepath, 'rb') as f: # 以二进制读取模式打开文件
                         bytes_sent_total = 0; chunk_size = 65536 # 64KB 分块大小
                         while True:
                             chunk = f.read(chunk_size) # 读取文件块
                             if not chunk: break # 文件读取完毕
                             try:
                                 s.wfile.write(chunk) # 发送文件块（字节串）
                                 bytes_sent_total += len(chunk)
                             except (ConnectionResetError, BrokenPipeError): # 捕获客户端断开连接的错误
                                 print(f"处理程序: 客户端在传输 {actual_display_name_for_header} 期间断开连接")
                                 return # 停止尝试发送
                         s.wfile.flush() # 确保所有数据已发送
                 except FileNotFoundError: # 文件在打开后被删除的罕见情况
                     if not s._headers_sent(): s.send_error(404, f"文件 '{actual_display_name_for_header}' 未找到 (竞争条件?)。")
                 except Exception as e:
                     print(f"处理程序错误: 文件传输 {actual_display_name_for_header} 期间: {e}")
                     if not s._headers_sent(): s.send_error(500, f"文件传输期间服务器错误: {e}")
                 return
             except Exception as e_outer:
                 print(f"处理程序错误: 准备文件 {actual_display_name_for_header}: {e_outer}")
                 if not s._headers_sent(): s.send_error(500, f"服务器准备文件时出错: {e_outer}")
                 return
        else: # 如果请求的文件名在列表中未匹配到
            if not s._headers_sent(): s.send_error(404, "未找到: 请求的文件未在服务器列表中找到。")
            return

    def do_POST(s): # 处理 POST 请求
        global filepaths # 使用全局文件信息列表
        global app_instance # 用于更新GUI

        content_type_header = s.headers.get('Content-Type', '') # 安全获取Content-Type
        content_length_header = s.headers.get('Content-Length') # 安全获取Content-Length

        if not content_length_header: # 检查Content-Length是否存在
            s.send_response(411) # Length Required
            s.send_header('Content-Type', 'text/plain; charset=utf-8')
            s.end_headers()
            s.wfile.write("错误请求: 需要 Content-Length 头部".encode('utf-8')) # 发送字节串错误信息
            return
        try:
            content_length = int(content_length_header) # 转换Content-Length为整数
        except ValueError:
            s.send_response(400)
            s.send_header('Content-Type', 'text/plain; charset=utf-8')
            s.end_headers()
            s.wfile.write("错误请求: Content-Length 无效".encode('utf-8')) # 发送字节串错误信息
            return

        if 'multipart/form-data' not in content_type_header: # 检查是否为 multipart/form-data
            s.send_response(400)
            s.send_header('Content-Type', 'text/plain; charset=utf-8')
            s.end_headers()
            s.wfile.write("错误请求: 需要 multipart/form-data".encode('utf-8')) # 发送字节串错误信息
            return

        # 解析表单数据
        form = cgi.FieldStorage(
            fp=s.rfile, # 从请求体读取
            headers=s.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': content_type_header, # 使用安全的头部信息
                     'CONTENT_LENGTH': str(content_length) # cgi可能需要字符串形式的长度
                     })

        if s.path == '/upload': # 处理文件上传
            if not os.path.exists(UPLOAD_FOLDER): # 检查上传文件夹是否存在
                try:
                    os.makedirs(UPLOAD_FOLDER) # 创建上传文件夹
                except OSError as e:
                    print(f"处理程序错误: 无法创建上传文件夹 {UPLOAD_FOLDER}: {e}")
                    s.send_response(500)
                    s.send_header('Content-Type', 'text/plain; charset=utf-8')
                    s.end_headers()
                    s.wfile.write("服务器错误: 无法创建上传目录。".encode('utf-8')) # 发送字节串错误信息
                    return


            if 'files_to_upload' not in form: # 检查表单中是否有上传的文件
                s.send_response(400)
                s.send_header('Content-Type', 'text/plain; charset=utf-8')
                s.end_headers()
                s.wfile.write("在上传请求中未找到文件。".encode('utf-8')) # 发送字节串错误信息
                return

            form_files = form['files_to_upload']
            if not isinstance(form_files, list): # 处理单个文件上传的情况
                form_files = [form_files]

            newly_added_to_list_count = 0 # 记录新添加到列表的文件数
            for file_item in form_files: # 遍历上传的文件项
                if file_item.filename: # 确保文件项有文件名
                    original_filename_from_client = os.path.basename(file_item.filename) # 获取原始文件名
                    # 清理文件名（简单版本）
                    filename_sanitized = "".join(c for c in original_filename_from_client if c.isalnum() or c in ['.', '_', '-'])
                    if not filename_sanitized: filename_sanitized = f"uploaded_file_{int(time.time())}" # 如果清理后文件名为空，则生成一个

                    save_path_candidate = os.path.join(UPLOAD_FOLDER, filename_sanitized) # 候选保存路径
                    
                    # 防止覆盖，通过在文件名后附加数字
                    counter = 1
                    actual_filename_to_save = filename_sanitized # 最终保存的文件名
                    final_save_path = save_path_candidate # 最终保存路径
                    original_filename_stem, original_filename_ext = os.path.splitext(filename_sanitized)
                    while os.path.exists(final_save_path): # 如果文件已存在
                        actual_filename_to_save = f"{original_filename_stem}_{counter}{original_filename_ext}"
                        final_save_path = os.path.join(UPLOAD_FOLDER, actual_filename_to_save)
                        counter += 1
                    
                    try:
                        with open(final_save_path, 'wb') as f_out: # 以二进制写入模式保存文件
                            shutil.copyfileobj(file_item.file, f_out) # 从内存复制到文件
                        
                        abs_final_save_path = os.path.abspath(final_save_path) # 获取绝对路径
                        
                        # 如果文件的绝对路径不在全局列表中，则添加
                        if not any(item['path'] == abs_final_save_path for item in filepaths):
                            new_file_entry = {
                                'path': abs_final_save_path,
                                'name': actual_filename_to_save, # 使用在服务器上保存的（可能重命名的）文件名
                                'size_str': App.format_file_size_static(os.path.getsize(abs_final_save_path)),
                                'source': FILE_SOURCE_BROWSER # 标记来源为浏览器
                            }
                            filepaths.append(new_file_entry) # 添加到全局列表
                            newly_added_to_list_count +=1
                            print(f"处理程序: 已将来自浏览器的 '{actual_filename_to_save}' 添加到共享列表。")
                        else:
                             print(f"处理程序: 文件 '{abs_final_save_path}' 已在列表中 (可能由GUI从上传文件夹共享)。未重新添加。")
                        
                    except Exception as e:
                        print(f"处理程序错误: 无法保存上传的文件 {original_filename_from_client} 为 {actual_filename_to_save}: {e}")
                else:
                    print("处理程序: 收到一个没有文件名的文件项。")

            # 上传后，重定向到主页
            s.send_response(303) # See Other (POST后重定向)
            s.send_header('Location', '/')
            s.end_headers()
            if app_instance and app_instance.master.winfo_exists() and newly_added_to_list_count > 0 : # 如果GUI存在且有新文件添加
                app_instance.master.after_idle(app_instance.showUploadedFile) # 更新Tkinter GUI列表

        elif s.path == '/delete': # 处理文件删除
            filename_to_delete_encoded = form.getvalue('filename_to_delete') # 获取要删除的文件名（已编码）
            if not filename_to_delete_encoded:
                s.send_response(400); s.send_header('Content-Type', 'text/plain; charset=utf-8'); s.end_headers()
                s.wfile.write("错误请求: 缺少 filename_to_delete 参数。".encode('utf-8')); return # 发送字节串错误信息

            filename_to_delete = unquote(filename_to_delete_encoded) # 解码文件名
            item_to_remove_web = None # 要从列表中移除的项
            path_to_delete_on_disk = None # 要从磁盘删除的路径

            # 在全局列表中查找要删除的文件
            for item_d in filepaths:
                if item_d['name'] == filename_to_delete: # 匹配文件名
                    item_to_remove_web = item_d
                    path_to_delete_on_disk = item_d['path']
                    break
            
            action_occurred = False # 标记是否执行了删除操作
            if item_to_remove_web: # 如果找到了要删除的项
                if os.path.exists(path_to_delete_on_disk): # 检查文件是否存在于磁盘
                    try:
                        os.remove(path_to_delete_on_disk) # 从磁盘删除
                        filepaths.remove(item_to_remove_web) # 从全局列表移除
                        print(f"处理程序: 已删除 '{filename_to_delete}' 从 '{path_to_delete_on_disk}' (通过web请求)")
                        action_occurred = True
                    except Exception as e:
                        print(f"处理程序错误: 无法从磁盘删除文件 {filename_to_delete}: {e}")
                        s.send_response(500); s.send_header('Content-Type', 'text/plain; charset=utf-8'); s.end_headers()
                        s.wfile.write(f"从磁盘删除文件时出错: {e}".encode('utf-8')); return # 发送编码后的字节串错误
                else: # 文件在磁盘上未找到，但可能仍在列表中
                    try:
                        filepaths.remove(item_to_remove_web) # 仅从列表移除
                        print(f"处理程序: 文件 '{filename_to_delete}' 在磁盘上未找到，已从列表中移除 (通过web请求)。")
                        action_occurred = True 
                    except ValueError: # 如果项已不在列表中
                        print(f"处理程序警告: 无法从文件路径列表中移除 '{filename_to_delete}'，是否已移除?")
                
                if action_occurred and app_instance and app_instance.master.winfo_exists(): # 如果操作成功且GUI存在
                    app_instance.master.after_idle(app_instance.showUploadedFile) # 更新GUI
                
                if action_occurred: # 如果操作成功，重定向
                    s.send_response(303); s.send_header('Location', '/'); s.end_headers()
                # else: (如果磁盘删除失败，错误已发送)
            
            else: # 如果在列表中未找到文件
                s.send_response(404); s.send_header('Content-Type', 'text/plain; charset=utf-8'); s.end_headers()
                s.wfile.write("具有该名称的文件未在共享列表中找到。".encode('utf-8')); return # 发送字节串错误
        else: # 未知的POST端点
            s.send_response(404); s.send_header('Content-Type', 'text/plain; charset=utf-8'); s.end_headers()
            s.wfile.write("未找到: 未知的POST端点。".encode('utf-8')); return # 发送字节串错误信息


class App: # Tkinter应用程序类
    def __init__(self, master):
        self.master = master
        master.configure(bg=COLORS["background"])
        master.title("本地文件分享")
        master.geometry("800x700"); master.minsize(700, 650) # 增加了高度以容纳新按钮

        # 确保上传文件夹存在
        if not os.path.exists(UPLOAD_FOLDER):
            try:
                os.makedirs(UPLOAD_FOLDER)
                print(f"应用: 已在 '{os.path.abspath(UPLOAD_FOLDER)}' 创建 UPLOAD_FOLDER")
            except OSError as e:
                messagebox.showerror("错误", f"无法创建上传文件夹 '{UPLOAD_FOLDER}': {e}")

        self.fonts = {} # 初始化字体
        for name, definition in FONTS.items():
            font_config = {"family": definition[0], "size": definition[1]}
            if len(definition) > 2: # 处理粗体、斜体等样式
                for style_attr in definition[2:]:
                    if isinstance(style_attr, str):
                        attr_lower = style_attr.lower()
                        if attr_lower == "bold": font_config["weight"] = "bold"
                        elif attr_lower == "italic": font_config["slant"] = "italic"
                        elif attr_lower == "underline": font_config["underline"] = True
                        elif attr_lower == "overstrike": font_config["overstrike"] = True
            self.fonts[name] = tkFont.Font(**font_config)


        self.ip_addr_str = get_ip_addr(); self.port = 8080 # 获取IP和端口
        self.url = f"http://{self.ip_addr_str}:{self.port}" # 构建URL
        self.http_server_thread = None # HTTP服务器线程
        self.httpd_server_instance = None; self.is_server_running = False # 服务器实例和运行状态

        # --- GUI 布局 ---
        self.main_frame = Frame(master, **FRAME_STYLE["main"]); self.main_frame.pack(fill=BOTH, expand=True)
        self.title_label = Label(self.main_frame, text="本地文件分享", font=self.fonts["title"], **{k:v for k,v in LABEL_STYLE["title"].items() if k !='font'})
        self.title_label.pack(pady=(0, LAYOUT["small_spacing"]))
        self.subtitle_label = Label(self.main_frame, text="简单、快速地分享文件到同一网络的设备", font=self.fonts["subtitle"], **{k:v for k,v in LABEL_STYLE["subtitle"].items() if k !='font'})
        self.subtitle_label.pack(pady=(0, LAYOUT["padding"]))

        self.content_card = Frame(self.main_frame, **FRAME_STYLE["content_card"]); self.content_card.pack(fill=BOTH, expand=True)

        # 文件信息区域 (标签和文件计数)
        self.file_info_section = Frame(self.content_card, **FRAME_STYLE["section"]); self.file_info_section.pack(fill=X, pady=(0, LAYOUT["small_spacing"]))
        Label(self.file_info_section, text="共享文件列表:", bg=COLORS["white"], font=self.fonts["body_bold"], fg=COLORS["text"]).pack(side=LEFT)
        self.file_count_label = Label(self.file_info_section, text="0 个文件", bg=COLORS["white"], font=self.fonts["body"], fg=COLORS["text_light"]); self.file_count_label.pack(side=RIGHT)

        # 文件列表框和滚动条
        self.list_container = Frame(self.content_card, **FRAME_STYLE["file_list_container"]); self.list_container.pack(fill=BOTH, expand=True, pady=LAYOUT["small_spacing"])
        self.scrollbar = Scrollbar(self.list_container, orient=VERTICAL)
        self.files_listbox = Listbox(self.list_container, yscrollcommand=self.scrollbar.set, height=10, font=self.fonts["body"], exportselection=False, **{k:v for k,v in LABEL_STYLE["listbox"].items() if k != 'font'})
        self.scrollbar.config(command=self.files_listbox.yview); self.scrollbar.pack(side=RIGHT, fill=Y)
        self.files_listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=LAYOUT["small_padding"], pady=LAYOUT["small_padding"])

        # 操作按钮区域
        self.action_buttons_frame = Frame(self.content_card, **FRAME_STYLE["section"]); self.action_buttons_frame.pack(fill=X, pady=(LAYOUT["small_spacing"], LAYOUT["small_spacing"]))
        btn_secondary_style_dict = {k:v for k,v in BUTTON_STYLE["secondary"].items() if k!='font'}
        btn_primary_style_dict = {k:v for k,v in BUTTON_STYLE["primary"].items() if k!='font'}
        btn_danger_style_dict_small = {k:v for k,v in BUTTON_STYLE["danger"].items() if k!='font'}
        btn_danger_style_dict_small["padx"] = 10 # 使删除按钮稍微小一点
        btn_danger_style_dict_small["pady"] = 8


        self.upload_button = ModernButton(self.action_buttons_frame, text="选择文件", command=self.choose_files_via_gui, font=self.fonts["button"], **btn_secondary_style_dict)
        self.upload_button.pack(side=LEFT, padx=(0, LAYOUT["small_spacing"]))

        # 新增 "另存选中" 按钮
        self.save_as_gui_button = ModernButton(self.action_buttons_frame, text="另存选中", command=self.save_selected_file_as_gui, font=self.fonts["button"], **btn_secondary_style_dict)
        self.save_as_gui_button.pack(side=LEFT, padx=(0, LAYOUT["small_spacing"]))
        
        self.delete_gui_button = ModernButton(self.action_buttons_frame, text="删除选中", command=self.delete_selected_file_from_gui, font=self.fonts["button"], **btn_danger_style_dict_small)
        self.delete_gui_button.pack(side=LEFT, padx=(0, LAYOUT["small_spacing"]))
        
        self.serve_button = ModernButton(self.action_buttons_frame, text="开始分享", command=self.toggle_server_state, font=self.fonts["button"], **btn_primary_style_dict)
        self.serve_button.pack(side=LEFT)

        # 服务器状态和URL显示区域
        self.info_frame = Frame(self.content_card, **FRAME_STYLE["section"]); self.info_frame.pack(fill=X, pady=(LAYOUT["small_spacing"], 0))
        self.status_label = Label(self.info_frame, text="服务器: 未启动", font=self.fonts["body_bold"], **{k:v for k,v in LABEL_STYLE["status"].items() if k!='font'})
        self.status_label.pack(side=LEFT, pady=(0, LAYOUT["small_spacing"]))

        self.url_container = Frame(self.info_frame, **FRAME_STYLE["section"]); self.url_container.pack(side=RIGHT, fill=X, expand=True, pady=(0, LAYOUT["small_spacing"]), padx=(LAYOUT["small_spacing"], 0))
        self.url_display_label = Entry(self.url_container, font=self.fonts["body"], **{k:v for k,v in LABEL_STYLE["url_entry"].items() if k!='font'})
        self.url_display_label.pack(side=LEFT, fill=X, expand=True); self.url_display_label.insert(0, self.url)
        copy_btn_style_dict = {k:v for k,v in BUTTON_STYLE["secondary"].items() if k not in ['font', 'padx', 'pady']}
        self.copy_url_button = ModernButton(self.url_container, text="复制", command=self.copy_url_to_clipboard, font=self.fonts["small_bold"], padx=10, pady=4, state=DISABLED, **copy_btn_style_dict)
        self.copy_url_button.pack(side=LEFT, padx=(LAYOUT["small_spacing"], 0))

        # 底部提示信息
        self.footer_frame = Frame(self.main_frame, **FRAME_STYLE["footer_bar"]); self.footer_frame.pack(fill=X, side=BOTTOM)
        self.footer_label = Label(self.footer_frame, text="确保设备连接到同一WiFi网络以下载文件。", font=self.fonts["small"], **{k:v for k,v in LABEL_STYLE["hint"].items() if k!='font'}); self.footer_label.pack()


        self.showUploadedFile() # 初始化时调用以显示文件列表
        self._update_gui_after_server_stop() # 初始化服务器相关GUI元素状态

    def remove_item_if_not_exists(self, item_dict_to_check):
        """从filepaths中移除字典项，如果其路径不存在。由HTTP处理器调用。"""
        global filepaths
        path_to_check = item_dict_to_check.get('path') # 获取项的路径
        if not path_to_check: return # 如果没有路径，则返回

        removed_by_identity = False # 标记是否通过对象身份移除
        if item_dict_to_check in filepaths: # 检查项是否在列表中
            if not os.path.exists(path_to_check): # 如果路径不存在
                try:
                    filepaths.remove(item_dict_to_check) # 尝试通过对象身份移除
                    print(f"应用: 通过身份移除非存在项 '{path_to_check}'。")
                    removed_by_identity = True
                except ValueError: # 并发修改可能导致此问题
                    pass 
        
        # 如果通过身份移除失败 (或未尝试)，但路径确实不存在，则按路径移除
        if not removed_by_identity and not os.path.exists(path_to_check):
            self.remove_path_if_not_exists(path_to_check) # 这会调用 showUploadedFile
        elif removed_by_identity: # 如果通过身份移除成功，则刷新GUI
            self.showUploadedFile()

    def remove_path_if_not_exists(self, file_path_to_check):
        """(主要由GUI内部使用) 从filepaths中移除具有指定路径的所有项，如果路径不存在。"""
        global filepaths
        original_length = len(filepaths)
        # 创建一个新列表，排除路径不存在的项
        filepaths[:] = [item for item in filepaths if not (item['path'] == file_path_to_check and not os.path.exists(item['path']))]
        
        if len(filepaths) < original_length: # 如果列表长度改变
            print(f"应用: 从列表中移除非存在路径 '{file_path_to_check}'。")
            self.showUploadedFile() # 刷新GUI列表

    def showUploadedFile(self): # 更新GUI中的文件列表框
        global filepaths
        self.files_listbox.delete(0, END) # 清空列表框
        
        # 在迭代前清理不存在的文件 (创建副本进行迭代)
        items_removed_count = 0
        for item in list(filepaths): # 迭代副本以安全地修改原始列表
            if not os.path.exists(item['path']): # 如果文件路径不存在
                print(f"应用 (showUploadedFile): 路径 {item['path']} 不再存在。从列表中移除。")
                try:
                    filepaths.remove(item) # 从原始全局列表中移除
                    items_removed_count +=1
                except ValueError: # 可能由于并发修改导致项已不在列表中
                    pass 
        # filepaths 全局列表现已清理。

        if not filepaths: # 如果清理后没有文件
            self.files_listbox.insert(END, "  没有共享文件");
            self.files_listbox.config(fg=COLORS["text_light"]) # 设置提示文字颜色
            self.file_count_label.configure(text="0 个文件") # 更新文件计数
            self.delete_gui_button.configure(state=DISABLED) # 禁用删除按钮
            self.save_as_gui_button.configure(state=DISABLED) # 禁用另存为按钮
            return

        self.files_listbox.config(fg=COLORS["text"]) # 恢复正常文本颜色
        
        # 按文件名排序显示
        sorted_items_for_display = sorted(filepaths, key=lambda x: x['name'].lower())
        
        file_count = len(sorted_items_for_display)
        self.file_count_label.configure(text=f"{file_count} 个文件") # 更新文件计数
        self.delete_gui_button.configure(state=NORMAL if file_count > 0 else DISABLED) # 根据文件数量设置按钮状态
        self.save_as_gui_button.configure(state=NORMAL if file_count > 0 else DISABLED)

        # 填充列表框
        for item in sorted_items_for_display:
            display_source_tag = "" # 文件来源标签
            if item['source'] == FILE_SOURCE_GUI:
                display_source_tag = "[应用选择]"
            elif item['source'] == FILE_SOURCE_BROWSER:
                display_source_tag = "[浏览器上传]"
            
            listbox_entry = f"  {item['name']} ({item['size_str']}) {display_source_tag}"
            self.files_listbox.insert(END, listbox_entry)

    @staticmethod
    def format_file_size_static(size_bytes): # 静态方法格式化文件大小
        if size_bytes is None: return "未知大小"
        try: size_bytes = int(size_bytes)
        except (ValueError, TypeError): return "无效大小"
        if size_bytes < 0: return "无效大小";
        if size_bytes == 0: return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]; i = 0
        while size_bytes >= 1024 and i < len(units) - 1: size_bytes /= 1024.0; i += 1
        return f"{size_bytes:.1f} {units[i]}"
    format_file_size = format_file_size_static # 别名，方便实例方法调用

    def choose_files_via_gui(self): # 通过GUI选择文件
        global filepaths
        # 打开文件选择对话框
        chosen_files_temp = askopenfilenames(
            multiple=True,
            title="选择文件 (替换应用选择的文件, 保留浏览器上传的)",
            filetypes=[("所有文件", "*.*"), ("文本文档", "*.txt"), ("图片", "*.png *.jpg *.jpeg *.gif"), ("PDF", "*.pdf")]
        )
        
        # 先移除所有之前通过GUI选择的文件
        filepaths[:] = [item for item in filepaths if item['source'] != FILE_SOURCE_GUI]

        if not chosen_files_temp: # 如果用户取消选择
            self.showUploadedFile() # 刷新列表（可能清空了GUI文件）
            self.status_label.configure(text="服务器: 应用选择的文件已清空", fg=COLORS["text_light"])
            return

        new_gui_files_added_count = 0 # 记录新添加的GUI文件数
        for f_path_str in chosen_files_temp: # 遍历选择的文件路径
            abs_path = os.path.abspath(f_path_str) # 获取绝对路径
            # 检查路径是否已存在 (例如来自浏览器或之前选择的且未被清除的)
            if any(item['path'] == abs_path for item in filepaths):
                print(f"应用: 文件 {abs_path} 已在列表中 (可能来自浏览器)，跳过。")
                messagebox.showinfo("跳过文件", f"文件 '{os.path.basename(abs_path)}' 已存在于共享列表中 (可能由浏览器上传)，因此未重新添加。")
                continue
            try:
                file_size = os.path.getsize(abs_path) # 获取文件大小
                new_file_item = { # 创建新的文件信息字典
                    'path': abs_path,
                    'name': os.path.basename(abs_path), # 文件名
                    'size_str': self.format_file_size(file_size), # 格式化大小
                    'source': FILE_SOURCE_GUI # 标记来源为GUI
                }
                filepaths.append(new_file_item) # 添加到全局列表
                new_gui_files_added_count += 1
            except Exception as e:
                print(f"应用错误: 无法处理文件 {abs_path}: {e}")
                messagebox.showerror("文件错误", f"处理文件 '{os.path.basename(abs_path)}' 时出错: {e}")
        
        self.showUploadedFile() # 刷新列表

        if new_gui_files_added_count > 0: # 如果成功添加了新文件
            status_msg = "服务器: 待启动 (文件已更新)" if not self.is_server_running else "服务器: 运行中 (列表已更新)"
            status_fg = COLORS["text"] if not self.is_server_running else COLORS["success"]
            self.status_label.configure(text=status_msg, fg=status_fg)
            if not self.is_server_running and self.master.winfo_exists(): # 如果服务器未运行，闪烁启动按钮
                self.flash_button(self.serve_button, BUTTON_STYLE["primary"]["activebackground"], BUTTON_STYLE["primary"]["bg"])


    def save_selected_file_as_gui(self): # GUI "另存为" 功能
        global filepaths
        selected_indices = self.files_listbox.curselection() # 获取列表框中选中的项
        if not selected_indices:
            messagebox.showwarning("另存为文件", "请先在列表中选择一个文件。")
            return

        selected_index = selected_indices[0] # 获取第一个选中项的索引
        # 列表框是基于排序后的 filepaths 显示的
        sorted_items_for_display = sorted(filepaths, key=lambda x: x['name'].lower())

        if selected_index >= len(sorted_items_for_display): # 检查索引是否有效
            messagebox.showerror("错误", "选择索引无效。列表可能已更改。")
            self.showUploadedFile() # 刷新列表
            return

        item_to_save_view = sorted_items_for_display[selected_index] # 获取选中项的视图信息
        # 从全局 filepaths 中找到实际的项以获取其路径 (通过路径匹配)
        actual_item_info = next((item for item in filepaths if item['path'] == item_to_save_view['path']), None)
        
        if not actual_item_info: # 如果未找到实际信息
             messagebox.showerror("错误", "无法找到文件信息。")
             self.showUploadedFile() 
             return

        source_path = actual_item_info['path'] # 源文件路径
        original_filename = actual_item_info['name'] # 原始文件名

        if not os.path.exists(source_path): # 检查源文件是否存在
            messagebox.showerror("错误", f"源文件 '{original_filename}' 不存在，无法另存为。")
            self.remove_item_if_not_exists(actual_item_info) # 从列表中移除不存在的文件
            return

        # 打开 "另存为" 对话框
        dest_path_suggestion = asksaveasfilename(
            initialfile=original_filename, # 建议的文件名
            title="选择保存位置...",
            defaultextension=os.path.splitext(original_filename)[1] or ".file", # 默认扩展名
            filetypes=[("所有文件", "*.*")] 
        )

        if dest_path_suggestion: # 如果用户选择了路径
            try:
                shutil.copy2(source_path, dest_path_suggestion) # 复制文件 (copy2保留元数据)
                messagebox.showinfo("成功", f"文件 '{original_filename}' 已保存到 '{os.path.basename(dest_path_suggestion)}'.")
            except Exception as e:
                messagebox.showerror("保存失败", f"保存文件时出错: {e}")
                print(f"应用错误: 保存文件 '{original_filename}' 到 '{dest_path_suggestion}': {e}")


    def delete_selected_file_from_gui(self): # 从GUI删除选中的文件
        global filepaths
        selected_indices = self.files_listbox.curselection() # 获取选中项
        if not selected_indices:
            messagebox.showwarning("删除文件", "请先在列表中选择一个文件。")
            return

        selected_index = selected_indices[0]
        # 列表框基于排序后的 filepaths 显示
        sorted_items_for_display = sorted(filepaths, key=lambda x: x['name'].lower())

        if selected_index >= len(sorted_items_for_display): # 检查索引有效性
            messagebox.showerror("错误", "选择索引无效，列表可能已更改。")
            self.showUploadedFile() 
            return

        item_to_delete_view = sorted_items_for_display[selected_index] # 获取选中项的视图信息
        # 从全局 filepaths 中找到实际的项
        actual_item_to_delete = next((item for item in filepaths if item['path'] == item_to_delete_view['path']), None)

        if not actual_item_to_delete: # 如果未找到
            messagebox.showerror("错误", "无法在内部列表中找到要删除的文件。请刷新。")
            self.showUploadedFile(); return

        path_to_delete_on_disk = actual_item_to_delete['path'] # 要删除的磁盘路径
        file_name_to_delete = actual_item_to_delete['name'] # 要删除的文件名

        # 确认删除操作
        if not messagebox.askyesno("确认删除", f"确定要从磁盘和分享列表中删除 '{file_name_to_delete}' 吗？\n此操作无法撤销。"):
            return

        try:
            if os.path.exists(path_to_delete_on_disk): # 如果文件在磁盘上存在
                os.remove(path_to_delete_on_disk) # 从磁盘删除
                print(f"应用: 已通过GUI从 '{path_to_delete_on_disk}' 删除 '{file_name_to_delete}'。")
            else:
                print(f"应用: 文件 '{path_to_delete_on_disk}' 在磁盘上未找到但仍在列表中 (可能已被删除?)。")
            
            filepaths.remove(actual_item_to_delete) # 从全局列表移除
            
            self.showUploadedFile() # 刷新列表
            self.status_label.configure(text=f"文件 '{file_name_to_delete}' 已删除", fg=COLORS["text_light"])

        except Exception as e:
            messagebox.showerror("删除失败", f"删除文件 '{file_name_to_delete}' 时出错: {e}")
            print(f"应用错误: 删除 {file_name_to_delete}: {e}")
            self.showUploadedFile() # 刷新以处理部分失败或状态不匹配

    def toggle_server_state(self): # 切换服务器启动/停止状态
        if self.is_server_running: self.stop_http_server()
        else: self.start_http_server()

    def start_http_server(self): # 启动HTTP服务器
        global filepaths
        if not filepaths: # 检查是否有文件可分享
            self.status_label.configure(text="服务器: 请先选择或上传文件!", fg=COLORS["warning"])
            if self.master.winfo_exists(): self.flash_button(self.upload_button, BUTTON_STYLE["secondary"]["activebackground"], BUTTON_STYLE["secondary"]["bg"])
            return

        if self.is_server_running: # 如果服务器已在运行
            self.status_label.configure(text="服务器: 运行中", fg=COLORS["success"])
            return

        if self.master.winfo_exists(): # 更新GUI状态为启动中
            self.status_label.configure(text="服务器: 启动中...", fg=COLORS["accent"])
            self.serve_button.configure(text="启动中...", state=DISABLED); self.master.update_idletasks()

        try:
            self.ip_addr_str = get_ip_addr(); self.url = f"http://{self.ip_addr_str}:{self.port}" # 更新URL
            if not os.path.exists(UPLOAD_FOLDER): # 确保上传文件夹存在
                os.makedirs(UPLOAD_FOLDER)

            # 创建并启动HTTP服务器实例
            self.httpd_server_instance = HTTPServer((self.ip_addr_str, self.port), MyHandler)
            self.httpd_server_instance.allow_reuse_address = True # 允许地址重用
            self.http_server_thread = Thread(target=self._server_thread_target, daemon=True, name="HTTPServerThread")
            self.http_server_thread.start() # 启动服务器线程
            self.is_server_running = True
            if self.master.winfo_exists(): self.master.after(100, self._update_gui_after_server_start_success) # 稍后更新GUI
        except OSError as e: # 捕获端口占用等OS错误
            self.is_server_running = False; self.httpd_server_instance = None; error_message = f"启动失败: {e.strerror}"
            if e.errno in [98, 48, 10048, 10013]: error_message = f"端口 {self.port} 已被占用或无权限。"
            if self.master.winfo_exists():
                self.status_label.configure(text=f"服务器: {error_message}", fg=COLORS["error"])
                self.serve_button.configure(text="开始分享", state=NORMAL, **{k:v for k,v in BUTTON_STYLE["primary"].items() if k!='font'})
        except Exception as e: # 捕获其他启动错误
            self.is_server_running = False; self.httpd_server_instance = None
            if self.master.winfo_exists():
                self.status_label.configure(text=f"服务器: 启动失败 - {type(e).__name__}", fg=COLORS["error"])
                self.serve_button.configure(text="开始分享", state=NORMAL, **{k:v for k,v in BUTTON_STYLE["primary"].items() if k!='font'})


    def _update_gui_after_server_start_success(self): # 服务器成功启动后更新GUI
        if not self.master.winfo_exists() or not self.is_server_running: return
        self.status_label.configure(text="服务器: 运行中", fg=COLORS["success"])
        self.url_display_label.configure(state="normal", fg=COLORS["primary"]) # 使URL可编辑以更新内容
        self.url_display_label.delete(0, END); self.url_display_label.insert(0, self.url)
        self.url_display_label.configure(state="readonly") # 设回只读
        self.serve_button.configure(text="停止分享", state=NORMAL, **{k:v for k,v in BUTTON_STYLE["danger"].items() if k!='font'}) # 更新按钮样式为停止
        self.copy_url_button.configure(state=NORMAL) # 启用复制按钮

    def _server_thread_target(self): # 服务器线程的执行目标
        if not self.httpd_server_instance: return
        try:
            print(f"应用: HTTP 服务器线程已启动，服务于 {self.url}")
            self.httpd_server_instance.serve_forever() # 阻塞直到 shutdown() 被调用
            print("应用: HTTP 服务器线程 serve_forever() 已返回。") # 正常情况下在 shutdown 后发生
        except Exception as e:
            if self.is_server_running: # 仅在非预期停止时记录错误
                print(f"应用错误: HTTP 服务器线程中发生异常: {e}")
        finally:
            # 此块在 serve_forever() 退出后运行
            if self.httpd_server_instance:
                try:
                    self.httpd_server_instance.server_close() # 关闭服务器套接字
                    print("应用: HTTP server_close() 已调用。")
                except Exception as e_close:
                    print(f"应用错误: server_close 期间发生异常: {e_close}")
                self.httpd_server_instance = None # 清理实例

            # 在主线程上安排 GUI 更新
            if self.master.winfo_exists():
                self.master.after_idle(self._update_gui_after_server_stop)
            else: # 如果GUI已不存在
                self.is_server_running = False


    def stop_http_server(self): # 停止HTTP服务器
        if not self.is_server_running or not self.httpd_server_instance: # 如果服务器未运行或实例不存在
            if self.master.winfo_exists(): self._update_gui_after_server_stop() # 更新GUI状态
            return

        if self.master.winfo_exists(): # 更新GUI为停止中状态
            self.status_label.configure(text="服务器: 停止中...", fg=COLORS["accent"])
            self.serve_button.configure(state=DISABLED); self.master.update_idletasks()

        # 在新线程中启动关闭以防止 GUI 冻结
        Thread(target=self._execute_shutdown_safely, daemon=True, name="ShutdownThread").start()

    def _execute_shutdown_safely(self): # 安全地执行服务器关闭
        if self.httpd_server_instance:
            try:
                print("应用: 正在调用 httpd_server_instance.shutdown()...")
                self.httpd_server_instance.shutdown() # 这会使 serve_forever() 停止
                print("应用: httpd_server_instance.shutdown() 已返回。")
            except Exception as e:
                print(f"应用错误: httpd_server_instance.shutdown 期间发生异常: {e}")
        # _server_thread_target 的 finally 块将处理 server_close 和 GUI 更新

    def _update_gui_after_server_stop(self): # 服务器停止后更新GUI
        self.is_server_running = False
        if self.master.winfo_exists(): # 如果GUI存在
            self.status_label.configure(text="服务器: 已停止", fg=COLORS["text_light"])
            self.serve_button.configure(text="开始分享", state=NORMAL, **{k:v for k,v in BUTTON_STYLE["primary"].items() if k!='font'}) # 恢复启动按钮样式
            self.url_display_label.configure(state="normal"); self.url_display_label.delete(0, END)
            self.url_display_label.insert(0, "服务器未运行或URL无效") # 占位符文本
            self.url_display_label.configure(state="readonly", fg=COLORS["text_light"])
            self.copy_url_button.configure(state=DISABLED) # 禁用复制按钮
            print("应用: 服务器停止后GUI已更新。")
        else:
            print("应用: 服务器已停止，但GUI不再存在。")


    def flash_button(self, button, color1, color2, count=2): # 按钮闪烁效果
        if not self.master.winfo_exists() or not button.winfo_exists(): return # 检查窗口和按钮是否存在
        if count <= 0 : # 闪烁结束
            if button.winfo_exists(): button.config(bg=color2); return
        try:
            button.config(bg=color1) # 改变颜色
            self.master.after(150, lambda: button.config(bg=color2) if button.winfo_exists() else None) # 稍后恢复颜色
            self.master.after(300, lambda: self.flash_button(button, color1, color2, count-1) if button.winfo_exists() else None) # 递归调用以继续闪烁
        except TclError: pass # 捕获Tcl错误（例如窗口已销毁）

    def copy_url_to_clipboard(self): # 复制URL到剪贴板
        url_to_copy = self.url_display_label.get() # 获取URL输入框内容
        if url_to_copy and "未运行" not in url_to_copy : # 检查是否为有效URL
            try:
                self.master.clipboard_clear(); self.master.clipboard_append(url_to_copy) # 清空并追加到剪贴板
                original_text = self.copy_url_button.cget("text") # 保存按钮原始文本
                # 获取按钮原始颜色（从样式字典中获取以确保一致性）
                btn_orig_bg = BUTTON_STYLE["secondary"]["bg"] 
                btn_hover_bg = BUTTON_STYLE["secondary"]["activebackground"]
                btn_orig_fg = BUTTON_STYLE["secondary"]["fg"]
                # btn_hover_fg = BUTTON_STYLE["secondary"]["activeforeground"] # 如果需要，可以添加悬停前景色的逻辑

                # 改变按钮外观表示已复制
                self.copy_url_button.config(text="已复制!", bg=COLORS["success"], activebackground=COLORS["success_dark"], fg=COLORS["white"], activeforeground=COLORS["white"])
                if self.copy_url_button.winfo_exists(): # 确保按钮仍然存在
                    # 1.5秒后恢复按钮原始外观
                    self.master.after(1500, lambda:
                        self.copy_url_button.config(text=original_text, bg=btn_orig_bg, activebackground=btn_hover_bg, fg=btn_orig_fg, activeforeground=btn_orig_fg) # 使用原始颜色
                        if self.copy_url_button.winfo_exists() else None )
            except Exception as e:
                print(f"应用错误: 剪贴板复制: {e}")
                messagebox.showerror("复制失败", f"无法复制到剪贴板: {e}")

    def on_closing(self): # 处理窗口关闭事件
        print("应用: 正在关闭应用程序...")
        if self.is_server_running: # 如果服务器正在运行
            print("应用: 服务器正在运行，尝试停止它。")
            self.stop_http_server() # 停止服务器
            if self.http_server_thread and self.http_server_thread.is_alive(): # 等待服务器线程结束
                print("应用: 等待服务器线程加入 (最多0.5秒)...")
                self.http_server_thread.join(timeout=0.5) # 短暂等待
                if self.http_server_thread.is_alive():
                    print("应用警告: 服务器线程未完全关闭。")
        
        if self.master.winfo_exists(): # 如果主窗口存在
            self.master.destroy() # 销毁主窗口
        print("应用: 应用程序已关闭。")

# 全局 filepaths 现在是字典列表: [{'path': str, 'name': str, 'size_str': str, 'source': str}]
filepaths = []
app_instance = None # 全局应用实例

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER): # 程序启动时检查上传文件夹
        try:
            os.makedirs(UPLOAD_FOLDER)
            print(f"主程序: 已在 '{os.path.abspath(UPLOAD_FOLDER)}' 创建 UPLOAD_FOLDER")
        except OSError as e:
            print(f"主程序警告: 无法创建上传文件夹 '{UPLOAD_FOLDER}': {e}")

    root = Tk() # 创建Tkinter根窗口
    app_instance = App(root) # 创建应用实例
    root.protocol("WM_DELETE_WINDOW", app_instance.on_closing) # 绑定窗口关闭事件
    root.mainloop() # 进入Tkinter事件循环