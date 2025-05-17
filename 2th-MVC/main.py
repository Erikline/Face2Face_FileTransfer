# main.py
import tkinter as tk
from file_model import FileModel
from app_controller import AppController
# AppView 类会被 AppController 内部导入和实例化，所以这里不需要直接导入 AppView
# from app_view import AppView 

if __name__ == '__main__':
    # 1. 创建模型
    file_model_instance = FileModel()

    # 2. 创建控制器 (并将模型和视图类传递给它)
    #    视图类 (AppView) 会在控制器内部根据Tk根窗口实例化
    app_controller_instance = AppController(model=file_model_instance, view_class=None) # view_class 参数现在由控制器内部处理

    # 3. 创建Tkinter根窗口
    root = tk.Tk()
    
    # 4. 在控制器中设置Tk根窗口，控制器将在此之后初始化视图
    app_controller_instance.set_tk_root(root)

    # 5. 启动Tkinter事件循环
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("应用程序被中断。正在关闭...")
        if app_controller_instance:
            app_controller_instance.handle_window_close()