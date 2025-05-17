# app_controller.py
import os
import shutil
import time
from threading import Thread
from http.server import HTTPServer
from functools import partial # 用于传递 controller 给 HTTP Handler

from file_model import FileModel # 导入模型
from app_view import AppView     # 导入视图类
from http_handler import FileShareHTTPRequestHandler # 导入HTTP处理器
from ip_utils import get_ip_addr # 导入IP工具
from config import DEFAULT_PORT, FILE_SOURCE_GUI, FILE_SOURCE_BROWSER, UPLOAD_FOLDER # 导入配置

class AppController:
    def __init__(self, model, view_class):
        self.model = model
        self.tk_root = None
        self.view = None

        self.ip_addr_str = get_ip_addr()
        self.port = DEFAULT_PORT
        self.url = f"http://{self.ip_addr_str}:{self.port}"
        
        self.http_server_thread = None
        self.httpd_server_instance = None
        self.is_server_running = False

    def set_tk_root(self, root):
        self.tk_root = root
        self.view = AppView(root, self) # 初始化视图
        self.refresh_view_file_list()

    def refresh_view_file_list(self):
        if self.view and self.tk_root.winfo_exists():
            sorted_files = self.model.get_all_files_sorted()
            # 使用 after_idle 确保GUI更新在主线程
            self.tk_root.after_idle(self.view.update_file_list, sorted_files)

    def handle_gui_select_files(self):
        if not self.view: return
        
        self.model.clear_files_by_source(FILE_SOURCE_GUI)

        chosen_files_temp = self.view.ask_for_filenames(
            title="选择文件 (替换应用选择的文件, 保留浏览器上传的)",
            filetypes=[("所有文件", "*.*"), ("文本文档", "*.txt"), ("图片", "*.png *.jpg *.jpeg *.gif"), ("PDF", "*.pdf")]
        )
        
        if not chosen_files_temp:
            self.refresh_view_file_list()
            self.view.update_status_label("服务器: 应用选择的文件已清空")
            return

        new_gui_files_added_count = 0
        for f_path_str in chosen_files_temp:
            add_result = self.model.add_file(f_path_str, FILE_SOURCE_GUI)
            if add_result == "exists":
                 self.view.show_message("跳过文件", f"文件 '{os.path.basename(f_path_str)}' 已在列表中 (可能由浏览器上传)，因此未重新添加。", type="info")
            elif add_result:
                new_gui_files_added_count += 1
            else:
                self.view.show_message("文件错误", f"处理文件 '{os.path.basename(f_path_str)}' 时出错。", type="error")

        self.refresh_view_file_list()

        if new_gui_files_added_count > 0:
            status_msg = "服务器: 待启动 (文件已更新)" if not self.is_server_running else "服务器: 运行中 (列表已更新)"
            status_fg = "text" if not self.is_server_running else "success"
            self.view.update_status_label(status_msg, status_fg)
            if not self.is_server_running and self.tk_root.winfo_exists():
                self.view.flash_button_visual(self.view.server_toggle_button, "accent_light", "primary")

    def handle_gui_save_selected_as(self):
        if not self.view: return
        selected_idx = self.view.get_selected_listbox_index()
        if selected_idx is None:
            self.view.show_message("另存为", "请先在列表中选择一个文件。", type="warning")
            return

        sorted_files = self.model.get_all_files_sorted()
        if selected_idx >= len(sorted_files):
            self.view.show_message("错误", "选择索引无效。列表可能已更改。", type="error")
            self.refresh_view_file_list()
            return
        
        item_to_save = sorted_files[selected_idx]
        source_path = item_to_save['path']
        original_filename = item_to_save['name']

        if not os.path.exists(source_path):
            self.view.show_message("错误", f"源文件 '{original_filename}' 不存在，无法另存为。", type="error")
            self.model.remove_item_if_not_exists_on_disk(item_to_save)
            self.refresh_view_file_list()
            return

        dest_path_suggestion = self.view.ask_for_save_as_filename(
            initial_file=original_filename,
            title="选择保存位置...",
            default_ext=os.path.splitext(original_filename)[1] or ".file",
            filetypes=[("所有文件", "*.*")]
        )

        if dest_path_suggestion:
            try:
                shutil.copy2(source_path, dest_path_suggestion)
                self.view.show_message("成功", f"文件 '{original_filename}' 已保存到 '{os.path.basename(dest_path_suggestion)}'.")
            except Exception as e:
                self.view.show_message("保存失败", f"保存文件时出错: {e}", type="error")
                print(f"Controller Error: 保存文件 '{original_filename}' 到 '{dest_path_suggestion}': {e}")

    def handle_gui_delete_selected(self):
        if not self.view: return
        selected_idx = self.view.get_selected_listbox_index()
        if selected_idx is None:
            self.view.show_message("删除文件", "请先在列表中选择一个文件。", type="warning")
            return

        sorted_files = self.model.get_all_files_sorted()
        if selected_idx >= len(sorted_files):
            self.view.show_message("错误", "选择索引无效，列表可能已更改。", type="error")
            self.refresh_view_file_list()
            return
        
        item_to_delete = sorted_files[selected_idx]
        path_to_delete_on_disk = item_to_delete['path']
        file_name_to_delete = item_to_delete['name']

        if not self.view.ask_yes_no("确认删除", f"确定要从磁盘和分享列表中删除 '{file_name_to_delete}' 吗？\n此操作无法撤销。"):
            return

        delete_from_disk_flag = True 
        status = self.model.remove_file_by_path(path_to_delete_on_disk, delete_from_disk=delete_from_disk_flag)
        
        if status == "removed":
            self.view.update_status_label(f"文件 '{file_name_to_delete}' 已删除。", "text_light")
        elif status == "disk_delete_failed":
             self.view.show_message("删除部分失败", f"已从列表移除 '{file_name_to_delete}'，但从磁盘删除失败。", "warning")
        elif status == "not_found":
             self.view.show_message("错误", f"文件 '{file_name_to_delete}' 在列表中未找到。", "error")
        else:
             self.view.show_message("删除失败", f"删除 '{file_name_to_delete}' 时发生错误。", "error")

        self.refresh_view_file_list()

    def handle_toggle_server(self):
        if self.is_server_running:
            self._stop_http_server()
        else:
            self._start_http_server()

    def _start_http_server(self):
        if not self.model.get_all_files_sorted():
            if self.view: self.view.update_status_label("服务器: 请先选择或上传文件!", "warning")
            if self.view and self.tk_root.winfo_exists():
                self.view.flash_button_visual(self.view.select_files_button, "accent_light", "secondary")
            return

        if self.is_server_running:
            if self.view: self.view.update_status_label("服务器: 已在运行", "success")
            return

        if self.view: self.view.update_server_starting_gui()

        try:
            self.ip_addr_str = get_ip_addr()
            self.url = f"http://{self.ip_addr_str}:{self.port}"
            self.model._ensure_upload_folder_exists()

            handler_with_controller = partial(FileShareHTTPRequestHandler, controller=self)
            self.httpd_server_instance = HTTPServer((self.ip_addr_str, self.port), handler_with_controller)
            self.httpd_server_instance.allow_reuse_address = True
            
            self.http_server_thread = Thread(target=self._server_thread_target, daemon=True, name="HTTPServerThread")
            self.http_server_thread.start()
            self.is_server_running = True
            
            if self.view and self.tk_root.winfo_exists():
                 self.tk_root.after(100, lambda: self.view.update_server_running_gui(self.url) if self.is_server_running else None)

        except OSError as e:
            self.is_server_running = False; self.httpd_server_instance = None
            error_message = f"启动失败: {e.strerror}"
            if e.errno in [98, 48, 10048, 10013]: error_message = f"端口 {self.port} 已被占用或无权限。"
            if self.view: 
                self.view.update_status_label(f"服务器: {error_message}", "error")
                self.view.update_server_stopped_gui()
        except Exception as e:
            self.is_server_running = False; self.httpd_server_instance = None
            if self.view:
                self.view.update_status_label(f"服务器: 启动失败 - {type(e).__name__}", "error")
                self.view.update_server_stopped_gui()

    def _server_thread_target(self):
        if not self.httpd_server_instance: return
        try:
            print(f"Controller: HTTP 服务器线程已启动，服务于 {self.url}")
            self.httpd_server_instance.serve_forever()
            print("Controller: HTTP 服务器线程 serve_forever() 已返回。")
        except Exception as e:
            if self.is_server_running:
                print(f"Controller Error: HTTP 服务器线程中发生异常: {e}")
        finally:
            if self.httpd_server_instance:
                try: self.httpd_server_instance.server_close(); print("Controller: HTTP server_close() 已调用。")
                except Exception as e_close: print(f"Controller Error: server_close 期间发生异常: {e_close}")
                self.httpd_server_instance = None
            
            if self.view and self.tk_root and self.tk_root.winfo_exists():
                self.tk_root.after_idle(self._update_gui_after_server_fully_stopped)
            else:
                self.is_server_running = False

    def _stop_http_server(self):
        if not self.is_server_running or not self.httpd_server_instance:
            if self.view: self._update_gui_after_server_fully_stopped()
            return

        if self.view: self.view.update_server_stopping_gui()
        Thread(target=self._execute_shutdown_safely, daemon=True, name="ShutdownThread").start()

    def _execute_shutdown_safely(self):
        if self.httpd_server_instance:
            try:
                print("Controller: 正在调用 httpd_server_instance.shutdown()...")
                self.httpd_server_instance.shutdown()
                print("Controller: httpd_server_instance.shutdown() 已返回。")
            except Exception as e:
                print(f"Controller Error: httpd_server_instance.shutdown 期间发生异常: {e}")

    def _update_gui_after_server_fully_stopped(self):
        self.is_server_running = False
        if self.view and self.tk_root.winfo_exists():
            self.view.update_server_stopped_gui()
            print("Controller: 服务器停止后GUI已更新。")
        else:
            print("Controller: 服务器已停止，但GUI不再存在。")

    def handle_copy_url(self):
        if not self.view or not self.is_server_running: return
        self.view.copy_to_clipboard(self.url)

    def handle_window_close(self):
        print("Controller: 正在关闭应用程序...")
        if self.is_server_running:
            print("Controller: 服务器正在运行，尝试停止它。")
            self._stop_http_server() 
            if self.http_server_thread and self.http_server_thread.is_alive():
                print("Controller: 等待服务器线程加入 (最多0.5秒)...")
                self.http_server_thread.join(timeout=0.5)
                if self.http_server_thread.is_alive():
                    print("Controller 警告: 服务器线程未完全关闭。")
        
        if self.tk_root and self.tk_root.winfo_exists():
            self.tk_root.destroy()
        print("Controller: 应用程序已关闭。")

    def get_sorted_files_for_display(self):
        return self.model.get_all_files_sorted()

    def get_file_info_by_name(self, name):
        return self.model.get_file_by_name(name)

    def handle_file_not_found_on_disk(self, item_dict):
        removed = self.model.remove_item_if_not_exists_on_disk(item_dict)
        if removed:
            self.refresh_view_file_list()

    def handle_browser_upload(self, cgi_file_item):
        original_filename = os.path.basename(cgi_file_item.filename)
        filename_sanitized = "".join(c for c in original_filename if c.isalnum() or c in ['.', '_', '-'])
        if not filename_sanitized: filename_sanitized = f"uploaded_file_{int(time.time())}"

        save_path_candidate = os.path.join(UPLOAD_FOLDER, filename_sanitized)
        
        counter = 1
        actual_filename_to_save = filename_sanitized
        final_save_path = save_path_candidate
        original_filename_stem, original_filename_ext = os.path.splitext(filename_sanitized)
        while os.path.exists(final_save_path):
            actual_filename_to_save = f"{original_filename_stem}_{counter}{original_filename_ext}"
            final_save_path = os.path.join(UPLOAD_FOLDER, actual_filename_to_save)
            counter += 1
        
        try:
            with open(final_save_path, 'wb') as f_out:
                shutil.copyfileobj(cgi_file_item.file, f_out)
            
            add_status = self.model.add_file(final_save_path, FILE_SOURCE_BROWSER)
            if add_status and add_status != "exists":
                self.refresh_view_file_list()
                return final_save_path
            elif add_status == "exists":
                print(f"Controller: 上传的文件 {final_save_path} 模型已知。")
                self.refresh_view_file_list()
                return final_save_path
            else:
                if os.path.exists(final_save_path): os.remove(final_save_path)
                return None
        except Exception as e:
            print(f"Controller Error: 无法保存上传的文件 {original_filename} 为 {actual_filename_to_save}: {e}")
            if os.path.exists(final_save_path): os.remove(final_save_path) # 清理
            return None

    def handle_browser_delete(self, filename_to_delete):
        item_info = self.model.get_file_by_name(filename_to_delete)
        if not item_info:
            return "not_found"

        path_to_delete = item_info['path']
        delete_from_disk = True 
        status = self.model.remove_file_by_path(path_to_delete, delete_from_disk=delete_from_disk)
        
        if status == "removed" or status == "disk_delete_failed":
            self.refresh_view_file_list()
        return status