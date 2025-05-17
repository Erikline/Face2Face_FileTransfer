# file_model.py
import os
from config import UPLOAD_FOLDER # 从config导入常量

class FileModel:
    def __init__(self):
        self.filepaths_data = []
        self._ensure_upload_folder_exists()

    def _ensure_upload_folder_exists(self):
        if not os.path.exists(UPLOAD_FOLDER):
            try:
                os.makedirs(UPLOAD_FOLDER)
                print(f"Model: 已在 '{os.path.abspath(UPLOAD_FOLDER)}' 创建 UPLOAD_FOLDER")
            except OSError as e:
                print(f"Model Error: 无法创建上传文件夹 '{UPLOAD_FOLDER}': {e}")
                raise

    def format_file_size(self, size_bytes):
        if size_bytes is None: return "未知大小"
        try: size_bytes = int(size_bytes)
        except (ValueError, TypeError): return "无效大小"
        if size_bytes < 0: return "无效大小";
        if size_bytes == 0: return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]; i = 0
        while size_bytes >= 1024 and i < len(units) - 1: size_bytes /= 1024.0; i += 1
        return f"{size_bytes:.1f} {units[i]}"

    def add_file(self, path, source):
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"Model: 文件 {abs_path} 未找到, 无法添加。")
            return None

        if any(item['path'] == abs_path for item in self.filepaths_data):
            print(f"Model: 文件 {abs_path} 已在列表中。")
            return "exists"

        try:
            file_size = os.path.getsize(abs_path)
            file_name = os.path.basename(abs_path)
            new_file_item = {
                'path': abs_path,
                'name': file_name,
                'size_str': self.format_file_size(file_size),
                'source': source
            }
            self.filepaths_data.append(new_file_item)
            print(f"Model: 已添加文件 '{file_name}' (来源: '{source}')。")
            return new_file_item
        except Exception as e:
            print(f"Model Error: 处理文件 {abs_path} 失败: {e}")
            return None

    def remove_file_by_path(self, path_to_remove, delete_from_disk=False):
        abs_path_to_remove = os.path.abspath(path_to_remove)
        item_removed = None

        for item in list(self.filepaths_data):
            if item['path'] == abs_path_to_remove:
                try:
                    self.filepaths_data.remove(item)
                    item_removed = item
                    print(f"Model: 已从列表移除 '{item['name']}'。")
                    if delete_from_disk:
                        if os.path.exists(item['path']):
                            os.remove(item['path'])
                            print(f"Model: 已从磁盘删除 '{item['name']}': {item['path']}")
                        else:
                            print(f"Model: 文件 '{item['name']}' 在磁盘上未找到: {item['path']}")
                    break
                except ValueError:
                    pass
                except OSError as e:
                    print(f"Model Error: 从磁盘删除文件 {item['path']} 失败: {e}")
                    if item_removed:
                         self.filepaths_data.append(item_removed)
                         return "disk_delete_failed"
                    return "error"

        if item_removed:
            return "removed"
        return "not_found"

    def remove_item_if_not_exists_on_disk(self, item_dict_to_check):
        path_to_check = item_dict_to_check.get('path')
        if not path_to_check or not os.path.exists(path_to_check):
            if item_dict_to_check in self.filepaths_data:
                try:
                    self.filepaths_data.remove(item_dict_to_check)
                    print(f"Model: 已通过标识移除不存在的文件 '{path_to_check}'。")
                    return True
                except ValueError:
                    pass
            for item in list(self.filepaths_data):
                if item['path'] == path_to_check and not os.path.exists(item['path']):
                    self.filepaths_data.remove(item)
                    print(f"Model: 已通过路径移除不存在的文件 '{path_to_check}'。")
                    return True
        return False

    def get_all_files_sorted(self):
        for item in list(self.filepaths_data):
            if not os.path.exists(item['path']):
                print(f"Model (get_all_files_sorted): 路径 {item['path']} 不再存在。正在移除。")
                try:
                    self.filepaths_data.remove(item)
                except ValueError: pass
        return sorted(self.filepaths_data, key=lambda x: x['name'].lower())

    def get_file_by_name(self, name):
        for item in self.filepaths_data:
            if item['name'].lower() == name.lower():
                if not os.path.exists(item['path']):
                    self.remove_item_if_not_exists_on_disk(item)
                    return None
                return item
        return None
    
    def clear_files_by_source(self, source):
        self.filepaths_data[:] = [item for item in self.filepaths_data if item['source'] != source]
        print(f"Model: 已清除来源为 '{source}' 的文件。")