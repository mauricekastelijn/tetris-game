#!/usr/bin/env python3
"""
Build script for creating Windows executable of Tetris Ultimate Edition

This script automates the process of building a standalone executable using PyInstaller.
It ensures all dependencies are installed, runs the build process, and verifies the output.

Usage:
    python build.py [--clean] [--onefile] [--console]

Options:
    --clean     Clean build artifacts before building
    --onefile   Build as a single executable file (default)
    --console   Show console window (for debugging)
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check if required build dependencies are installed."""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
        return

    print("✓ PyInstaller is installed")


def clean_build_artifacts():
    """Remove previous build artifacts."""
    print("\nCleaning build artifacts...")
    artifacts = ["build", "dist", "__pycache__"]

    for artifact in artifacts:
        artifact_path = Path(artifact)
        if artifact_path.exists():
            print(f"  Removing {artifact}/")
            shutil.rmtree(artifact_path)

    # Remove auto-generated spec files, keep tetris.spec
    for spec_file in Path(".").glob("*.spec"):
        if spec_file.name != "tetris.spec":
            print(f"  Removing {spec_file}")
            spec_file.unlink()

    print("✓ Build artifacts cleaned")


def build_executable(use_spec=True, show_console=False):
    """Build the executable using PyInstaller.

    Args:
        use_spec: Use the tetris.spec file (recommended)
        show_console: Show console window in the executable
    """
    print("\nBuilding executable...")

    if use_spec and Path("tetris.spec").exists():
        # Use the spec file for consistent builds
        cmd = [sys.executable, "-m", "PyInstaller", "tetris.spec"]
        if show_console:
            print("  Note: To enable console, edit tetris.spec and set console=True")
        print("  Using tetris.spec configuration")
    else:
        # Fallback to command-line build
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--name",
            "tetris",
            "--hidden-import",
            "src",
            "--hidden-import",
            "src.config",
            "--hidden-import",
            "src.game_states",
            "--hidden-import",
            "src.tetromino",
        ]

        if not show_console:
            cmd.append("--windowed")

        cmd.append("src/tetris.py")
        print("  Using command-line configuration")

    print(f"  Running: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print("\n✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error code {e.returncode}")
        return False


def verify_build():
    """Verify the build output exists."""
    # Platform-specific executable name
    if sys.platform == "win32":
        exe_path = Path("dist/tetris.exe")
    else:
        exe_path = Path("dist/tetris")

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Executable created: {exe_path}")
        print(f"  Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"\n✗ Expected executable not found: {exe_path}")
        return False


def main():
    """Main build process."""
    parser = argparse.ArgumentParser(description="Build Tetris Ultimate Edition executable")
    parser.add_argument(
        "--clean", action="store_true", help="Clean build artifacts before building"
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        default=True,
        help="Build as single executable file (default)",
    )
    parser.add_argument(
        "--console", action="store_true", help="Show console window (for debugging)"
    )
    parser.add_argument(
        "--no-spec", action="store_true", help="Don't use tetris.spec, build from command line"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Tetris Ultimate Edition - Build Script")
    print("=" * 60)

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"\nWorking directory: {Path.cwd()}")

    # Check dependencies
    check_dependencies()

    # Clean if requested
    if args.clean:
        clean_build_artifacts()

    # Build executable
    use_spec = not args.no_spec
    success = build_executable(use_spec=use_spec, show_console=args.console)

    if success:
        # Verify build
        if verify_build():
            print("\n" + "=" * 60)
            print("Build Process Complete!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Test the executable: dist/tetris.exe")
            print("2. Distribute the executable to users")
            print("\nNote: The executable is standalone and doesn't require Python")
            return 0

    print("\n✗ Build process failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
