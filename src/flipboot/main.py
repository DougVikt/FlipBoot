#!/usr/bin/env python3
"""FlipBoot - Cross-platform boot switcher between any OS."""
import argparse
import os
import platform
import sys

# ---- Request elevation at the very beginning -----------------------------
def _ensure_elevated():
    """Ensure the script runs with admin/root privileges. Re-launch if needed."""
    system = platform.system().lower()

    if system == "windows":
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                return True
        except Exception:
            pass

        print("  [*] Requesting administrator privileges...")
        try:
            import ctypes
            # Build the command line: script path + arguments
            script_path = os.path.abspath(sys.argv[0])
            args = [f'"{script_path}"'] + [f'"{a}"' for a in sys.argv[1:]]
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(args), os.path.dirname(script_path), 1
            )
            sys.exit(0)
        except Exception as e:
            print(f"  [ERROR] Failed to elevate: {e}")
            print("  Please run this script as Administrator.")
            sys.exit(1)

    elif system == "linux" or system == "darwin":
        if os.geteuid() == 0:
            return True

        print("  [*] Requesting root privileges...")
        try:
            script_path = os.path.abspath(sys.argv[0])
            os.execvp("sudo", ["sudo", sys.executable, script_path] + sys.argv[1:])
        except Exception as e:
            print(f"  [ERROR] Failed to elevate: {e}")
            print("  Please run this script with sudo.")
            sys.exit(1)

    return True


_ensure_elevated()

try:
    from .detector import detect_boot_mode, list_boot_entries
    from .tool_checker import check_and_install
    from .security import verify_project_integrity, print_security_status
    from .uefi_strategy import switch_boot_uefi
    from .legacy_strategy import switch_boot_legacy
    from .ui import (print_banner, print_section, print_step, print_success, print_error,
                    print_warning, print_info, print_entry, print_progress, print_table,
                    print_footer, ask_yes_no, ask_choice)
except ImportError:
    from detector import detect_boot_mode, list_boot_entries
    from tool_checker import check_and_install
    from security import verify_project_integrity, print_security_status
    from uefi_strategy import switch_boot_uefi
    from legacy_strategy import switch_boot_legacy
    from ui import (print_banner, print_section, print_step, print_success, print_error,
                    print_warning, print_info, print_entry, print_progress, print_table,
                    print_footer, ask_yes_no, ask_choice)


def main():
    parser = argparse.ArgumentParser(
        description="Switch next boot to any OS - works on UEFI and Legacy BIOS"
    )
    parser.add_argument(
        "-t", "--target",
        default="",
        help="Text to match boot entry (e.g.: kali, ubuntu, 'Windows 11', 'Windows 10')",
    )
    parser.add_argument(
        "-r", "--reboot",
        action="store_true",
        help="Reboot immediately after switching",
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available boot entries and exit",
    )
    parser.add_argument(
        "--windows-to-windows",
        action="store_true",
        help="Switch between Windows installations (use with --target for Windows version)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Abort if integrity check fails",
    )
    parser.add_argument(
        "--no-menu",
        action="store_true",
        help="Skip interactive menu (use with --target)",
    )
    args = parser.parse_args()

    print_banner()

    # Security check
    print_section("Security Check")
    print_step("Running security checks...", "info")
    integrity_ok = verify_project_integrity(verbose=False)
    if not integrity_ok:
        print_warning("Project files may have been modified!")
        if args.strict:
            print_error("Integrity check failed. Aborting (--strict mode).")
            sys.exit(1)
        print_info("Continuing anyway (use --strict to abort on integrity failure)")
    print_security_status()
    print()

    # Detect boot mode
    print_section("Boot Mode Detection")
    print_step("Detecting boot mode...", "info")
    try:
        mode = detect_boot_mode()
    except RuntimeError as e:
        print_error(str(e))
        sys.exit(1)

    print_step(f"Boot mode: {mode.upper()}", "ok")
    print()

    # Read boot entries
    print_section("Available Boot Entries")
    print_step("Reading boot entries...", "info")
    print()
    entries = list_boot_entries(mode)
    if not entries:
        print_warning("No boot entries found.")
        print_footer()
        sys.exit(1)

    # Display entries as numbered list
    for i, entry in enumerate(entries, 1):
        print_entry(i, entry["name"], entry["guid"], entry.get("disk", ""))
    print()

    # Interactive menu (unless --no-menu or --target provided)
    if args.target and args.no_menu:
        target = args.target
        windows_to_windows = args.windows_to_windows
    elif args.target and not args.no_menu:
        # Target provided but still show menu for confirmation
        target = args.target
        windows_to_windows = args.windows_to_windows
    else:
        # Interactive mode: ask user to choose
        print_info("Enter the number of the OS you want to boot into:")
        print_info("Or type 'q' to quit, 'r' to reboot after switching")
        print()

        while True:
            choice = input("  Your choice: ").strip().lower()

            if choice == "q":
                print_info("Cancelled by user.")
                print_footer()
                sys.exit(0)

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(entries):
                    selected = entries[idx]
                    target = selected["name"]
                    # Auto-detect windows-to-windows
                    windows_to_windows = selected.get("type") == "windows_bcd" or "BCD" in selected["name"]

                    # Ask if user wants to reboot
                    if not args.reboot:
                        reboot = ask_yes_no("Reboot after switching?", default=True)
                    else:
                        reboot = True
                    break
                else:
                    print_error(f"Invalid choice. Enter a number between 1 and {len(entries)}.")
            except ValueError:
                print_error("Please enter a valid number.")

    # Check and install required tools
    print_section("Tool Check")
    print_step("Checking required tools...", "info")
    if not check_and_install(mode):
        print()
        print_error("Cannot proceed without required tools.")
        print_info("Please install them manually and try again.")
        print_footer()
        sys.exit(1)
    print_step("All required tools available", "ok")
    print()

    # Switch based on mode
    print_section("Boot Switch")
    if mode == "uefi":
        print_step(f"Switching to: {target}", "info")
        success = switch_boot_uefi(
            target=target,
            reboot=reboot,
            windows_to_windows=windows_to_windows,
        )
    else:
        print_step(f"Switching to: {target}", "info")
        success = switch_boot_legacy(
            target=target,
            reboot=reboot,
            windows_to_windows=windows_to_windows,
        )

    if not success:
        print()
        print_error("Could not switch boot automatically.")
        print()
        print_info("Tips:")
        print("  - Try a different entry number")
        print("  - Check if the target OS is installed")
        print("  - For Windows-to-Windows, the entry must be in BCD store")
        print_footer()
        sys.exit(1)

    print_success(f"Boot switched to '{target}'!")
    if reboot:
        print_info("Rebooting in 5 seconds... (close window to cancel)")
    print_footer()


if __name__ == "__main__":
    main()