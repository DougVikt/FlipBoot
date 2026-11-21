"""UEFI boot strategy - change boot order using platform-specific tools."""
import platform
import re
import subprocess
import time


# Entries to skip (not actual OS boot entries)
_SKIP_NAMES = [
    "gerenciador de inicialização de firmware",
    "gerenciador de inicializacao de firmware",
    "firmware boot manager",
    "fwbootmgr",
    "windows boot manager",
    "uefi os",
    "boot manager",
    "aplicativo de firmware",
    "firmware application",
]


def _is_real_os_entry(name: str, guid: str, block: str) -> bool:
    """Check if an entry represents an actual OS installation."""
    name_lower = name.lower().strip()

    # Skip firmware manager entries
    if guid in ("{fwbootmgr}", "{bootmgr}", "{default}", "{globalsettings}"):
        return False

    # Skip entries with generic/non-OS names
    for skip in _SKIP_NAMES:
        if skip in name_lower:
            return False

    # Skip entries that look like disk names (e.g., "ST500LM034-2GH17A 3202")
    os_keywords = ["windows", "linux", "ubuntu", "kali", "fedora", "debian", "arch",
                   "manjaro", "mint", "opensuse", "suse", "grub", "pop", "centos",
                   "redhat", "gentoo", "slackware", "zorin", "elementary", "deepin"]
    if not any(kw in name_lower for kw in os_keywords):
        # Check if it's a disk name pattern (has digits and spaces)
        if any(c.isdigit() for c in name) and " " in name:
            return False
        # If no OS keyword and no digits, might still be an OS (e.g., "kali" without digits)
        # But if it's very short or looks like a device, skip
        if len(name) < 3:
            return False

    return True


def _clean_os_name(name: str) -> str:
    """Clean up OS name for display."""
    # Replace non-breaking spaces and other special chars with regular space
    name = name.replace("\xa0", " ").replace("\u200b", "").replace("\ufeff", "")
    # Replace 0xFF (ÿ) and other non-ASCII separators with space
    name = "".join(c if ord(c) < 128 else " " for c in name)
    name = name.strip()
    if name.endswith(" (BCD)"):
        name = name[:-6].strip()
    # Remove any remaining non-printable characters
    name = "".join(c if c.isprintable() or c == " " else " " for c in name)
    name = " ".join(name.split())
    return name


def list_boot_entries_uefi() -> list:
    """List all UEFI boot entries. Returns list of dicts with name, guid, disk."""
    system = platform.system().lower()
    entries = []
    seen_guids = set()

    if system == "windows":
        # First, get Windows BCD entries (these have the actual OS names)
        try:
            result = subprocess.run(
                ["bcdedit", "/enum"],
                capture_output=True, text=True, timeout=30,
            )
            if result.stdout:
                blocks = re.split(r"\n\s*\n", result.stdout)
                for block in blocks:
                    if "Windows" not in block and "windows" not in block.lower():
                        continue
                    lines = [l.strip() for l in block.splitlines() if l.strip()]
                    id_match = re.search(r"identificador\s+(\{[a-zA-Z0-9-]+\})", block, re.IGNORECASE)
                    if not id_match:
                        continue
                    guid = id_match.group(1)
                    if guid in ("{bootmgr}", "{fwbootmgr}", "{default}", "{globalsettings}"):
                        continue
                    if guid in seen_guids:
                        continue

                    # Must contain winload (Windows boot entry)
                    if "winload" not in block.lower():
                        continue

                    desc = "Windows"
                    for line in lines:
                        if line.lower().startswith("description"):
                            desc = line.split(None, 1)[-1] if len(line.split()) > 1 else desc
                            break

                    if not _is_real_os_entry(desc, guid, block):
                        continue

                    seen_guids.add(guid)
                    entries.append({
                        "name": _clean_os_name(desc),
                        "guid": guid,
                        "disk": "BCD store",
                        "raw": block,
                        "type": "windows_bcd",
                    })
        except Exception:
            pass

        # Then, get firmware entries (Linux distros, etc.)
        try:
            result = subprocess.run(
                ["bcdedit", "/enum", "firmware"],
                capture_output=True, text=True, timeout=30,
            )
            if not result.stdout:
                return entries

            blocks = re.split(r"\n\s*\n", result.stdout)
            for block in blocks:
                lines = [l.strip() for l in block.splitlines() if l.strip()]
                if len(lines) < 2:
                    continue
                # Find the identifier of this block (must be "identificador {guid}")
                id_match = re.search(r"identificador\s+(\{[a-zA-Z0-9-]+\})", block, re.IGNORECASE)
                if not id_match:
                    continue
                guid = id_match.group(1)
                if guid == "{fwbootmgr}":
                    continue
                if guid in seen_guids:
                    continue

                # Extract description (prefer description field over first line)
                desc = None
                for line in lines:
                    if line.lower().startswith("description"):
                        desc = line.split(None, 1)[-1] if len(line.split()) > 1 else None
                        break
                if not desc:
                    # Use first non-separator line as name
                    for line in lines:
                        if not line.startswith("-") and not line.startswith("identificador") and not line.startswith("device") and not line.startswith("path") and not line.startswith("description"):
                            desc = line
                            break
                    if not desc:
                        desc = lines[0] if lines else "Unknown"

                if not _is_real_os_entry(desc, guid, block):
                    continue

                # Extract disk info
                disk = ""
                for line in lines:
                    if "partition=" in line.lower():
                        disk = line.strip()
                        break

                seen_guids.add(guid)
                entries.append({
                    "name": _clean_os_name(desc),
                    "guid": guid,
                    "disk": disk if disk else "Firmware",
                    "raw": block,
                    "type": "firmware",
                })
        except Exception:
            pass

    elif system == "linux":
        try:
            result = subprocess.run(
                ["efibootmgr"],
                capture_output=True, text=True, timeout=30,
            )
            if result.stdout:
                for line in result.stdout.splitlines():
                    m = re.match(r"Boot([0-9A-Fa-f]+)\*?\s+(.+)", line)
                    if m:
                        num = m.group(1)
                        name = m.group(2).strip()
                        if not _is_real_os_entry(name, f"Boot{num}", line):
                            continue
                        entries.append({
                            "name": _clean_os_name(name),
                            "guid": f"Boot{num}",
                            "disk": "EFI",
                            "raw": line,
                            "type": "efi",
                        })
        except Exception:
            pass

    return entries


