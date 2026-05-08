# Auto Typer

A modern desktop automation utility built with Python and CustomTkinter that allows users to create keyword-based typing shortcuts for rapid text automation.

## Preview

Auto Typer Pro provides a sleek modern interface with:

* Real-time keyword detection
* Automated message typing
* Adjustable typing speed
* Multi-repeat support
* Dark / Light theme switching
* Keyboard shortcut controls
* Interactive shortcut management

---

# Features

## Core Features

* Keyword-triggered auto typing
* Adjustable typing delay
* Message repeat functionality
* Live typing automation
* ESC key emergency cancel
* Multi-shortcut support
* Thread-safe execution
* Instant shortcut testing

## User Interface

* Modern CustomTkinter UI
* Responsive desktop layout
* Professional dark theme
* Light mode support
* Tooltip system
* Animated cards and controls
* Real-time status indicators

## Productivity Tools

* Quick message templates
* Automated repetitive typing
* Hotkey support
* Shortcut preview cards
* Delete and manage shortcuts
* Typing speed customization

---

# Tech Stack

| Technology    | Purpose                   |
| ------------- | ------------------------- |
| Python        | Core application logic    |
| CustomTkinter | Modern desktop UI         |
| PyAutoGUI     | Keyboard automation       |
| Keyboard      | Global keyboard detection |
| Pillow (PIL)  | Image support             |
| Threading     | Background task handling  |

---

# Project Structure

```bash
AutoTyperPro/
│
├── auto_typer_pro.py
├── requirements.txt
├── README.md
└── assets/
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/auto-typer.git
cd auto-typer-pro
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install customtkinter pyautogui keyboard pillow
```

---

# Run Application

```bash
python auto_typer_pro.py
```

---

# How It Works

1. Enter a message.
2. Assign a trigger keyword.
3. Set typing speed.
4. Configure repeat count.
5. Save shortcut.
6. Type the keyword anywhere.
7. Application automatically types the assigned message.

---

# Example Usage

| Keyword | Output                      |
| ------- | --------------------------- |
| ;;hello | Hello, how are you?         |
| ;;mail  | Thank you for reaching out. |
| ;;bye   | Have a great day!           |

---

# Keyboard Controls

| Key             | Action                      |
| --------------- | --------------------------- |
| ESC             | Stop current typing process |
| Trigger Keyword | Activate auto typing        |

---

# Safety Features

* Emergency typing cancellation
* Thread-safe automation
* Fail-safe support using PyAutoGUI
* Input validation
* Protected UI operations

---

# Customization

Users can customize:

* Typing speed
* Repeat count
* UI appearance mode
* Shortcut keywords
* Message templates

---

# Future Improvements

* Shortcut export/import
* Cloud sync
* Macro recording
* Custom themes
* Voice activation
* Multi-language support
* Startup launch option
* System tray integration
* Encrypted shortcut storage

---

# Screenshots

Add your application screenshots here.

```md
![Screenshot.png]([assets/screenshot.png](https://github.com/Shivkd2803/Auto-Typer/blob/main/Screenshot.png))

assets/screenshot2.png
```

---

# Requirements

* Python 3.10+
* Windows / Linux / macOS
* Keyboard access permissions

---

# Known Limitations

* Some operating systems may require administrator privileges for global keyboard hooks.
* Antivirus software may flag automation tools because of keyboard simulation.

---

# License

This project is licensed under the MIT License.

---

# Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to your branch
5. Open a Pull Request

---

# Author

Developed by Shivendra Kumar.

---

# Support

If you found this project useful:

* Star the repository
* Share the project
* Contribute improvements

---

# Disclaimer

This software is intended for productivity and automation purposes only. Users are responsible for ensuring ethical and lawful usage.
