# Build Instructions

## Prerequisites

- Python 3.8+
- PyInstaller (`pip install pyinstaller`)
- Nuitka (optional, `pip install nuitka`)

## Building Locally

### Windows
```bash
# Install PyInstaller
pip install pyinstaller

# Build
python build.py --clean

# Output: dist/FlipBoot.exe
```

### Linux
```bash
# Install PyInstaller
pip install pyinstaller

# Build
python3 build.py --clean

# Output: dist/FlipBoot
# Make executable
chmod +x dist/FlipBoot
```

### macOS
```bash
# Install PyInstaller
pip install pyinstaller

# Build
python3 build.py --clean

# Output: dist/FlipBoot.app
```

## Build Options

| Option | Description |
|--------|-------------|
| `--clean` | Remove build artifacts before building |
| `--onefile` | Single file executable (default) |
| `--onedir` | Directory-based executable |
| `--nuitka` | Use Nuitka instead of PyInstaller |
| `--all` | Build all platform variants |

## Cross-Platform Builds

For building on all platforms simultaneously, use GitHub Actions:

1. Push a tag: `git tag v0.1.0-alpha && git push origin v0.1.0-alpha`
2. GitHub Actions will build for Windows, Linux, and macOS
3. Download artifacts from the Actions tab
4. Release will be created automatically (as draft)

## Manual Cross-Platform Build

To build for multiple platforms manually:
1. Build on Windows → `dist/FlipBoot.exe`
2. Build on Linux → `dist/FlipBoot`
3. Build on macOS → `dist/FlipBoot.app`
4. Package all three into a release archive

## Build Tips

### Reducing Size
- Use `--upx` for compression (requires UPX)
- Exclude unnecessary modules (already configured)
- Use `--onedir` for faster startup (larger size)

### Debugging
- Add `--debug` flag to PyInstaller for verbose output
- Check `build/` directory for intermediate files
- Use `--log-level DEBUG` for detailed logs

### Code Signing (Optional)
- Windows: Use `signtool` with a code signing certificate
- macOS: Use `codesign` with Apple Developer certificate
- Linux: Use GPG signing

## Troubleshooting

### "Module not found" errors
- Add the module to `--hidden-import` in build.py
- Check if the module is in `src/flipboot/`

### Large executable size
- Check for unnecessary imports
- Use `--exclude-module` for unused packages
- Enable UPX compression

### Slow startup
- Use `--onedir` instead of `--onefile`
- Reduce number of hidden imports
- Profile with `python -m cProfile`