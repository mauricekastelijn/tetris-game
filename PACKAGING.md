# Building Executables

This guide explains how to create standalone executables for Tetris Ultimate Edition that can run on machines without Python installed.

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
python build_exe.py
```

The script will:
1. ✓ Check and install PyInstaller if needed
2. ✓ Build the executable using the optimized `tetris.spec` configuration
3. ✓ Verify the output
4. ✓ Report the executable location and size

**Output**: 
- Windows: `dist/tetris.exe`
- Linux/macOS: `dist/tetris`

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

### Using build_exe.py

```bash
# Clean build (removes previous build artifacts)
python build_exe.py --clean

# Build with console window (for debugging)
python build_exe.py --console

# Build without using spec file
python build_exe.py --no-spec

# Combine options
python build_exe.py --clean --console
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
│   └── tetris(.exe)   # Final executable (distribute this)
├── tetris.spec         # Build configuration
└── build_exe.py            # Build script
```

### Cleaning Up

```bash
# Manual cleanup
rm -rf build/ dist/

# Or use the build script
python build_exe.py --clean
```

## Distribution

### Single File Distribution

The executables are completely standalone:
- ✓ No Python installation required
- ✓ All dependencies bundled
- ✓ No additional files needed
- ✓ Can be run from any location

### Creating a Release Package

For professional distribution:

```bash
# Windows
zip -r tetris-windows-x64.zip dist/tetris.exe

# Linux
tar -czf tetris-linux-x64.tar.gz dist/tetris

# macOS
tar -czf tetris-macos-x64.tar.gz dist/tetris
```

## Automated Builds (CI/CD)

The repository includes GitHub Actions workflows for automated builds:

### Build Executables Workflow

The `.github/workflows/build-executables.yml` workflow automatically builds executables for both Windows and Linux platforms **on a single Ubuntu runner**:

- **Triggered on**: Pushes to main, pull requests, tags (releases)
- **Build Host**: Ubuntu (Linux) runner only
- **Platforms**: Windows and Linux executables
- **Method**: 
  - Linux: Native PyInstaller build
  - Windows: Cross-compilation using Docker with Wine (cdrx/pyinstaller-windows image)
- **Artifacts**: Uploaded as GitHub artifacts for 30 days
- **Releases**: Automatically attached to GitHub releases when tagged

#### Download Pre-built Executables

1. Go to the [Actions tab](../../actions/workflows/build-executables.yml)
2. Click on the latest successful workflow run
3. Download the artifact for your platform:
   - `tetris-linux` - Linux executable
   - `tetris-windows` - Windows executable

#### Creating a Release

To create a release with executables:

```bash
# Tag a new version
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

The workflow will automatically:
1. Build executables for Windows and Linux on Ubuntu runner
2. Create compressed archives (`.zip` for Windows, `.tar.gz` for Linux)
3. Attach them to the GitHub release

## Platform-Specific Builds

### Building on Windows
```bash
python build_exe.py
# Output: dist/tetris.exe
```

### Building on Linux
```bash
python build_exe.py
# Output: dist/tetris
```

### Building on macOS
```bash
python build_exe.py
# Output: dist/tetris
```

### Cross-Platform Build (Linux → Windows)

To build Windows executables on Linux, use Docker with Wine:

```bash
# Using the cdrx/pyinstaller-windows Docker image
docker run --rm \
  -v "$(pwd):/src" \
  cdrx/pyinstaller-windows:python3-amd64 \
  "pip install -r requirements.txt && pyinstaller tetris.spec"
```

This method is used by the CI/CD workflow to create Windows executables on Ubuntu runners.

**Note**: While PyInstaller typically requires building on the target platform, the GitHub Actions workflow uses Docker with Wine to enable Windows builds on Linux runners. For local development, it's recommended to build on the native platform for best results.

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
- [Pygame and PyInstaller](https://github.com/pygame/pygame/wiki/Distributing-pygame-apps)
