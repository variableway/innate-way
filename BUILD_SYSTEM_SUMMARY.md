# Build System Summary

## Overview

Complete build system for Capture TUI supporting both **Go** and **Python** versions across **Windows**, **macOS**, and **Linux**.

---

## Build Files Created

### Taskfile (Task Runner)

| File | Description |
|------|-------------|
| `Taskfile.yml` | Main task runner configuration with targets for all platforms |

**Key Tasks:**
```bash
task build:go              # Build Go for current platform
task build:go:all          # Build Go for all platforms
task build:python          # Build Python for current platform
task build:python:all      # Build Python for all platforms (with Docker)
task test                  # Run all tests
task lint                  # Run all linters
task release               # Full release build
task clean                 # Clean build artifacts
```

### Build Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `scripts/build-go.sh` | macOS/Linux | Build Go application |
| `scripts/build-go.bat` | Windows | Build Go application |
| `scripts/build-python.sh` | macOS/Linux | Build Python CLI with PyInstaller |
| `scripts/build-python.bat` | Windows | Build Python CLI with PyInstaller |

### PyInstaller Spec

| File | Description |
|------|-------------|
| `scripts/capture-python.spec` | PyInstaller configuration for standalone Python executable |

### Build Documentation

| File | Description |
|------|-------------|
| `BUILD.md` | Comprehensive build guide |

---

## Supported Platforms

### Go Application

| OS | Architectures | Method |
|----|---------------|--------|
| macOS | Intel (x86_64), Apple Silicon (ARM64), Universal | Native or cross-compile |
| Linux | AMD64, ARM64, 386 | Native or cross-compile |
| Windows | AMD64, ARM64, 386 | Cross-compile |
| FreeBSD | AMD64 | Cross-compile |

### Python Application

| OS | Architectures | Method |
|----|---------------|--------|
| macOS | Intel, Apple Silicon | Native only |
| Linux | AMD64 | Native or Docker |
| Windows | AMD64 | Native or Docker |

---

## Usage Examples

### Using Task (Recommended)

```bash
# Install Task
curl -sL https://taskfile.dev/install.sh | sh

# Build Go for current platform
task build:go

# Build Go for all platforms
task build:go:all

# Build Python for current platform
task build:python

# Full release with packaging
task release
```

### Using Shell Scripts (macOS/Linux)

```bash
# Build Go for all platforms
./scripts/build-go.sh all

# Build Python for current platform
./scripts/build-python.sh current

# Build for specific platform
./scripts/build-go.sh macos
./scripts/build-go.sh linux
./scripts/build-go.sh windows

# Package builds
./scripts/build-go.sh package
./scripts/build-python.sh package

# Install locally
./scripts/build-go.sh install

# Run tests
./scripts/build-go.sh test
./scripts/build-python.sh test

# Clean
./scripts/build-go.sh clean
./scripts/build-python.sh clean
```

### Using Batch Scripts (Windows)

```cmd
:: Build Go for current platform
scripts\build-go.bat current

:: Build Go for all platforms
scripts\build-go.bat all

:: Build Python
scripts\build-python.bat current

:: Install locally
scripts\build-go.bat install

:: Run tests
scripts\build-go.bat test

:: Clean
scripts\build-go.bat clean
```

---

## Output Structure

```
dist/
├── capture-darwin-amd64          # macOS Intel
├── capture-darwin-arm64          # macOS Apple Silicon
├── capture-darwin-amd64-1.0.0.tar.gz
├── capture-darwin-arm64-1.0.0.tar.gz
├── capture-linux-amd64           # Linux AMD64
├── capture-linux-arm64           # Linux ARM64
├── capture-linux-386             # Linux 386
├── capture-linux-amd64-1.0.0.tar.gz
├── capture-linux-arm64-1.0.0.tar.gz
├── capture-windows-amd64.exe     # Windows AMD64
├── capture-windows-arm64.exe     # Windows ARM64
├── capture-windows-386.exe       # Windows 386
├── capture-windows-amd64-1.0.0.zip
├── capture-windows-arm64-1.0.0.zip
├── capture-python                # Python macOS/Linux
├── capture-python.exe            # Python Windows
└── capture-1.0.0-checksums.txt   # SHA256 checksums
```

---

## Cross-Compilation

### Go (Native Support)

```bash
# From any platform, build for any platform
GOOS=windows GOARCH=amd64 go build -o capture.exe ./cmd/capture
GOOS=linux GOARCH=arm64 go build -o capture ./cmd/capture
GOOS=darwin GOARCH=amd64 go build -o capture ./cmd/capture
```

### Python (Docker Required)

```bash
# Build Linux binary from macOS/Windows
./scripts/build-python.sh linux

# Build Windows binary from macOS/Linux
./scripts/build-python.sh windows
```

---

## Prerequisites

### All Platforms

- Git

### Go Builds

- Go 1.21 or later

### Python Builds

- Python 3.9 or later
- pip or uv
- PyInstaller (`pip install pyinstaller`)
- Docker (for cross-compilation)

### Windows-Specific

- Git Bash or WSL (for shell scripts)
- Or use `.bat` files in Command Prompt

---

## Quick Reference

| Action | Command |
|--------|---------|
| **Go - Current Platform** | `task build:go` or `./scripts/build-go.sh current` |
| **Go - All Platforms** | `task build:go:all` or `./scripts/build-go.sh all` |
| **Python - Current** | `task build:python` or `./scripts/build-python.sh current` |
| **Package** | `task package` or `./scripts/build-go.sh package` |
| **Test** | `task test` |
| **Lint** | `task lint` |
| **Clean** | `task clean` |
| **Full Release** | `task release` |

---

## Troubleshooting

### Go Issues

```bash
# Missing dependencies
cd capture-tui-go && go mod download

# Clean cache
./scripts/build-go.sh clean
```

### Python Issues

```bash
# Install dependencies
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"
```

### Permission Denied (Unix)

```bash
chmod +x scripts/*.sh
```

---

## CI/CD Ready

All scripts are designed to work in CI/CD environments:

```yaml
# GitHub Actions example
- name: Build Go
  run: ./scripts/build-go.sh all

- name: Build Python
  run: |
    pip install -e ".[dev]"
    ./scripts/build-python.sh current

- name: Upload artifacts
  uses: actions/upload-artifact@v3
  with:
    path: dist/*
```

---

**Build system is ready!** 🚀

```bash
# Quick start
task build:go:all
task build:python
task release
```
