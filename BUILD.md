# Build Guide for Capture TUI

This guide covers building Capture TUI for both Go and Python versions across Windows, macOS, and Linux.

## Quick Start

### Using Task (Recommended)

```bash
# Install Task if not already installed
# macOS/Linux: sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
# Windows: choco install go-task or scoop install task

# Build Go for current platform
task build:go

# Build Go for all platforms
task build:go:all

# Build Python for current platform
task build:python

# Run all builds and package
task release
```

### Using Shell Scripts

```bash
# Build Go
./scripts/build-go.sh all

# Build Python
./scripts/build-python.sh all

# Package builds
./scripts/build-go.sh package
```

### Using Batch Scripts (Windows)

```cmd
:: Build Go
scripts\build-go.bat all

:: Build Python
scripts\build-python.bat current
```

---

## Go Application Build

### Prerequisites

- Go 1.21 or later
- Git

### Build Commands

```bash
# Navigate to Go directory
cd capture-tui-go

# Build for current platform
go build -o ../dist/capture ./cmd/capture

# Using the build script
cd ..
./scripts/build-go.sh current    # Current platform
./scripts/build-go.sh macos      # macOS only
./scripts/build-go.sh linux      # Linux only
./scripts/build-go.sh windows    # Windows only
./scripts/build-go.sh all        # All platforms
```

### Supported Platforms

| Platform | Architecture | Output Name |
|----------|--------------|-------------|
| macOS | Intel (x86_64) | `capture-darwin-amd64` |
| macOS | Apple Silicon (ARM64) | `capture-darwin-arm64` |
| Linux | AMD64 | `capture-linux-amd64` |
| Linux | ARM64 | `capture-linux-arm64` |
| Linux | 386 | `capture-linux-386` |
| Windows | AMD64 | `capture-windows-amd64.exe` |
| Windows | ARM64 | `capture-windows-arm64.exe` |
| Windows | 386 | `capture-windows-386.exe` |
| FreeBSD | AMD64 | `capture-freebsd-amd64` |

### Build with Version

```bash
VERSION=2.0.0 ./scripts/build-go.sh all
```

### Install Locally

```bash
# Install to $GOPATH/bin
./scripts/build-go.sh install

# Or manually
cd capture-tui-go
go install ./cmd/capture
```

---

## Python Application Build

### Prerequisites

- Python 3.9 or later
- pip or uv
- PyInstaller (for standalone executables)

### Build Commands

```bash
# Setup environment
pip install -e ".[dev]"
# or
uv pip install -e ".[dev]"

# Build for current platform using Task
task build:python

# Using the build script
./scripts/build-python.sh current    # Current platform
./scripts/build-python.sh macos      # macOS (on macOS only)
./scripts/build-python.sh linux      # Linux (on Linux or Docker)
./scripts/build-python.sh windows    # Windows (using Docker)
./scripts/build-python.sh all        # All platforms (requires Docker)
```

### Building for Different Platforms

#### macOS

```bash
# Native build (creates both Intel and Apple Silicon binaries)
./scripts/build-python.sh macos
```

#### Linux

```bash
# Native build on Linux
./scripts/build-python.sh linux

# Cross-compile using Docker (on macOS/Windows)
./scripts/build-python.sh linux
```

#### Windows

```cmd
:: On Windows
scripts\build-python.bat current

:: Using Docker on macOS/Linux
./scripts/build-python.sh windows
```

### Standalone Executable

The build creates a standalone executable using PyInstaller:

```bash
# Output location
dist/
├── capture-python                    # macOS/Linux
├── capture-python.exe               # Windows
└── ...
```

---

## Cross-Compilation

### Go Cross-Compilation

Go supports easy cross-compilation using environment variables:

```bash
# Build for Windows on macOS/Linux
GOOS=windows GOARCH=amd64 go build -o capture.exe ./cmd/capture

# Build for Linux on macOS/Windows
GOOS=linux GOARCH=amd64 go build -o capture ./cmd/capture

# Build for macOS on Linux/Windows
GOOS=darwin GOARCH=amd64 go build -o capture ./cmd/capture
```

