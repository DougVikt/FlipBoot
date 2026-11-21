"""Tool checker - detects missing tools and provides install guidance."""
import platform
import shutil
import subprocess
import sys

# Import security module if available
try:
    from .security import safe_download, TRUSTED_URLS
    SECURITY_AVAILABLE = True
except ImportError:
    try:
        from security import safe_download, TRUSTED_URLS
        SECURITY_AVAILABLE = True
    except ImportError:
        SECURITY_AVAILABLE = False


# Tool definitions: name -> {description, windows, linux, macos, auto_install_linux}
TOOLS = {
    "bcdedit": {
        "description": "Windows Boot Configuration Data editor (built-in)",
        "windows": {"builtin": True, "path": "C:\\Windows\\System32\\bcdedit.exe"},
        "linux": None,
        "macos": None,
    },
    "efibootmgr": {
        "description": "UEFI boot manager for Linux",
        "windows": None,
        "linux": {
            "package": "efibootmgr",
            "apt": "sudo apt install efibootmgr",
            "dnf": "sudo dnf install efibootmgr",
            "pacman": "sudo pacman -S efibootmgr",
            "zypper": "sudo zypper install efibootmgr",
        },
        "macos": None,
    },
    "grub-set-default": {
        "description": "GRUB default entry setter (Linux Legacy)",
        "windows": None,
        "linux": {
            "package": "grub-common",
            "apt": "sudo apt install grub-common",
            "dnf": "sudo dnf install grub2-tools",
            "pacman": "sudo pacman -S grub",
            "zypper": "sudo zypper install grub2",
        },
        "macos": None,
    },
    "update-grub": {
        "description": "GRUB configuration updater (Linux Legacy)",
        "windows": None,
        "linux": {
            "package": "grub2-common",
            "apt": "sudo apt install grub-pc",
            "dnf": "sudo dnf install grub2-tools",
            "pacman": "sudo pacman -S grub",
            "zypper": "sudo zypper install grub2",
        },
        "macos": None,
    },
}

# External tools that need manual download
EXTERNAL_TOOLS = {
    "EasyBCD": {
        "description": "Windows bootloader manager (Legacy BIOS)",
        "url": "https://neosmart.net/EasyBCD/",
        "platforms": ["windows"],
        "purpose": "Add Linux entry to Windows bootloader on Legacy BIOS",
    },
    "rEFInd": {
        "description": "UEFI boot manager (cross-platform)",
        "url": "https://www.rodsbooks.com/refind/getting.html",
        "platforms": ["windows", "linux", "darwin"],
        "purpose": "Alternative boot manager for UEFI systems",
    },
    "grub4dos": {
        "description": "GRUB for DOS (Legacy BIOS)",
        "url": "https://sourceforge.net/projects/grub4dos/",
        "platforms": ["windows"],
        "purpose": "Chainload Linux from Windows bootloader on Legacy BIOS",
    },
}


def check_tool(name: str) -> bool:
    """Check if a tool is available on the system."""
    if shutil.which(name):
        return True
    # Check Windows built-in paths
    tool_info = TOOLS.get(name, {})
    if platform.system().lower() == "windows":
        win_info = tool_info.get("windows", {})
        if win_info and win_info.get("builtin"):
            path = win_info.get("path", "")
            if path and __import__("os").path.exists(path):
                return True
    return False


def get_linux_distro() -> str:
    """Detect Linux distribution family."""
    try:
        with open("/etc/os-release") as f:
            content = f.read().lower()
        if "ubuntu" in content or "debian" in content or "mint" in content or "pop" in content:
            return "apt"
        if "fedora" in content or "rhel" in content or "centos" in content or "rocky" in content:
            return "dnf"
        if "arch" in content or "manjaro" in content:
            return "pacman"
        if "suse" in content or "opensuse" in content:
            return "zypper"
    except Exception:
        pass
    return "apt"  # default


def get_install_command(tool_name: str) -> str | None:
    """Get the install command for a tool on the current platform."""
    system = platform.system().lower()
    tool_info = TOOLS.get(tool_name, {})

    if system == "linux":
        linux_info = tool_info.get("linux")
        if not linux_info:
            return None
        distro = get_linux_distro()
        return linux_info.get(distro, linux_info.get("apt"))
    return None


