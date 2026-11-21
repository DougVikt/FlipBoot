"""UI module - presentable terminal interface with colors and formatting."""
import os
import platform
import sys


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"


# Enable ANSI colors on Windows
def _enable_colors():
    if platform.system().lower() == "windows":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Enable virtual terminal processing
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


_enable_colors()


def clear_screen():
    """Clear the terminal screen."""
    if platform.system().lower() == "windows":
        os.system("cls")
    else:
        os.system("clear")


def print_banner():
    """Print the application banner."""
    banner = r"""
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
"""
    print(Colors.CYAN + banner + Colors.RESET)


def print_section(title: str):
    """Print a section header."""
    width = 62
    print()
    print(Colors.BOLD + Colors.BLUE + "  " + "=" * width + Colors.RESET)
    print(Colors.BOLD + Colors.BLUE + f"  {title}" + Colors.RESET)
    print(Colors.BOLD + Colors.BLUE + "  " + "=" * width + Colors.RESET)
    print()


def print_step(step: str, status: str = "info"):
    """Print a step with status indicator."""
    icons = {
        "info": ("[*]", Colors.CYAN),
        "ok": ("[+]", Colors.GREEN),
        "warn": ("[!]", Colors.YELLOW),
        "error": ("[X]", Colors.RED),
        "wait": ("[~]", Colors.MAGENTA),
    }
    icon, color = icons.get(status, icons["info"])
    print(f"  {color}{icon}{Colors.RESET} {step}")


def print_success(message: str):
    """Print a success message."""
    print()
    print(Colors.GREEN + "  " + "=" * 62 + Colors.RESET)
    print(Colors.BOLD + Colors.GREEN + f"  SUCCESS: {message}" + Colors.RESET)
    print(Colors.GREEN + "  " + "=" * 62 + Colors.RESET)
    print()


def print_error(message: str):
    """Print an error message."""
    print()
    print(Colors.RED + "  " + "=" * 62 + Colors.RESET)
    print(Colors.BOLD + Colors.RED + f"  ERROR: {message}" + Colors.RESET)
    print(Colors.RED + "  " + "=" * 62 + Colors.RESET)
    print()


def print_warning(message: str):
    """Print a warning message."""
    print(Colors.YELLOW + f"  [!] WARNING: {message}" + Colors.RESET)


def print_info(message: str):
    """Print an info message."""
    print(Colors.CYAN + f"  [i] {message}" + Colors.RESET)


def print_entry(index: int, name: str, guid: str, disk: str = ""):
    """Print a boot entry in a formatted way."""
    name_color = Colors.WHITE
    if "kali" in name.lower() or "linux" in name.lower() or "ubuntu" in name.lower():
        name_color = Colors.GREEN
    elif "windows" in name.lower():
        name_color = Colors.BLUE

    print(f"  {Colors.BOLD}{index:2d}.{Colors.RESET} {name_color}{name:<35}{Colors.RESET} {Colors.DIM}[{guid}]{Colors.RESET}  {Colors.YELLOW}{disk}{Colors.RESET}")


def print_progress(current: int, total: int, label: str = ""):
    """Print a progress bar."""
    bar_width = 40
    filled = int(bar_width * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_width - filled)
    percent = int(100 * current / total) if total > 0 else 0
    print(f"\r  {Colors.CYAN}[{bar}]{Colors.RESET} {percent:3d}% {label}", end="", flush=True)
    if current >= total:
        print()


def print_table(headers: list, rows: list):
    """Print a formatted table."""
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Print header
    header_line = "  " + " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(Colors.BOLD + Colors.CYAN + header_line + Colors.RESET)
    print("  " + "-+-".join("-" * w for w in widths))

    # Print rows
    for row in rows:
        row_line = "  " + " | ".join(str(cell).ljust(w) for cell, w in zip(row, widths))
        print(row_line)


def ask_yes_no(question: str, default: bool = False) -> bool:
    """Ask a yes/no question and return the answer."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"  {Colors.YELLOW}?{Colors.RESET} {question} ({default_str}): ").strip().lower()
    if not response:
        return default
    return response in ("y", "yes", "s", "sim")


def ask_choice(question: str, choices: list) -> int:
    """Ask user to choose from a list. Returns index (0-based)."""
    print(f"  {Colors.YELLOW}?{Colors.RESET} {question}")
    for i, choice in enumerate(choices, 1):
        print(f"    {Colors.CYAN}{i}.{Colors.RESET} {choice}")
    while True:
        try:
            response = input(f"  Enter choice (1-{len(choices)}): ").strip()
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return idx
        except ValueError:
            pass
        print(Colors.RED + "  Invalid choice. Try again." + Colors.RESET)


def print_footer():
    """Print footer."""
    print()
    print(Colors.DIM + "  " + "-" * 62 + Colors.RESET)
    print(Colors.DIM + "  FlipBoot v2.0 | Cross-OS Boot Switcher" + Colors.RESET)
    print(Colors.DIM + "  " + "-" * 62 + Colors.RESET)
    print()


if __name__ == "__main__":
    # Demo
    print_banner()
    print_section("Demo Section")
    print_step("This is an info step", "info")
    print_step("This is a success step", "ok")
    print_step("This is a warning step", "warn")
    print_step("This is an error step", "error")
    print_entry(1, "kali", "{cec69539-abcb-11f1-9416-806e6f6e6963}", "HDD1")
    print_entry(2, "Windows 11", "{b7962449-e560-11ef-ae92-88606e01e267}", "HDD2")
    print_success("Boot switched successfully!")
    print_error("Something went wrong!")
    print_footer()