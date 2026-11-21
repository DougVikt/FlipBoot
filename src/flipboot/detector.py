"""Boot mode detector - identifies UEFI vs Legacy BIOS."""
import os
import platform
import subprocess


def detect_boot_mode() -> str:
    """Return 'uefi' or 'legacy' based on the current system."""
    system = platform.system().lower()

    if system == "windows":
        return _detect_windows()
    elif system == "linux":
        return _detect_linux()
    elif system == "darwin":
        return _detect_macos()
    else:
        raise RuntimeError(f"Unsupported OS: {system}")


def _detect_windows() -> str:
    """Detect boot mode on Windows."""
    # Method 1: Try bcdedit /enum firmware
    try:
        result = subprocess.run(
            ["bcdedit", "/enum", "firmware"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 or "firmware" in result.stdout.lower() or "fwbootmgr" in result.stdout.lower():
            return "uefi"
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # Method 2: Check if EFI system partition exists via diskpart
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Partition | Where-Object { $_.Type -eq 'System' } | Select-Object -First 1"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return "uefi"
    except Exception:
        pass

    # Method 3: Check WMI SystemType
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance -ClassName Win32_ComputerSystem).SystemType"],
            capture_output=True, text=True, timeout=15,
        )
        if result.stdout.strip() == "9":
            return "uefi"
    except Exception:
        pass

    # Method 4: Check environment variable
    if os.environ.get("firmware_type", "").lower() == "uefi":
        return "uefi"

    # Method 5: Check for EFI directory
    efi_paths = [
        r"C:\Windows\Boot\EFI",
        r"C:\EFI",
        r"C:\Windows\Boot\EFI\bootmgfw.efi",
    ]
    for p in efi_paths:
        if os.path.exists(p):
            return "uefi"

    return "legacy"


def _detect_linux() -> str:
    """Detect boot mode on Linux."""
    if os.path.isdir("/sys/firmware/efi"):
        return "uefi"
    try:
        result = subprocess.run(
            ["efibootmgr"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return "uefi"
    except FileNotFoundError:
        pass
    return "legacy"


def _detect_macos() -> str:
    """Detect boot mode on macOS."""
    try:
        result = subprocess.run(
            ["ioreg", "-l", "-p", "IODeviceTree"],
            capture_output=True, text=True, timeout=10,
        )
        if "firmware-abi" in result.stdout.lower() or "efi" in result.stdout.lower():
            return "uefi"
    except FileNotFoundError:
        pass
    return "uefi"


def is_uefi() -> bool:
    return detect_boot_mode() == "uefi"


def list_boot_entries(mode: str) -> list:
    """List boot entries for the given mode."""
    try:
        from .uefi_strategy import list_boot_entries_uefi
    except ImportError:
        from uefi_strategy import list_boot_entries_uefi
    if mode == "uefi":
        return list_boot_entries_uefi()
    return []