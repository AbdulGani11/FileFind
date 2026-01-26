# ⚡ File Commander

[![CI](https://github.com/AbdulGani11/file-commander/actions/workflows/ci.yml/badge.svg)](https://github.com/AbdulGani11/file-commander/actions)
![Platform Windows](https://img.shields.io/badge/platform-Windows-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Smart operations made simple.** A fast, offline tool for Windows that helps you find and manage files instantly. It runs in your terminal but looks and feels like a professional app.

---

## 🚀 Key Features

*   **⚡ Instant Search**: Finds files immediately, no matter how many you have. It uses advanced **Trie technology** (Prefix Trees) to search as fast as you type.
*   **🎨 Modern Design**: A clean, easy-to-read interface with colors, icons, and tables. No messy text blocks.
*   **🛡️ Safe & Secure**: Automatically blocks unsafe file names to protect your computer from errors.
*   **🧠 Smart Memory**: Scans your folders once and remembers them. You can search again and again without waiting.
*   **🧪 Reliable**: Tested automatically on every change to ensure it never breaks.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AbdulGani11/file-commander.git
    cd file-commander
    ```

2.  **Set up environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🖥️ Usage

Run the app:
```bash
python file-commander.py
```

### 📋 What can it do?
The menu is controlled by your keyboard:
1.  **📁 Create**: Make new files and folders easily.
2.  **⚡ Search**: Find any file instantly (you can open or rename them too).
3.  **📋 List**: See what is inside your folders.
4.  **⚙️ Stats**: Check how many files are indexed.

## 🧪 Development & Testing

This project is built with high standards.

**Run Tests:**
```bash
# Check if everything works
pytest
```

**Auto-Checks (CI):**
Every time we update the code, GitHub automatically runs tests on Python 3.10, 3.11, and 3.12 to make sure it works for everyone.

## 🔧 Technical Details (For Developers)

*   **Language**: Python 3.10+ (with Type Hints)
*   **Data Structure**: Prefix Trie & Inverted Index
*   **UI Library**: Rich
*   **Testing**: Pytest & GitHub Actions

## 📜 License

MIT License © 2025 Abdul Gani
