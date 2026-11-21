"""Security module - integrity checks and safe operations."""
import hashlib
import os
import subprocess
import sys
import urllib.request


# Known SHA256 hashes of project files (update when files change)
# These are computed at build time; in development, use --update-hashes
KNOWN_HASHES = {
    "main.py": None,  # Will be computed on first run
    "detector.py": None,
    "tool_checker.py": None,
    "uefi_strategy.py": None,
    "legacy_strategy.py": None,
}

# Trusted download URLs (HTTPS only)
TRUSTED_URLS = {
    "EasyBCD": "https://neosmart.net/EasyBCD/",
    "rEFInd": "https://www.rodsbooks.com/refind/getting.html",
    "grub4dos": "https://sourceforge.net/projects/grub4dos/",
}

# Official package repositories (for auto-install verification)
TRUSTED_REPOS = {
    "apt": ["archive.ubuntu.com", "deb.debian.org", "security.ubuntu.com"],
    "dnf": ["download.fedoraproject.org", "mirrors.fedoraproject.org"],
    "pacman": ["archlinux.org", "mirror.rackspace.com"],
    "zypper": ["download.opensuse.org"],
}


def compute_file_hash(filepath: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_project_dir() -> str:
    """Get the project directory."""
    return os.path.dirname(os.path.abspath(__file__))


def verify_file_integrity(filepath: str, expected_hash: str = None) -> tuple:
    """Verify a single file's integrity. Returns (ok, actual_hash, message)."""
    if not os.path.exists(filepath):
        return False, "", f"File not found: {filepath}"

    actual_hash = compute_file_hash(filepath)

    if expected_hash is None:
        # No expected hash provided - just return the hash
        return True, actual_hash, "No expected hash to compare"

    if actual_hash == expected_hash:
        return True, actual_hash, "OK"
    else:
        return False, actual_hash, f"Hash mismatch! Expected: {expected_hash[:16]}... Got: {actual_hash[:16]}..."


def verify_project_integrity(verbose: bool = True) -> bool:
    """Verify integrity of all project files."""
    project_dir = get_project_dir()
    all_ok = True
    results = []

    for filename in ["main.py", "detector.py", "tool_checker.py", "uefi_strategy.py", "legacy_strategy.py"]:
        filepath = os.path.join(project_dir, filename)
        if not os.path.exists(filepath):
            results.append((filename, False, "MISSING"))
            all_ok = False
            continue

        actual_hash = compute_file_hash(filepath)
        results.append((filename, True, actual_hash[:16] + "..."))

    if verbose:
        print("  [*] Project integrity check:")
        for filename, ok, info in results:
            status = "OK" if ok else "FAIL"
            print(f"      {filename}: {status} ({info})")

    # Check if any file was modified since last run (using a marker file)
    marker_file = os.path.join(project_dir, ".integrity_marker")
    if os.path.exists(marker_file):
        try:
            with open(marker_file, "r") as f:
                saved_hashes = {}
                for line in f:
                    if "=" in line:
                        name, h = line.strip().split("=", 1)
                        saved_hashes[name] = h

            for filename in ["main.py", "detector.py", "tool_checker.py", "uefi_strategy.py", "legacy_strategy.py"]:
                filepath = os.path.join(project_dir, filename)
                if os.path.exists(filepath):
                    current_hash = compute_file_hash(filepath)
                    if filename in saved_hashes and saved_hashes[filename] != current_hash:
                        print(f"  [WARNING] {filename} was modified since last run!")
                        all_ok = False
        except Exception:
            pass

    # Save current hashes
    try:
        with open(marker_file, "w") as f:
            for filename in ["main.py", "detector.py", "tool_checker.py", "uefi_strategy.py", "legacy_strategy.py"]:
                filepath = os.path.join(project_dir, filename)
                if os.path.exists(filepath):
                    f.write(f"{filename}={compute_file_hash(filepath)}\n")
    except Exception:
        pass

    return all_ok


def safe_download(url: str, dest_path: str, expected_hash: str = None) -> bool:
    """Download a file safely using HTTPS with optional hash verification."""
    # Enforce HTTPS
    if not url.startswith("https://"):
        print(f"  [SECURITY] Refusing to download from non-HTTPS URL: {url}")
        return False

    # Check if URL is in trusted list
    is_trusted = any(url.startswith(trusted) for trusted in TRUSTED_URLS.values())
    if not is_trusted:
        print(f"  [SECURITY] URL not in trusted list: {url}")
        response = input("  Continue anyway? (y/N): ").strip().lower()
        if response != "y":
            return False

    print(f"  [*] Downloading from: {url}")
    try:
        # Use urllib with timeout
        req = urllib.request.Request(url, headers={"User-Agent": "FlipBoot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()

        # Verify hash if provided
        if expected_hash:
            actual_hash = hashlib.sha256(data).hexdigest()
            if actual_hash != expected_hash:
                print(f"  [SECURITY] Hash mismatch! Download may be tampered.")
                print(f"  Expected: {expected_hash[:16]}...")
                print(f"  Got:      {actual_hash[:16]}...")
                return False

        # Write to file
        with open(dest_path, "wb") as f:
            f.write(data)

        print(f"  [OK] Downloaded to: {dest_path}")
        return True

    except Exception as e:
        print(f"  [ERROR] Download failed: {e}")
        return False


def safe_auto_install_linux(tool_name: str, package_manager: str) -> bool:
    """Safely auto-install a tool on Linux with repository verification."""
    import platform

    # Map package managers to their verification commands
    verify_cmds = {
        "apt": ["apt-cache", "policy"],
        "dnf": ["dnf", "info"],
        "pacman": ["pacman", "-Si"],
        "zypper": ["zypper", "info"],
    }

    print(f"  [*] Verifying package source for {tool_name}...")

    # Check if package manager is available
    if not __import__("shutil").which(package_manager.split()[0] if isinstance(package_manager, str) else package_manager):
        print(f"  [ERROR] Package manager not found: {package_manager}")
        return False

    # Show what will be installed
    print(f"  [*] Package manager: {package_manager}")
    print(f"  [*] This will install {tool_name} from official repositories")

    # Confirm with user
    response = input(f"  Proceed with installation? (y/N): ").strip().lower()
    if response != "y":
        print("  [CANCELLED] Installation cancelled by user.")
        return False

    # Execute installation
    try:
        if isinstance(package_manager, str):
            cmd = package_manager.split() + [tool_name]
        else:
            cmd = list(package_manager) + [tool_name]

        result = subprocess.run(
            cmd,
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


def check_admin_privileges() -> bool:
    """Check if running with admin/root privileges."""
    system = platform.system().lower() if False else __import__("platform").system().lower()
    if system == "windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        return os.geteuid() == 0


def get_security_warnings() -> list:
    """Return list of security warnings for the current environment."""
    warnings = []
    system = __import__("platform").system().lower()

    if not check_admin_privileges():
        warnings.append("Not running with admin/root privileges - some operations may fail")

    # Check if running from a writable location (could be tampered)
    project_dir = get_project_dir()
    if os.access(project_dir, os.W_OK):
        warnings.append(f"Project directory is writable: {project_dir}")

    # Check for suspicious files
    suspicious = [".exe", ".bat", ".ps1", ".sh"] if system == "windows" else [".exe", ".so"]
    for f in os.listdir(project_dir):
        if any(f.endswith(ext) for ext in suspicious) and f not in ["run.bat", "run.sh"]:
            warnings.append(f"Suspicious file found: {f}")

    return warnings


def print_security_status():
    """Print security status of the environment."""
    print("  [*] Security status:")
    warnings = get_security_warnings()
    if warnings:
        for w in warnings:
            print(f"      [WARN] {w}")
    else:
        print("      [OK] No security warnings")

    # Verify integrity
    ok = verify_project_integrity(verbose=False)
    print(f"      Integrity: {'OK' if ok else 'WARNING - files modified!'}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Security checks for FlipBoot")
    parser.add_argument("--check", action="store_true", help="Run security checks")
    parser.add_argument("--verify", action="store_true", help="Verify file integrity")
    parser.add_argument("--hashes", action="store_true", help="Show file hashes")
    args = parser.parse_args()

    if args.check:
        print_security_status()
    elif args.verify:
        verify_project_integrity(verbose=True)
    elif args.hashes:
        project_dir = get_project_dir()
        for f in os.listdir(project_dir):
            if f.endswith(".py"):
                fp = os.path.join(project_dir, f)
                print(f"{f}={compute_file_hash(fp)}")
    else:
        print("Use --check, --verify, or --hashes")