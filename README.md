# 📁 本地文件分享应用

这是一个使用 Tkinter 构建 GUI，并使用 `http.server` 作为 Web 服务器的简单 Python 应用程序。  
它允许您通过 Web 浏览器在同一局域网（WiFi 或以太网）中轻松分享本地文件。

---

## ✨ 功能亮点

- 🖼️ **GUI 界面：** 简洁直观的 Tkinter 窗口，轻松启动/停止服务器
- 📤 **文件分享：** 分享您通过 GUI 选择的文件
- 🌐 **Web 上传：** 可直接从浏览器上传文件到服务器
- 📥 **Web 下载：** 在浏览器中访问和下载共享文件
- ❌ **Web 删除：** 在浏览器中一键删除共享文件
- 🔍 **自动 IP 检测：** 自动显示本机在局域网中的访问地址
- 🎨 **现代样式：** 简洁美观的网页前端界面

---

## 🧰 要求

- 🐍 Python 3.6 或更高版本
- 🧱 Tkinter（Python 默认自带）

---

## 🚀 安装步骤

1. 📥 克隆或下载本仓库
2. 📂 打开终端并切换至项目目录：

    ```bash
    cd /path/to/your/project
    ```

3. ▶️ 运行主脚本：

    ```bash
    python main.py
    ```

---

## 🧑‍💻 使用方法

1. 运行 `main.py` 启动程序  
2. 弹出 Tkinter GUI 窗口  
3. 点击 **“选择文件”** 添加您想分享的文件  
4. 点击 **“开始分享”** 启动 HTTP 服务  
5. 程序会显示访问地址（如 `http://192.168.1.100:8000`）  
6. 在局域网内任一设备的浏览器中输入该地址  
7. 🌐 浏览共享文件列表，点击下载或使用按钮上传/删除文件  
8. 点击 **“停止分享”** 可关闭服务器

---

## 🗃️ 项目版本

本项目包含两个主要版本：

1. 🧾 **非 MVC 版本 (`1st-NON/`)**  
   > 所有逻辑集中在一个脚本中，便于快速理解和运行

2. 🧱 **MVC 版本 (`2th-MVC/`)**  
   > 遵循 Model-View-Controller 架构，结构清晰，易于扩展和维护

---

## 📁 项目结构

````

.
├── 1st-NON/
│   ├── main.py
│   └── uploads/
├── 2th-MVC/
│   ├── app\_controller.py
│   ├── app\_view\.py
│   ├── config.py
│   ├── file\_model.py
│   ├── http\_handler.py
│   ├── ip\_utils.py
│   ├── main.py
│   ├── styles.py
│   └── uploads/
├── README.md
└── README\_en.md

````

---

## ⚙️ 配置说明

- 📂 上传目录默认设置为 `uploads/`  
- 如需修改，请在 `config.py` 中设置：

    ```python
    UPLOAD_FOLDER = "uploads"
    ```

---

## 🙌 贡献方式

欢迎 🙌 Fork 本项目并提交 Pull Request  
也欢迎通过 Issues 提出建议或报告 Bug 🐛

---

## 📄 许可证

本项目采用 **MIT License** 开源授权。  
详情请参见根目录下的 `LICENSE` 文件。  
> 📝 *如果尚未添加 LICENSE 文件，请及时补充以完善开源合规性。*

---

## 🖼️ 项目效果图

> 以下是本地文件分享应用运行界面与 Web 文件管理界面的实际效果截图：

### 🎛️ GUI 界面（Tkinter）

![GUI界面截图](./assets/gui_example.png)

### 🌐 Web 界面（文件列表 + 上传/删除）

![Web界面截图](./assets/web_example.png)

---

