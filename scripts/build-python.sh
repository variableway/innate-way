#!/usr/bin/env bash
# Build Python CLI application for macOS and Linux
# Usage: ./scripts/build-python.sh [platform]
# Platforms: current, macos, linux, windows (requires Docker), all

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"
VERSION="1.0.0"
APP_NAME="capture-python"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Setup function
setup() {
    print_info "Setting up build environment..."
    
    # Create dist directory
    mkdir -p "$DIST_DIR"
    
    # Install pyinstaller if not present
    if ! command_exists pyinstaller; then
        print_info "Installing pyinstaller..."
        pip install pyinstaller
    fi
    
    # Install project dependencies
    print_info "Installing project dependencies..."
    cd "$PROJECT_ROOT"
    if command_exists uv; then
        uv pip install -e ".[dev]"
    else
        pip install -e ".[dev]"
    fi
}

# Build for current platform
build_current() {
    print_info "Building for current platform..."
    
    cd "$PROJECT_ROOT"
    pyinstaller \
        --clean \
        --onefile \
        --name "${APP_NAME}" \
        --distpath "$DIST_DIR" \
        --workpath "$PROJECT_ROOT/build" \
        scripts/capture-python.spec
    
    print_info "Build complete: $DIST_DIR/${APP_NAME}"
}

# Build for macOS
build_macos() {
    print_info "Building for macOS..."
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_warn "Not on macOS. Cross-compilation not supported for Python."
        print_warn "Use Docker or build on a macOS machine."
        return 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # Build Intel version
    print_info "Building for Intel (x86_64)..."
    pyinstaller \
        --clean \
        --onefile \
        --name "${APP_NAME}-darwin-x86_64" \
        --distpath "$DIST_DIR" \
        --workpath "$PROJECT_ROOT/build" \
        scripts/capture-python.spec
    
    # Build Apple Silicon version
    print_info "Building for Apple Silicon (arm64)..."
    arch -arm64 pyinstaller \
        --clean \
        --onefile \
        --name "${APP_NAME}-darwin-arm64" \
        --distpath "$DIST_DIR" \
        --workpath "$PROJECT_ROOT/build-arm64" \
        scripts/capture-python.spec
    
    print_info "macOS builds complete"
}

# Build for Linux
build_linux() {
    print_info "Building for Linux..."
    
    if [[ "$OSTYPE" != "linux"* ]]; then
        print_warn "Not on Linux. Using Docker for build..."
        build_linux_docker
        return
    fi
    
    cd "$PROJECT_ROOT"
    
    # Build AMD64
    print_info "Building for AMD64..."
    pyinstaller \
        --clean \
        --onefile \
        --name "${APP_NAME}-linux-amd64" \
        --distpath "$DIST_DIR" \
        --workpath "$PROJECT_ROOT/build" \
        scripts/capture-python.spec
    
    print_info "Linux build complete"
}

# Build Linux using Docker
build_linux_docker() {
    print_info "Building Linux binaries using Docker..."
    
    if ! command_exists docker; then
        print_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    docker run --rm \
        -v "$PROJECT_ROOT:/src" \
        -w /src \
        python:3.11-slim \
        bash -c "
            pip install pyinstaller &&
            pip install -e . &&
            pyinstaller --clean --onefile --name ${APP_NAME}-linux-amd64 \
                --distpath dist --workpath build scripts/capture-python.spec
        "
    
    print_info "Linux Docker build complete"
}

# Build for Windows using Docker
build_windows() {
    print_info "Building for Windows using Docker..."
    
    if ! command_exists docker; then
        print_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # Use wine-based pyinstaller image
    docker run --rm \
        -v "$PROJECT_ROOT:/src" \
        -w /src \
        cdrx/pyinstaller-windows:python3 \
        pyinstaller --clean --onefile --name ${APP_NAME}-windows-amd64.exe \
            --distpath dist --workpath build scripts/capture-python.spec
    
    print_info "Windows build complete"
}

# Build all platforms
build_all() {
    print_info "Building for all platforms..."
    
    setup
    
    case "$OSTYPE" in
        linux*)
            build_linux
            build_windows
            ;;
        darwin*)
            build_macos
            build_linux_docker
            build_windows
            ;;
        *)
            print_error "Unsupported platform: $OSTYPE"
            exit 1
            ;;
    esac
    
    print_info "All builds complete!"
}

# Package builds
package() {
    print_info "Packaging builds..."
    
    cd "$DIST_DIR"
    
    for file in *; do
        if [[ "$file" == *.exe ]]; then
            print_info "Creating zip archive for $file..."
            zip "${file%.exe}-${VERSION}.zip" "$file"
        elif [[ -x "$file" ]]; then
            print_info "Creating tar.gz archive for $file..."
            tar -czf "${file}-${VERSION}.tar.gz" "$file"
        fi
    done
    
    print_info "Packaging complete!"
}

# Main
main() {
    local platform="${1:-current}"
    
    print_info "Building Capture TUI Python CLI v$VERSION"
    print_info "Platform: $platform"
    
    case "$platform" in
        current)
            setup
            build_current
            ;;
        macos|darwin)
            setup
            build_macos
            ;;
        linux)
            setup
            build_linux
            ;;
        windows)
            build_windows
            ;;
        all)
            build_all
            ;;
        package)
            package
            ;;
        *)
            echo "Usage: $0 [current|macos|linux|windows|all|package]"
            echo ""
            echo "Platforms:"
            echo "  current  - Build for current platform (default)"
            echo "  macos    - Build for macOS (Intel + Apple Silicon)"
            echo "  linux    - Build for Linux (AMD64)"
            echo "  windows  - Build for Windows using Docker"
            echo "  all      - Build for all platforms (requires Docker)"
            echo "  package  - Package existing builds into archives"
            exit 1
            ;;
    esac
    
    print_info "Done!"
}

main "$@"