def switch_boot_uefi(target: str, reboot: bool = False, windows_to_windows: bool = False) -> bool:
    """Switch the next boot to target OS on a UEFI system."""
    system = platform.system().lower()

    if system == "windows":
        return _switch_windows_uefi(target, reboot, windows_to_windows)
    elif system == "linux":
        return _switch_linux_uefi(target, reboot)
    elif system == "darwin":
        return _switch_macos_uefi(target, reboot)
    else:
        print(f"ERROR: Unsupported OS: {system}")
        return False


def _switch_windows_uefi(target: str, reboot: bool, windows_to_windows: bool) -> bool:
    """Switch boot on Windows UEFI."""

    if windows_to_windows:
        return _switch_windows_to_windows(target, reboot)

    # Standard: switch firmware boot entry
    print("  [*] Reading firmware boot entries...")

    try:
        result = subprocess.run(
            ["bcdedit", "/enum", "firmware"],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        print("  ERROR: bcdedit not found.")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    if not result.stdout or ("fwbootmgr" not in result.stdout.lower() and "bootmgr" not in result.stdout.lower()):
        print("  ERROR: Failed to read firmware entries.")
        if result.stderr:
            print(f"  stderr: {result.stderr}")
        return False

    output = result.stdout
    blocks = output.split("\n\n")
    guid = None
    matched_name = None

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        id_match = re.search(r"identificador\s+(\{[a-zA-Z0-9-]+\})", block, re.IGNORECASE)
        if not id_match:
            continue
        g = id_match.group(1)
        if g == "{fwbootmgr}":
            continue
        # Check if block contains target (case-insensitive)
        if target.lower() in block.lower():
            guid = g
            for line in lines:
                if line.lower().startswith("description"):
                    matched_name = line.split(None, 1)[-1] if len(line.split()) > 1 else None
                    break
            if not matched_name:
                matched_name = lines[0] if lines else target
            break

    if not guid:
        print(f"  ERROR: No firmware entry matching '{target}' found.")
        print("  Available entries:")
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if len(lines) < 2:
                continue
            id_match = re.search(r"identificador\s+(\{[a-zA-Z0-9-]+\})", block, re.IGNORECASE)
            if id_match and id_match.group(1) != "{fwbootmgr}":
                desc = lines[0] if lines else "Unknown"
                for line in lines:
                    if line.lower().startswith("description"):
                        desc = line.split(None, 1)[-1] if len(line.split()) > 1 else desc
                        break
                print(f"    - {id_match.group(1)} : {desc}")
        return False

    print(f"  Found entry: {matched_name or target} ({guid})")

    # Set as first in displayorder
    print("  [*] Setting as first boot entry...")
    try:
        result = subprocess.run(
            ["bcdedit", "/displayorder", guid, "/addfirst"],
            capture_output=True, text=True, timeout=30,
        )
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    if result.returncode != 0:
        print(f"  ERROR: Failed to set boot order: {result.stderr or result.stdout}")
        return False

    print("  OK! Next boot will be the selected OS.")
    print()

    if reboot:
        print("  Rebooting in 5 seconds... (close window to cancel)")
        time.sleep(5)
        try:
            subprocess.run(["shutdown", "/r", "/t", "0"], check=False)
        except Exception as e:
            print(f"  ERROR: Failed to reboot: {e}")
            return False

    return True


def _switch_windows_to_windows(target: str, reboot: bool) -> bool:
    """Switch between Windows installations using BCD store."""
    print("  [*] Reading Windows boot entries (BCD store)...")

    try:
        result = subprocess.run(
            ["bcdedit", "/enum"],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        print("  ERROR: bcdedit not found.")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    if not result.stdout:
        print("  ERROR: Failed to read BCD store.")
        return False

    output = result.stdout
    blocks = output.split("\n\n")
    guid = None
    matched_name = None

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        # Must contain winload (Windows boot entry)
        if "winload" not in block.lower() and "windows" not in block.lower():
            continue
        id_match = re.search(r"identificador\s+(\{[a-zA-Z0-9-]+\})", block, re.IGNORECASE)
        if not id_match:
            continue
        g = id_match.group(1)
        if g in ("{bootmgr}", "{fwbootmgr}", "{default}", "{globalsettings}"):
            continue

        # Check if block contains target (normalize spaces and special chars)
        block_normalized = " ".join(block.lower().split())
        target_normalized = " ".join(target.lower().split())
        target_words = target_normalized.split()

        full_match = target_normalized in block_normalized
        words_match = len(target_words) > 0 and all(w in block_normalized for w in target_words)

        if full_match or words_match:
            desc = ""
            for line in lines:
                if line.lower().startswith("description"):
                    desc = " ".join(line.split(None, 1)[-1].lower().split()) if len(line.split()) > 1 else ""
                    break

            if desc:
                if target_normalized in desc or all(w in desc for w in target_words):
                    guid = g
                    matched_name = desc
                    break
            else:
                guid = g
                matched_name = target
                break

    if not guid:
        print(f"  ERROR: No Windows entry matching '{target}' found in BCD store.")
        print("  Available Windows entries:")
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if len(lines) < 2:
                continue
            if "winload" not in block.lower():
                continue
            id_match = re.search(r"identificador\s+(\{[a-zA-Z0-9-]+\})", block, re.IGNORECASE)
            if id_match and id_match.group(1) not in ("{current}", "{bootmgr}", "{fwbootmgr}", "{default}"):
                desc = "Windows"
                for line in lines:
                    if line.lower().startswith("description"):
                        desc = line.split(None, 1)[-1] if len(line.split()) > 1 else desc
                        break
                print(f"    - {id_match.group(1)} : {desc}")
        return False

    print(f"  Found Windows entry: {matched_name} ({guid})")

    # Set as default
    print("  [*] Setting as default boot entry...")
    try:
        result = subprocess.run(
            ["bcdedit", "/default", guid],
            capture_output=True, text=True, timeout=30,
        )
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    if result.returncode != 0:
        print(f"  ERROR: Failed to set default: {result.stderr or result.stdout}")
        return False

    print("  OK! Next boot will be the selected OS.")
    print()

    if reboot:
        print("  Rebooting in 5 seconds... (close window to cancel)")
        time.sleep(5)
        try:
            subprocess.run(["shutdown", "/r", "/t", "0"], check=False)
        except Exception as e:
            print(f"  ERROR: Failed to reboot: {e}")
            return False

    return True


def _switch_linux_uefi(target: str, reboot: bool) -> bool:
    """Use efibootmgr to change UEFI boot order on Linux."""
    print("  [*] Reading UEFI boot entries...")

    try:
        result = subprocess.run(
            ["efibootmgr"],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        print("  ERROR: efibootmgr not found. Install it with: sudo apt install efibootmgr")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    if result.returncode != 0:
        print(f"  ERROR: efibootmgr failed: {result.stderr}")
        return False

    output = result.stdout
    boot_num = None
    matched_name = None

    for line in output.splitlines():
        if target.lower() in line.lower():
            m = re.match(r"Boot([0-9A-Fa-f]+)\*?\s+(.+)", line)
            if m:
                boot_num = m.group(1)
                matched_name = m.group(2).strip()
                break

    if not boot_num:
        print(f"  ERROR: No boot entry matching '{target}' found.")
        print("  Available entries:")
        print(output)
        return False

    print(f"  Found entry: {matched_name} (Boot{boot_num})")

    order_match = re.search(r"BootOrder:\s*([0-9A-Fa-f,]+)", output)
    if not order_match:
        print("  ERROR: Could not parse BootOrder.")
        return False

    current_order = order_match.group(1).split(",")
    new_order = [boot_num] + [b for b in current_order if b != boot_num]
    new_order_str = ",".join(new_order)

    print("  [*] Setting as first boot entry...")
    try:
        result = subprocess.run(
            ["sudo", "efibootmgr", "-o", new_order_str],
            capture_output=True, text=True, timeout=30,
        )
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    if result.returncode != 0:
        print(f"  ERROR: Failed to set boot order: {result.stderr}")
        return False

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


def _switch_macos_uefi(target: str, reboot: bool) -> bool:
    """macOS boot switching."""
    print("  macOS boot switching requires manual configuration.")
    print("  For other OSes, use rEFInd or hold Option key during boot.")
    return False


# Alias for backward compatibility
def switch_to_linux_uefi(target="kali", reboot=False):
    return switch_boot_uefi(target, reboot)


def list_boot_entries(mode: str) -> list:
    """List boot entries for the given mode."""
    if mode == "uefi":
        return list_boot_entries_uefi()
    return []