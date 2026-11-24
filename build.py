#!/usr/bin/env python3
"""Build script for FlipBoot executables.

Usage:
    python build.py                    # Build for current platform
    python build.py --clean            # Clean build artifacts first
    python build.py --onefile          # Single file executable
    python build.py --onedir           # Directory-based executable
    python build.py --all              # Build all platform variants (requires all tools)

Requirements:
    pip install pyinstaller
    pip install nuitka  (optional, for faster builds)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
DIST_DIR = os.path.join(PROJECT_DIR, "dist")
SRC_DIR = os.path.join(PROJECT_DIR, "src")


def clean():
    """Remove build artifacts."""
    for d in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(d):
            print(f"  [*] Removing {d}...")
            shutil.rmtree(d)
    # Remove .spec build artifacts
    for f in os.listdir(PROJECT_DIR):
        if f.endswith(".spec") and f != "flipboot.spec":
            os.remove(os.path.join(PROJECT_DIR, f))
    print("  [OK] Cleaned.")


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"  [OK] PyInstaller {PyInstaller.__version__} found.")
        return True
    except ImportError:
        print("  [ERROR] PyInstaller not found. Install with: pip install pyinstaller")
        return False


def build_pyinstaller(onefile: bool = True, onedir: bool = False):
    """Build executable using PyInstaller."""
    system = platform.system().lower()

    print(f"\n  Building for {system}...")

    # Base command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
    ]

    # One file or one dir
    if onefile:
        cmd.append("--onefile")
    if onedir:
        cmd.append("--onedir")

    # Console app
    cmd.append("--console")

    # Name
    cmd.extend(["--name", "FlipBoot"])

    # Icon
    icon_path = None
    if system == "windows" and os.path.exists(os.path.join(PROJECT_DIR, "assets", "icon.ico")):
        icon_path = os.path.join(PROJECT_DIR, "assets", "icon.ico")
    elif system == "darwin" and os.path.exists(os.path.join(PROJECT_DIR, "assets", "icon.icns")):
        icon_path = os.path.join(PROJECT_DIR, "assets", "icon.icns")

    if icon_path:
        cmd.extend(["--icon", icon_path])

    # Version info (Windows only)
    if system == "windows" and os.path.exists(os.path.join(PROJECT_DIR, "version_info.txt")):
        cmd.extend(["--version-file", "version_info.txt"])

    # Hidden imports
    hidden_imports = [
        "flipboot", "flipboot.main", "flipboot.ui", "flipboot.detector",
        "flipboot.security", "flipboot.tool_checker", "flipboot.uefi_strategy",
        "flipboot.legacy_strategy", "ctypes", "subprocess", "platform",
        "hashlib", "urllib.request",
    ]
    for hi in hidden_imports:
        cmd.extend(["--hidden-import", hi])

    # Exclude unnecessary modules
    excludes = [
        "tkinter", "matplotlib", "numpy", "pandas", "scipy", "PIL",
        "PyQt5", "PyQt6", "wx", "test", "tests",
    ]
    for ex in excludes:
        cmd.extend(["--exclude-module", ex])

    # UPX compression (only if UPX is available)
    upx_available = os.path.exists("/usr/bin/upx") or os.path.exists("C:\\upx") or shutil.which("upx")
    if upx_available:
        cmd.append("--upx")
    else:
        cmd.append("--noupx")

    # Entry point
    cmd.append("flipboot_entry.py")

    # Set PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")

    print(f"  [*] Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=PROJECT_DIR, env=env)

    if result.returncode == 0:
        print()
        print("  [OK] Build successful!")
        _print_build_info(system)
    else:
        print()
        print("  [ERROR] Build failed!")
        sys.exit(1)


def _print_build_info(system: str):
    """Print information about the built executable."""
    if system == "windows":
        exe_path = os.path.join(DIST_DIR, "FlipBoot.exe")
    elif system == "darwin":
        exe_path = os.path.join(DIST_DIR, "FlipBoot.app")
    else:
        exe_path = os.path.join(DIST_DIR, "FlipBoot")

    if os.path.exists(exe_path):
        if os.path.isfile(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"  Executable: {exe_path}")
            print(f"  Size: {size:.2f} MB")
        else:
            print(f"  Bundle: {exe_path}")
    else:
        print(f"  Output: {DIST_DIR}")


def build_nuitka():
    """Build executable using Nuitka (optional, faster)."""
    print("\n  Building with Nuitka...")
    try:
        import nuitka
    except ImportError:
        print("  [ERROR] Nuitka not found. Install with: pip install nuitka")
        sys.exit(1)

    system = platform.system().lower()
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--console",
        "--output-filename=FlipBoot",
        f"--output-dir={DIST_DIR}",
        "--include-package=flipboot",
        "--nofollow-import-to=tkinter,matplotlib,numpy,pandas",
        os.path.join("src", "flipboot", "main.py"),
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(cmd, cwd=PROJECT_DIR, env=env)

    if result.returncode == 0:
        print("  [OK] Nuitka build successful!")
    else:
        print("  [ERROR] Nuitka build failed!")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build FlipBoot executables")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts first")
    parser.add_argument("--onefile", action="store_true", default=True, help="Single file executable (default)")
    parser.add_argument("--onedir", action="store_true", help="Directory-based executable")
    parser.add_argument("--nuitka", action="store_true", help="Use Nuitka instead of PyInstaller")
    parser.add_argument("--all", action="store_true", help="Build all platform variants")
    args = parser.parse_args()

    print("=" * 60)
    print("  FlipBoot Build System")
    print("=" * 60)
    print()

    if args.clean:
        clean()
        print()

    if args.all:
        print("  [INFO] Cross-platform builds require building on each OS.")
        print("  [INFO] Use GitHub Actions for automated multi-platform builds.")
        print("  [INFO] Building for current platform only...")
        print()

    if args.nuitka:
        if not check_nuitka():
            sys.exit(1)
        build_nuitka()
    else:
        if not check_pyinstaller():
            sys.exit(1)
        build_pyinstaller(onefile=not args.onedir, onedir=args.onedir)

    print()
    print("=" * 60)
    print("  Build complete!")
    print("=" * 60)


def check_nuitka():
    try:
        import nuitka
        print(f"  [OK] Nuitka found.")
        return True
    except ImportError:
        print("  [ERROR] Nuitka not found. Install with: pip install nuitka")
        return False


if __name__ == "__main__":
    main()