# 📁 Local File Sharing App

This is a simple Python application that uses Tkinter to build a GUI and `http.server` as a web server.  
It allows you to easily share local files over the same local network (WiFi or Ethernet) via a web browser.

---

## ✨ Features

- 🖼️ **GUI Interface:** A clean and intuitive Tkinter window to start/stop the server
- 📤 **File Sharing:** Share files selected through the GUI
- 🌐 **Web Upload:** Upload files directly to the server from the browser
- 📥 **Web Download:** Access and download shared files via the browser
- ❌ **Web Delete:** Easily delete shared files from the browser interface
- 🔍 **Auto IP Detection:** Automatically detects and displays your local IP address
- 🎨 **Modern Style:** Basic modern web UI for user-friendly interaction

---

## 🧰 Requirements

- 🐍 Python 3.6 or higher
- 🧱 Tkinter (usually bundled with Python)

---

## 🚀 Installation

1. 📥 Clone or download this repository
2. 📂 Open your terminal and navigate to the project directory:

    ```bash
    cd /path/to/your/project
    ```

3. ▶️ Run the main script:

    ```bash
    python main.py
    ```

---

## 🧑‍💻 How to Use

1. Run `main.py` to start the application  
2. A Tkinter GUI window will appear  
3. Click **"Choose File"** to select files you want to share  
4. Click **"Start Sharing"** to launch the HTTP server  
5. The application will display your access URL (e.g., `http://192.168.1.100:8000`)  
6. On any device connected to the same local network, open a web browser and enter the displayed address  
7. 🌐 View the shared file list, download files, or upload/delete using the buttons provided  
8. Click **"Stop Sharing"** in the GUI to shut down the server

---

## 🗃️ Project Versions

This project includes two main versions:

1. 🧾 **Non-MVC Version (`1st-NON/`)**  
   > A simple implementation with all logic in a single script for easy understanding and quick usage

2. 🧱 **MVC Version (`2th-MVC/`)**  
   > A structured implementation using the Model-View-Controller pattern, making the code more organized and maintainable

---

## 📁 Project Structure

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

## ⚙️ Configuration

- 📂 The default upload directory is `uploads/`  
- You can change it in `config.py`:

    ```python
    UPLOAD_FOLDER = "uploads"
    ```

---

## 🙌 Contributing

Contributions are welcome! 🙌  
Feel free to fork this repository and submit pull requests.  
Suggestions and bug reports are also appreciated via Issues 🐛

---

## 📄 License

This project is licensed under the **MIT License**.  
See the `LICENSE` file in the root directory for details.

---

## 🖼️ Screenshots

> Below are sample screenshots showing the local file sharing app interface and web management UI:

### 🎛️ GUI (Tkinter)

![GUI Screenshot](./assets/gui_example.png)

### 🌐 Web Interface (File List + Upload/Delete)

![Web UI Screenshot](./assets/web_example.png)

---
