# DiscShell

Python-Based Remote Management & Security Research Framework Utilizing Discord as C2

> [!WARNING]  
> **DiscShell is developed strictly for legitimate security research, system administration, and educational purposes.**  
> Unauthorized access to computer systems, networks, or data is illegal and strictly prohibited.   
> The developers and contributors of this project assume no responsibility for any misuse, damage, or legal consequences resulting from the improper use of this software.  
> By using DiscShell, you agree to comply with all applicable laws and regulations and accept full responsibility for your actions.

## Table of Contents
* [Overview](#overview)
* [Features](#features)
* [Project Structure](#project-Structure)
* [Prerequisites](#prerequisites)
* [Installation](#installation)  
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

## Overview

DiscShell is a Python-based remote management tool that leverages the Discord Bot API to control and monitor remote PCs. 
It uses a Discord server as a Command and Control (C2) channel, allowing multiple machines to be managed concurrently without requiring any port forwarding.

## Features
* C2 communication via Discord Bot API
* Multi-endpoint management (Control individual clients or broadcast commands)
* Remote Shell Execution:
    * Full access to system shell (CMD & PowerShell).
    * Real-time output redirection with encoding support.
* Advanced Surveillance (Observer):
    * Multi-Monitor Screenshot: Automatically detects and captures all connected monitors.
    * Webcam Capture: Auto-discovery of devices, dynamic max-resolution setting.
    * Stealth Recording: Records audio (WAV) directly to RAM (Memory) without saving files to the disk.
* System Monitoring:
    * Retrieve hardware specifications (CPU, RAM, GPU, Disk) and system uptime.
* File Operations:
    * Bidirectional Transfer: Upload and download files between the target PC and Discord.
* Persistence & Stealth :
    * Advanced Stealth Operations:
        * In-Memory Processing: Uses io.BytesIO streams for file transfers and recording to minimize forensic footprints on the hard drive.
        * Stealth Mode: Automatically hides the console window upon execution to run silently in the background.
    * Robust Persistence (Self-Healing):
        * Self-Replication: Copies the executable to a secure directory to prevent accidental deletion.
    * Dual Persistence Mechanism:
        * Registry Autorun: Adds an entry to `HKCU\...\Run` to ensure execution on system startup.
        * Task Scheduler: Registers a scheduled task with Highest Privileges, allowing the bot to bypass UAC prompts and run with Admin rights automatically upon user logon.
    * Self-Healing: Capable of maintaining access continuity without user intervention.

## Project Structure
```bash
DiscShell/
├── main.py   
├── modules/
│   ├── discdshell.py 
│   ├── persistence.py  
│   ├── constants.py
│   ├── __init__.py 
│   └── cogs
│       ├── __init__.py
│       ├── cmd.py
│       ├── powershell.py
│       ├── observer.py
│       ├── sysinfo.py
│       ├── fileoptions.py
│       ├── help.py
│       └── sessionManager.py       
└── .env
```

## Prerequisites

* Python 3.10+
* `pip` (Python package installer)
* Discord

## Installation

1.  **Clone the repository:** (If this is from a GitHub repo)
    ```bash
    git clone https://github.com/Quema100/DiscShell.git
    cd DiscShell
    ```
    (If you received the files directly, just navigate to the project directory.)

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
## Usage

### 1. Bot Token Configuration
Create a `.env` file in the project root directory and paste your Discord Bot Token.
```env
TOKEN = "Input your Discord Bot Token here"
```

### 2. Open Discord

After running the bot, verify that it appears online in your Discord server.
If the bot has not been added to your server yet, invite it first.

### 3. Use Slash Commands
To view all available commands, type the following in any channel where the bot is active:

```bash
/help
```

This will display a full list of supported DiscShell commands

### 4. Execute Commands on Endpoints
When a client (endpoint) is connected, you can directly control it from Discord:

```bash
!list
!select [ID] or 'all'
!cmd [ID] [command]
```

> [!TIP]
> **How to run this program on another PC**  
>  To run this program on another PC, follow these simple steps:  
>   1. install pyinstaller:
>       ``` ps
>       pip install pyinstaller
>       ```
>   2. Build:
>      ``` ps
>      pyinstaller -w -F --add-data=".env;." -n=DisCShell main.py
>      ```

## Contributing

Feel free to fork this repository, open issues, and submit pull requests. Suggestions for improving realism, or code quality are welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or discussions related to this simulation, please open an issue in the GitHub repository.