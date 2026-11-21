"""FlipBoot - Cross-platform, cross-OS boot switcher.

FlipBoot is a beautiful, cross-platform tool that detects whether your PC
uses UEFI or Legacy BIOS and switches the next boot to any OS.

Copyright (c) 2026 Lord_Doug
License: MIT
"""

__version__ = "0.1.0-alpha"
__author__ = "Lord_Doug"
__license__ = "MIT"

from .detector import detect_boot_mode, list_boot_entries

__all__ = [
    "detect_boot_mode",
    "list_boot_entries",
    "__version__",
]