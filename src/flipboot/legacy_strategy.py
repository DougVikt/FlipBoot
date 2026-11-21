"""Legacy BIOS boot strategy - change boot order using available tools."""
import platform
import re
import subprocess
import time


def switch_boot_legacy(target: str = "", reboot: bool = False, windows_to_windows: bool = False) -> bool:
    """Switch the next boot to target OS on a Legacy BIOS system."""
    system = platform.system().lower()

    if system == "windows":
        return _switch_windows_legacy(target, reboot, windows_to_windows)
    elif system == "linux":
        return _switch_linux_legacy(target, reboot)
    elif system == "darwin":
        return _switch_macos_legacy(target, reboot)
    else:
        print(f"ERROR: Unsupported OS: {system}")
        return False


def _switch_windows_legacy(target: str, reboot: bool, windows_to_windows: bool) -> bool:
    """On Windows Legacy BIOS, guide user to use EasyBCD or manual methods."""
    print("  Legacy BIOS detected on Windows.")
    print()
    print("  Automatic boot switching on Legacy BIOS Windows is limited.")
    print("  Recommended methods:")
    print()
    print("  1. EasyBCD (Recommended):")
    print("     - Download: https://neosmart.net/EasyBCD/")
    print("     - Install and run as Administrator")
    print("     - Add New Entry -> Linux/BSD or Windows -> select your OS")
    print("     - Save settings and reboot")
    print()
    print("  2. rEFInd (Alternative boot manager):")
    print("     - Download: https://www.rodsbooks.com/refind/getting.html")
    print("     - Provides a graphical boot menu for Legacy and UEFI")
    print()
    print("  3. Manual BIOS change:")
    print("     - Restart PC and press F2/F12/Del during boot")
    print("     - Change boot order to put target OS first")
    print()
    print("  4. grub4dos (Advanced):")
    print("     - Download: https://sourceforge.net/projects/grub4dos/")
    print("     - Chainload any OS from Windows bootloader")
    print()
    return False


def _switch_linux_legacy(target: str, reboot: bool) -> bool:
    """On Linux Legacy BIOS, use grub to set default boot entry."""
    print("  [*] Searching for grub entry matching '%s'..." % target)

    try:
        result = subprocess.run(
            ["grep", "-i", target, "/boot/grub/grub.cfg"],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        print("  ERROR: grep not found.")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    if result.returncode != 0 or not result.stdout:
        print(f"  ERROR: No grub entry matching '{target}' found.")
        print("  Make sure the target OS is installed and grub is configured.")
        return False

    menuentry = None
    for line in result.stdout.splitlines():
        m = re.search(r"menuentry\s+['\"]([^'\"]+)['\"]", line)
        if m:
            menuentry = m.group(1)
            break

    if not menuentry:
        print("  ERROR: Could not parse menuentry from grub.cfg.")
        return False

    print(f"  Found grub entry: {menuentry}")

    print("  [*] Setting as default boot entry...")
    try:
        result = subprocess.run(
            ["sudo", "grub-set-default", menuentry],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"  ERROR: grub-set-default failed: {result.stderr}")
            print("  Please manually set GRUB_DEFAULT in /etc/default/grub")
            return False
    except FileNotFoundError:
        print("  ERROR: grub-set-default not found.")
        print("  Please install grub-common: sudo apt install grub-common")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    print("  [*] Updating grub configuration...")
    try:
        subprocess.run(["sudo", "update-grub"], check=True, timeout=60)
    except FileNotFoundError:
        print("  WARNING: update-grub not found. Skipping.")
    except Exception as e:
        print(f"  WARNING: update-grub failed: {e}")

    print("  OK! Next boot will be the selected OS.")
    print()

    if reboot:
        print("  Rebooting in 5 seconds... (close window to cancel)")
        time.sleep(5)
        try:
            subprocess.run(["sudo", "reboot"], check=False)
        except Exception as e:
            print(f"  ERROR: Failed to reboot: {e}")
            return False

    return True


def _switch_macos_legacy(target: str, reboot: bool) -> bool:
    """macOS doesn't use Legacy BIOS in modern systems."""
    print("  macOS uses UEFI. Use the UEFI strategy.")
    return False


# Alias for backward compatibility
def switch_to_linux_legacy(target="kali", reboot=False):
    return switch_boot_legacy(target, reboot)