# Changelog

All notable changes to FlipBoot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-alpha] - 2026-11-21

### Added
- Initial alpha release of FlipBoot
- Cross-platform support (Windows, Linux, macOS)
- UEFI boot mode detection and switching
- Legacy BIOS boot mode detection and switching
- Beautiful terminal UI with colors, banners, tables, and progress bars
- Interactive menu for OS selection (numbered list)
- Automatic tool detection and installation
- File integrity verification (SHA256)
- Security status reporting
- Automatic elevation (admin/root) at startup
- Cross-OS switching (Linux-to-Linux, Windows-to-Windows, etc.)
- Windows-to-Windows switching via BCD store
- `--list` flag to display available boot entries
- `--reboot` flag for automatic reboot after switching
- `--strict` flag for strict integrity checking
- `--windows-to-windows` flag for Windows version switching
- `run.bat` and `run.sh` launchers
- Comprehensive README with documentation
- MIT License

### Known Issues
- Legacy BIOS on Windows requires manual setup (EasyBCD)
- macOS boot switching requires manual configuration
- Some non-ASCII characters in boot entry names may display incorrectly

### Planned for 0.2.0-alpha
- Improved filtering of boot entries
- Better error messages and recovery
- Unit tests
- CI/CD pipeline
- PyInstaller binary builds