def check_missing_tools(mode: str) -> list:
    """Check which tools are missing for the given boot mode."""
    system = platform.system().lower()
    missing = []

    if mode == "uefi":
        if system == "windows":
            if not check_tool("bcdedit"):
                missing.append("bcdedit")
        elif system == "linux":
            if not check_tool("efibootmgr"):
                missing.append("efibootmgr")
        elif system == "darwin":
            pass  # macOS uses bless (built-in)
    else:  # legacy
        if system == "linux":
            if not check_tool("grub-set-default"):
                missing.append("grub-set-default")
            if not check_tool("update-grub"):
                missing.append("update-grub")

    return missing


def try_auto_install(tool_name: str) -> bool:
    """Try to auto-install a tool on Linux. Returns True if successful."""
    system = platform.system().lower()
    if system != "linux":
        return False

    cmd = get_install_command(tool_name)
    if not cmd:
        return False

    print(f"  [*] Attempting to install {tool_name}...")
    print(f"      Command: {cmd}")
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"  [OK] {tool_name} installed successfully!")
            return True
        else:
            print(f"  [FAIL] Installation failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  [FAIL] Installation error: {e}")
        return False


def show_install_guide(missing_tools: list, mode: str):
    """Show detailed installation guide for missing tools."""
    system = platform.system().lower()

    print()
    print("=" * 60)
    print("  MISSING TOOLS DETECTED")
    print("=" * 60)
    print()

    for tool in missing_tools:
        tool_info = TOOLS.get(tool, {})
        desc = tool_info.get("description", tool)

        print(f"  Tool: {tool}")
        print(f"  Description: {desc}")
        print()

        if system == "linux":
            cmd = get_install_command(tool)
            if cmd:
                print(f"  Install command:")
                print(f"    {cmd}")
                print()
                # Try auto-install
                print(f"  Attempting automatic installation...")
                if try_auto_install(tool):
                    print(f"  [OK] {tool} is now available!")
                else:
                    print(f"  [FAIL] Could not install automatically.")
                    print(f"  Please run manually: {cmd}")
            else:
                print(f"  No automatic install available for this platform.")
        elif system == "windows":
            # Windows: suggest built-in or download
            win_info = tool_info.get("windows", {})
            if win_info and win_info.get("builtin"):
                print(f"  This tool should be built-in. Check if Windows is up to date.")
            else:
                print(f"  This tool is not available on Windows.")
                print(f"  Consider using an alternative method.")
        elif system == "darwin":
            print(f"  macOS: This tool is not available natively.")
            print(f"  Consider using rEFInd or manual boot selection.")

        print()

    # Show external tools if relevant
    if mode == "legacy" and system == "windows":
        print("  RECOMMENDED EXTERNAL TOOLS:")
        print()
        for name, info in EXTERNAL_TOOLS.items():
            if system in info["platforms"]:
                print(f"    {name}:")
                print(f"      Purpose: {info['purpose']}")
                print(f"      Download: {info['url']}")
                if SECURITY_AVAILABLE:
                    print(f"      [SECURITY] HTTPS enforced, verify installer signature")
                print()

    print("=" * 60)


def check_and_install(mode: str) -> bool:
    """Check for missing tools and attempt to install them. Returns True if all tools available."""
    missing = check_missing_tools(mode)

    if not missing:
        return True

    print(f"  [!] Missing tools: {', '.join(missing)}")
    show_install_guide(missing, mode)

    # Re-check after attempted installs
    still_missing = [t for t in missing if not check_tool(t)]
    if still_missing:
        print(f"  [FAIL] Still missing: {', '.join(still_missing)}")
        return False

    print(f"  [OK] All required tools are now available!")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Check and install boot tools")
    parser.add_argument("--mode", choices=["uefi", "legacy"], default="uefi")
    args = parser.parse_args()

    ok = check_and_install(args.mode)
    sys.exit(0 if ok else 1)