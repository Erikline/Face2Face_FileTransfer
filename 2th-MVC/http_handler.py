# http_handler.py
from http.server import BaseHTTPRequestHandler
import os
import cgi
import shutil
import mimetypes
from urllib.parse import quote, unquote

# 导入样式和配置常量 (用于HTML模板)
from styles import COLORS, FONTS
from config import FILE_SOURCE_GUI, FILE_SOURCE_BROWSER

class FileShareHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, controller=None, **kwargs):
        self.controller = controller 
        super().__init__(*args, **kwargs)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _headers_sent_check(self):
         return hasattr(self, '_headers_buffer') and self._headers_buffer is not None and len(self._headers_buffer) > 0

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        try:
            decoded_path = unquote(self.path, encoding='utf-8', errors='replace')
            decoded_path = decoded_path.split('?', 1)[0].split('#', 1)[0]
        except Exception as e:
            print(f"HTTP Handler Error: 解码路径 '{self.path}' 失败: {e}")
            if not self._headers_sent_check(): self.send_error(400, "错误请求: 无效的URL路径格式")
            return

        if decoded_path == '/' or decoded_path == '':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            
            html_page_font_family = FONTS["body"][0] if "body" in FONTS and isinstance(FONTS["body"], tuple) and len(FONTS["body"]) > 0 else "sans-serif"
            # (此处省略了大部分HTML模板字符串以保持简洁，实际应包含完整的HTML)
            html_page_template_start = f"""
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
                .file-source-tag {{ font-size: 0.85em; color: {COLORS["text_light"]}; margin-left: 8px; font-style: italic; opacity: 0.8; }}
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
            self.wfile.write(html_page_template_start.encode('utf-8'))
            
            files_for_web = self.controller.get_sorted_files_for_display()

            if files_for_web:
                for item_data in files_for_web:
                    full_path = item_data['path']
                    display_file_name = item_data['name']
                    size_str = item_data['size_str']
                    source_tag_web = ""
                    if item_data['source'] == FILE_SOURCE_GUI: source_tag_web = "<span class='file-source-tag'>(来自应用)</span>"
                    elif item_data['source'] == FILE_SOURCE_BROWSER: source_tag_web = "<span class='file-source-tag'>(来自浏览器)</span>"

                    if not os.path.exists(full_path):
                        self.controller.handle_file_not_found_on_disk(item_data)
                        continue
                    
                    try:
                        encoded_link_fn = quote(display_file_name, safe='')
                        encoded_delete_fn_param = quote(display_file_name, safe='')
                        escaped_display_file_name = display_file_name.replace("'", "\\'").replace('"', '\\"')

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
                        self.wfile.write(item_html.encode('utf-8'))
                    except Exception as e_item:
                        self.wfile.write(f"<li>显示文件错误: {display_file_name} ({e_item})</li>".encode('utf-8'))
            else:
                self.wfile.write("<li class='no-files-message'>当前没有文件可供下载。请在应用程序中或通过上面的表单添加文件。</li>".encode('utf-8'))
            self.wfile.write("</ul><div class='footer'>通过本地WiFi网络分享的文件</div></div></body></html>".encode('utf-8'))
            return

        requested_file_name = os.path.basename(decoded_path)
        matched_item_dict = self.controller.get_file_info_by_name(requested_file_name)

        if matched_item_dict:
            matched_filepath = matched_item_dict['path']
            actual_display_name_for_header = matched_item_dict['name']

            if not os.path.exists(matched_filepath):
                if not self._headers_sent_check(): self.send_error(404, f"文件 '{actual_display_name_for_header}' 在服务器上未找到。")
                self.controller.handle_file_not_found_on_disk(matched_item_dict)
                return
            
            try:
                file_size = os.path.getsize(matched_filepath)
                content_type, _ = mimetypes.guess_type(matched_filepath)
                if content_type is None: content_type = "application/octet-stream"
                if content_type.startswith("text/"): content_type = f"{content_type}; charset=utf-8"

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self._send_cors_headers()

                encoded_fn_for_header_star = quote(actual_display_name_for_header, encoding='utf-8', safe='')
                safe_filename_for_header_equals = actual_display_name_for_header
                try: safe_filename_for_header_equals.encode('latin-1')
                except UnicodeEncodeError:
                    safe_filename_for_header_equals = "".join(c if ord(c) < 128 else '_' for c in os.path.splitext(actual_display_name_for_header)[0]) + os.path.splitext(actual_display_name_for_header)[1]
                    if not safe_filename_for_header_equals.strip("_-."): safe_filename_for_header_equals = "downloaded_file" + os.path.splitext(actual_display_name_for_header)[1]
                
                disposition_value = f'attachment; filename="{safe_filename_for_header_equals}"; filename*=UTF-8\'\'{encoded_fn_for_header_star}'
                self.send_header("Content-Disposition", disposition_value)
                self.send_header("Content-Length", str(file_size))
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache"); self.send_header("Expires", "0")
                self.end_headers()

                with open(matched_filepath, 'rb') as f:
                    shutil.copyfileobj(f, self.wfile)
                self.wfile.flush()
            except (ConnectionResetError, BrokenPipeError):
                print(f"HTTP Handler: 客户端在传输 {actual_display_name_for_header} 期间断开连接")
            except FileNotFoundError:
                if not self._headers_sent_check(): self.send_error(404, f"文件 '{actual_display_name_for_header}' 未找到 (竞争条件?)。")
            except Exception as e:
                print(f"HTTP Handler Error: 文件传输 {actual_display_name_for_header} 期间: {e}")
                if not self._headers_sent_check(): self.send_error(500, f"文件传输期间服务器错误: {e}")
            return
        else:
            if not self._headers_sent_check(): self.send_error(404, "未找到: 请求的文件未在服务器列表中找到。")
            return


    def do_POST(self):
        content_type_header = self.headers.get('Content-Type', '')
        content_length_header = self.headers.get('Content-Length')

        if not content_length_header:
            self.send_response(411); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self._send_cors_headers(); self.end_headers()
            self.wfile.write("错误请求: 需要 Content-Length 头部".encode('utf-8')); return
        try:
            content_length = int(content_length_header)
        except ValueError:
            self.send_response(400); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self._send_cors_headers(); self.end_headers()
            self.wfile.write("错误请求: Content-Length 无效".encode('utf-8')); return

        if 'multipart/form-data' not in content_type_header:
            self.send_response(400); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self._send_cors_headers(); self.end_headers()
            self.wfile.write("错误请求: 需要 multipart/form-data".encode('utf-8')); return
        
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': content_type_header,
                     'CONTENT_LENGTH': str(content_length)
                     },
            keep_blank_values=True
        )

        if self.path == '/upload':
            if 'files_to_upload' not in form:
                self.send_response(400); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self._send_cors_headers(); self.end_headers()
                self.wfile.write("在上传请求中未找到文件。".encode('utf-8')); return

            form_files = form['files_to_upload']
            if not isinstance(form_files, list): form_files = [form_files]

            for file_item in form_files:
                if file_item.filename:
                    self.controller.handle_browser_upload(file_item)
                else:
                    print("HTTP Handler: 收到一个没有文件名的文件项。")
            
            self.send_response(303); self.send_header('Location', '/'); self._send_cors_headers(); self.end_headers()

        elif self.path == '/delete':
            filename_to_delete_encoded = form.getvalue('filename_to_delete')
            if not filename_to_delete_encoded:
                self.send_response(400); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self._send_cors_headers(); self.end_headers()
                self.wfile.write("错误请求: 缺少 filename_to_delete 参数。".encode('utf-8')); return

            filename_to_delete = unquote(filename_to_delete_encoded)
            delete_status = self.controller.handle_browser_delete(filename_to_delete)

            if delete_status == "deleted":
                self.send_response(303); self.send_header('Location', '/'); self._send_cors_headers(); self.end_headers()
            elif delete_status == "not_found":
                self.send_response(404); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self._send_cors_headers(); self.end_headers()
                self.wfile.write("具有该名称的文件未在共享列表中找到。".encode('utf-8'))
            else: 
                self.send_response(500); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self._send_cors_headers(); self.end_headers()
                self.wfile.write("删除文件时出错。".encode('utf-8'))
        else:
            self.send_response(404); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self._send_cors_headers(); self.end_headers()
            self.wfile.write("未找到: 未知的POST端点。".encode('utf-8'))