### Python Cross-Compilation

Python requires Docker for cross-compilation:

```bash
# Windows from macOS/Linux
./scripts/build-python.sh windows

# Linux from macOS/Windows
./scripts/build-python.sh linux
```

---

## Packaging

### Automatic Packaging

```bash
# Package Go builds
./scripts/build-go.sh package

# Package Python builds
./scripts/build-python.sh package
```

This creates:
- `.tar.gz` archives for Unix binaries
- `.zip` archives for Windows binaries
- `checksums.txt` with SHA256 hashes

### Output Structure

```
dist/
├── capture-darwin-amd64-1.0.0.tar.gz
├── capture-darwin-arm64-1.0.0.tar.gz
├── capture-linux-amd64-1.0.0.tar.gz
├── capture-linux-arm64-1.0.0.tar.gz
├── capture-windows-amd64-1.0.0.zip
├── capture-1.0.0-checksums.txt
└── ...
```

---

## Docker Builds

### Python Docker Build

```bash
# Linux
mkdir -p dist
docker run --rm -v "$PWD:/src" -w /src python:3.11-slim bash -c "
    pip install pyinstaller
    pip install -e .
    pyinstaller --clean --onefile --name capture-python-linux-amd64 \\
        --distpath dist --workpath build scripts/capture-python.spec
"

# Windows (using Wine)
docker run --rm -v "$PWD:/src" -w /src cdrx/pyinstaller-windows:python3 \\
    pyinstaller --clean --onefile --name capture-python-windows-amd64.exe \\
        --distpath dist --workpath build scripts/capture-python.spec
```

---

## Development

### Run in Development Mode

```bash
# Go
cd capture-tui-go
go run ./cmd/capture --help

# Or using Task
task dev:go

# Python
source .venv/bin/activate
capture --help

# Or using Task
task dev:python
```

### Testing

```bash
# Go tests
task test:go
# or
cd capture-tui-go
go test -v ./...

# Python tests
task test:python
# or
pytest tests/ -v
```

### Linting

```bash
# Go
task lint:go
# or
cd capture-tui-go
go fmt ./...
go vet ./...

# Python
task lint:python
# or
black capture_tui/
ruff check capture_tui/
mypy capture_tui/
```

---

## Troubleshooting

### Go Build Issues

**Issue:** "go: command not found"
- **Solution:** Install Go from https://golang.org/dl/

**Issue:** "cannot find module"
- **Solution:** Run `cd capture-tui-go && go mod download`

### Python Build Issues

**Issue:** "pyinstaller: command not found"
- **Solution:** Run `pip install pyinstaller`

**Issue:** Missing dependencies
- **Solution:** Run `pip install -e .` to install all dependencies

**Issue:** Docker not available for cross-compilation
- **Solution:** Build natively on target platform, or use CI/CD

### Windows-Specific Issues

**Issue:** Scripts won't run in PowerShell
- **Solution:** Use Command Prompt (cmd.exe) or Git Bash

**Issue:** Execution policy prevents running scripts
- **Solution:** Run PowerShell as Administrator and execute:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build

on: [push, pull_request]

jobs:
  build-go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - name: Build
        run: ./scripts/build-go.sh all
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: go-binaries
          path: dist/*

  build-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Build
        run: |
          pip install -e ".[dev]"
          ./scripts/build-python.sh current
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: python-binary
          path: dist/*
```

---

## Makefile Alternative

If you prefer Make over Task, create a `Makefile`:

```makefile
.PHONY: all build-go build-python clean test

VERSION ?= 1.0.0
DIST_DIR = dist

all: build-go build-python

build-go:
	./scripts/build-go.sh all

build-python:
	./scripts/build-python.sh current

clean:
	./scripts/build-go.sh clean
	./scripts/build-python.sh clean

test:
	./scripts/build-go.sh test
	pytest tests/

package:
	./scripts/build-go.sh package
```

---

## License

MIT License
