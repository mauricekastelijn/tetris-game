# Building Windows Executable

This guide explains how to create a standalone Windows executable for Tetris Ultimate Edition that can run on machines without Python installed.

## Requirements

- **Python**: 3.8 or higher
- **PyInstaller**: Installed automatically by build script, or manually with:
  ```bash
  pip install pyinstaller
  ```
- **Dependencies**: All game dependencies from `requirements.txt`

## Quick Build

### Method 1: Using the Build Script (Recommended)

The easiest way to build the executable:

```bash
# Install dependencies first
pip install -r requirements.txt

# Run the build script
python build.py
```

The script will:
1. ✓ Check and install PyInstaller if needed
2. ✓ Build the executable using the optimized `tetris.spec` configuration
3. ✓ Verify the output
4. ✓ Report the executable location and size

**Output**: `dist/tetris.exe`

### Method 2: Using PyInstaller Directly

If you prefer manual control:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build using the spec file (recommended)
pyinstaller tetris.spec

# OR build with command-line options
pyinstaller --onefile --windowed --name tetris \
  --hidden-import src \
  --hidden-import src.config \
  --hidden-import src.game_states \
  --hidden-import src.tetromino \
  src/tetris.py
```

## Build Options

### Using build.py

```bash
# Clean build (removes previous build artifacts)
python build.py --clean

# Build with console window (for debugging)
python build.py --console

# Build without using spec file
python build.py --no-spec

# Combine options
python build.py --clean --console
```

### Editing tetris.spec

For advanced customization, edit `tetris.spec`:

```python
# Show console window for debugging
console=True,  # Change from False to True

# Add an icon
icon='path/to/icon.ico',  # Uncomment and set path

# Include additional data files
datas=[
    ('path/to/assets', 'assets'),  # (source, destination)
],
```

After editing, rebuild:
```bash
pyinstaller tetris.spec
```

## Build Artifacts

After building, you'll see:

```
tetris-game/
├── build/              # Temporary build files (can be deleted)
├── dist/
│   └── tetris.exe     # Final executable (distribute this)
├── tetris.spec         # Build configuration
└── build.py            # Build script
```

### Cleaning Up

```bash
# Manual cleanup
rm -rf build/ dist/

# Or use the build script
python build.py --clean
```

## Distribution

### Single File Distribution

The executable in `dist/tetris.exe` is completely standalone:
- ✓ No Python installation required
- ✓ All dependencies bundled
- ✓ No additional files needed
- ✓ Can be run from any location

### Creating a Release Package

For professional distribution:

```bash
# Create a release folder
mkdir tetris-release
cp dist/tetris.exe tetris-release/
cp README.md tetris-release/
cp LICENSE tetris-release/

# Create a zip archive
zip -r tetris-ultimate-v1.0.zip tetris-release/
```

Or use the release workflow in `.github/workflows/` for automated releases.

## Platform-Specific Builds

### Windows
```bash
python build.py
# Output: dist/tetris.exe
```

### macOS
```bash
pyinstaller tetris.spec
# Output: dist/tetris (or tetris.app if configured)
```

### Linux
```bash
pyinstaller tetris.spec
# Output: dist/tetris
```

**Note**: Executables are platform-specific. Build on the target OS or use cross-compilation tools.

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
- [Pygame and PyInstaller](https://github.com/pygame/pygame/wiki/Distributing-pygame-apps)
