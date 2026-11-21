# FlipBoot - Cross-Platform, Cross-OS Boot Switcher

<div align="center">

![FlipBoot Banner](https://img.shields.io/badge/APP__BOOT-v2.0-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)

**A beautiful, cross-platform tool that detects whether your PC uses UEFI or Legacy BIOS
and switches the next boot to any OS (Linux distros, Windows versions, etc.).**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Screenshots](#screenshots) • [Contributing](#contributing)

</div>

---

## Overview

FlipBoot is a powerful, user-friendly command-line tool designed to simplify the process of switching between operating systems on multi-boot configurations. Whether you're running Windows and Linux on the same machine, or multiple versions of Windows, FlipBoot handles the complexity of UEFI and Legacy BIOS boot management behind a beautiful, intuitive interface.

### Why FlipBoot?

- **No more BIOS menus**: Switch OS without restarting into BIOS
- **One-click operation**: Simple double-click to switch and reboot
- **Cross-platform**: Works seamlessly on Windows, Linux, and macOS
- **Smart detection**: Automatically detects UEFI vs Legacy BIOS
- **Beautiful UI**: Colorful terminal interface with progress indicators
- **Safe and secure**: Built-in integrity checks and security features

---

## Features

### Core Features
- **Automatic Boot Mode Detection** - Detects UEFI vs Legacy BIOS automatically
- **Cross-OS Switching** - Switch between any installed OS (Linux-to-Linux, Windows-to-Windows, etc.)
- **Same or Separate HDDs** - Works regardless of disk layout
- **One-Click Operation** - Double-click to switch and reboot
- **Beautiful Terminal UI** - Colorful interface with banners, tables, and progress bars

### UEFI Support
- **Windows**: Uses `bcdedit` for firmware boot order management
- **Linux**: Uses `efibootmgr` for UEFI boot entry management
- **Windows-to-Windows**: Uses BCD store for switching between Windows versions
- **Auto-tool detection**: Checks and installs missing tools automatically

### Legacy BIOS Support
- **Linux**: Uses `grub-set-default` and `update-grub`
- **Windows**: Provides guided setup with EasyBCD, rEFInd, or grub4dos
- **Manual fallback**: Clear instructions for BIOS boot order changes

### Security Features
- **File Integrity Verification** - SHA256 hash checks on every run
- **Modification Detection** - Alerts if project files were changed
- **HTTPS Enforcement** - All downloads use secure HTTPS connections
- **Trusted URL Whitelist** - Downloads verified against known sources
- **Admin Privilege Verification** - Ensures proper permissions before operations
- **Security Status Report** - Comprehensive security overview
- **Safe Auto-Install** - User confirmation before package installation

### Developer Features
- **Modular Architecture** - Clean separation of concerns
- **CLI Interface** - Full command-line support with argparse
- **Extensible** - Easy to add new strategies or platforms
- **No Dependencies** - Pure Python standard library
- **Cross-Platform** - Single codebase for all platforms

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Administrator/root privileges (requested automatically)

### Quick Start

#### Windows
1. Download or clone the repository
2. Double-click `run.bat`
3. Follow the on-screen prompts

#### Linux
```bash
git clone https://github.com/yourusername/FlipBoot.git
cd FlipBoot
chmod +x run.sh
./run.sh
```

#### macOS
```bash
git clone https://github.com/yourusername/FlipBoot.git
cd FlipBoot
chmod +x run.sh
./run.sh
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/FlipBoot.git
cd FlipBoot

# Run directly with Python
python main.py --help
```

---

## Usage

### Basic Usage

#### Switch to an OS and reboot
```bash
# Switch to Kali Linux
python main.py --target kali --reboot

# Switch to Ubuntu
python main.py --target ubuntu -r

# Switch to Windows 11
python main.py --target "Windows 11" --windows-to-windows --reboot
```

#### List available boot entries
```bash
python main.py --list
```

#### Switch without rebooting
```bash
python main.py --target kali
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--target` | `-t` | Text to match boot entry (e.g., kali, ubuntu, "Windows 11") |
| `--reboot` | `-r` | Reboot immediately after switching |
| `--list` | `-l` | List all available boot entries and exit |
| `--windows-to-windows` | | Switch between Windows installations |
| `--strict` | | Abort if integrity check fails |

### Examples

#### Linux to Linux
```bash
# Switch from Ubuntu to Kali (same HDD)
python main.py --target kali --reboot

# Switch from Kali to Fedora (different HDD)
python main.py --target fedora --reboot

# Switch from Debian to Arch
python main.py --target arch -r
```

#### Windows to Windows
```bash
# Switch from Windows 10 to Windows 11
python main.py --target "Windows 11" --windows-to-windows --reboot

# Switch from Windows 11 to Windows 10
python main.py --target "Windows 10" --windows-to-windows -r
```

#### Cross-OS Switching
```bash
# From Linux to Windows
python main.py --target "Windows 11" --reboot

# From Windows to Linux
python main.py --target kali --reboot
```

#### Utility Commands
```bash
# List all boot entries
python main.py --list

# Strict mode (abort on integrity failure)
python main.py --target kali --strict

# Security check
python security.py --check

# Verify file integrity
python security.py --verify
```

---

## Screenshots

### Main Interface
```
  +==============================================================+
  |                                                              |
  |     ____    ____  ____     ____   ____  ____    _   _        |
  |    / ___|  |  _ \|  _ \   | __ ) | __ )|  _ \  | | | |       |
  |    \___ \  | |_) | |_) |  |  _ \ |  _ \| |_) | | |_| |       |
  |     ___) | |  __/|  __/   | |_) || |_) |  __/  |  _  |       |
  |    |____/  |_|   |_|      |____/ |____/|_|     |_| |_|       |
  |                                                              |
  |         Cross-OS Boot Switcher v2.0                          |
  |         UEFI & Legacy BIOS | Windows/Linux/macOS             |
  +==============================================================+
```

### Boot Entries Table
```
  # | Name                                     | GUID                                   | Disk
  --+------------------------------------------+----------------------------------------+------------------
  1 | kali                                     | {cec69539-abcb-11f1-9416-806e6f6e6963} | HDD1
  2 | Windows 11                               | {b7962449-e560-11ef-ae92-88606e01e267} | HDD2
  3 | Ubuntu                                   | {a53deeb4-a61d-11f1-9414-988389c9cef2} | HDD1
```

### Success Output
```
  ==============================================================
  SUCCESS: Boot switched to 'kali'!
  ==============================================================
```

---

## Architecture

```
FlipBoot/
├── main.py              # Entry point with CLI and elevation
├── ui.py                # Terminal UI module (colors, tables, etc.)
├── detector.py          # UEFI/Legacy detection
├── security.py          # Integrity checks and security
├── tool_checker.py      # Tool detection and auto-install
├── uefi_strategy.py     # UEFI boot switching (bcdedit/efibootmgr)
├── legacy_strategy.py   # Legacy BIOS boot switching (grub)
├── run.bat              # Windows launcher
├── run.sh               # Linux/macOS launcher
├── README.md            # Documentation
├── requirements.txt     # No external dependencies
└── __init__.py          # Package init
```

### Module Descriptions

| Module | Description |
|--------|-------------|
| `main.py` | Entry point, CLI parsing, elevation, orchestration |
| `ui.py` | Terminal UI with colors, banners, tables, progress bars |
| `detector.py` | Detects UEFI vs Legacy BIOS on all platforms |
| `security.py` | File integrity, security status, safe downloads |
| `tool_checker.py` | Detects missing tools, provides install guidance |
| `uefi_strategy.py` | UEFI boot switching via bcdedit/efibootmgr |
| `legacy_strategy.py` | Legacy BIOS boot switching via grub/EasyBCD |

---

## Requirements

### System Requirements
- **OS**: Windows 10/11, Linux (any distro), macOS
- **Python**: 3.8 or higher
- **Privileges**: Administrator (Windows) / Root (Linux/macOS)

### Platform-Specific Requirements

#### Windows (UEFI)
- `bcdedit` (built-in, no installation needed)

#### Linux (UEFI)
- `efibootmgr` (auto-installed if missing)

#### Linux (Legacy BIOS)
- `grub-set-default` (auto-installed if missing)
- `update-grub` (auto-installed if missing)

#### Windows (Legacy BIOS)
- Manual setup required (EasyBCD recommended)

---

## Security

FlipBoot includes comprehensive security features:

### Integrity Verification
- SHA256 hash verification of all project files
- Modification detection since last run
- User confirmation if integrity check fails

### Safe Operations
- HTTPS enforcement for all downloads
- Trusted URL whitelist for external tools
- Admin privilege verification before operations
- User confirmation before package installation

### Security Commands
```bash
# Run security check
python security.py --check

# Verify file integrity
python security.py --verify

# Show file hashes
python security.py --hashes
```

---

## Troubleshooting

### Common Issues

#### "bcdedit not found"
- Ensure you're running on a UEFI system
- Run as Administrator
- Check if Windows is up to date

#### "No firmware entry matching target"
- Use `--list` to see available entries
- Try a different target name
- Ensure the OS is properly installed

#### "Permission denied"
- Run with Administrator/root privileges
- On Windows, right-click and "Run as Administrator"
- On Linux, use `sudo`

#### "Tool not found"
- The tool checker will guide you through installation
- On Linux, tools are auto-installed
- On Windows, download from the provided links

### Getting Help
```bash
python main.py --help
python security.py --help
python tool_checker.py --help
```

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
git clone https://github.com/yourusername/FlipBoot.git
cd FlipBoot
python main.py --help
```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **bcdedit** - Windows Boot Configuration Data editor
- **efibootmgr** - Linux UEFI boot manager
- **grub** - GNU GRUB bootloader
- **EasyBCD** - Windows bootloader manager
- **rEFInd** - UEFI boot manager

---

## Support

If you find this project useful, please consider:
- Starring the repository on GitHub
- Reporting bugs and issues
- Contributing improvements
- Sharing with others

---

<div align="center">

**Made with ❤️ for the multi-boot community**

[⬆ Back to Top](#FlipBoot---cross-platform-cross-os-boot-switcher)

</div>