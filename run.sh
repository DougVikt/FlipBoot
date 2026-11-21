#!/bin/bash
# FlipBoot - Cross-OS Boot Switcher (Linux/macOS launcher)
cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found! Please install Python 3.8+"
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Run with root if needed
if [ "$EUID" -ne 0 ]; then
    echo "Requesting root privileges..."
    sudo env PYTHONPATH="$(pwd)/src:$PYTHONPATH" python3 -m flipboot.main "$@"
else
    python3 -m flipboot.main "$@"
fi