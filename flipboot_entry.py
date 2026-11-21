#!/usr/bin/env python3
"""FlipBoot entry point for PyInstaller and direct execution."""
import os
import sys

# Add src to path if running from source
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if os.path.exists(src_dir) and src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Also handle PyInstaller bundle
if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle
    bundle_dir = sys._MEIPASS
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

from flipboot.main import main

if __name__ == "__main__":
    main()