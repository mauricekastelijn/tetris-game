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

## Testing the Executable

### Local Testing

```bash
# Run the executable
./dist/tetris.exe

# Or on Windows
dist\tetris.exe
```

**Test checklist**:
- [ ] Executable launches without errors
- [ ] Game window appears with correct size
- [ ] All controls work (arrows, space, C, P, G, R, ESC)
- [ ] Ghost piece displays correctly
- [ ] Hold piece works
- [ ] Line clearing animation works
- [ ] Scoring updates correctly
- [ ] Game over screen appears
- [ ] No console window appears (unless built with --console)

### Testing on Clean Machine

For production testing, test on a Windows machine **without Python installed**:

1. Copy `dist/tetris.exe` to the target machine
2. Run the executable
3. Verify all functionality works
4. Check for any missing dependencies or errors

## Troubleshooting

### ModuleNotFoundError: No module named 'src'

**Solution**: The build is missing hidden imports. This is fixed by:
- Using the `tetris.spec` file (includes all required hidden imports)
- Or adding `--hidden-import src.modulename` flags

### Executable Size Too Large

The executable will be ~15-25 MB due to Python runtime and Pygame.

To optimize:
```bash
# Enable UPX compression (already in tetris.spec)
pyinstaller tetris.spec  # UPX is enabled by default

# Or install UPX separately for better compression
# Download from: https://github.com/upx/upx/releases
```

### Console Window Appears

**Solution**: Make sure `console=False` in `tetris.spec` or use `--windowed` flag.

### Missing DLL Errors

If you get DLL errors on target machine:
1. Install [Microsoft Visual C++ Redistributable for Visual Studio 2015-2022](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
2. Or build on a machine with minimal DLL dependencies

### Game Crashes on Startup

**Debug steps**:
1. Build with console enabled: `python build.py --console`
2. Run executable and check console output
3. Check if Pygame dependencies are included
4. Verify all hidden imports are in `tetris.spec`

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

## Continuous Integration

The repository includes a GitHub Actions workflow that can build executables automatically.

To enable executable builds in CI:
1. Add PyInstaller to the workflow
2. Use the build script in the workflow
3. Upload the executable as an artifact

Example workflow step:
```yaml
- name: Build executable
  run: python build.py --clean

- name: Upload executable
  uses: actions/upload-artifact@v3
  with:
    name: tetris-executable
    path: dist/tetris.exe
```

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

## Advanced Configuration

### Including Additional Resources

If you add assets (images, sounds, fonts) in the future:

Edit `tetris.spec`:
```python
datas=[
    ('assets/', 'assets'),
    ('fonts/', 'fonts'),
],
```

### Multi-File Distribution

If you prefer multiple files instead of a single executable:

Edit `tetris.spec` to create a directory bundle:
```python
# Change EXE to:
exe = EXE(
    pyz,
    a.scripts,
    # Don't include these in EXE:
    # a.binaries,
    # a.zipfiles,
    # a.datas,
    exclude_binaries=True,  # Add this
    name='tetris',
    # ... rest of config
)

# Add COLLECT step:
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='tetris',
)
```

## Version Information

To add version information to the executable, create a `version.txt` file and reference it in `tetris.spec`.

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review PyInstaller documentation: https://pyinstaller.org/
3. Open an issue on GitHub with:
   - Build command used
   - Error messages
   - Python version
   - Operating system

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
- [Pygame and PyInstaller](https://github.com/pygame/pygame/wiki/Distributing-pygame-apps)
