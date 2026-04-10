#!/usr/bin/env bash
# Build Go application for all platforms
# Usage: ./scripts/build-go.sh [platform]
# Platforms: current, macos, linux, windows, all

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GO_DIR="$PROJECT_ROOT/capture-tui-go"
DIST_DIR="$PROJECT_ROOT/dist"
VERSION="1.0.0"
APP_NAME="capture"

# Build flags for optimization
LDFLAGS="-s -w -X main.Version=$VERSION"

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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Setup function
setup() {
    print_step "Setting up build environment..."
    
    # Create dist directory
    mkdir -p "$DIST_DIR"
    
    # Check Go
    if ! command_exists go; then
        print_error "Go not found. Please install Go."
        exit 1
    fi
    
    # Check Go version
    GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
    print_info "Go version: $GO_VERSION"
    
    # Download dependencies
    print_info "Downloading Go dependencies..."
    cd "$GO_DIR"
    go mod download
    go mod tidy
}

# Build for current platform
build_current() {
    print_step "Building for current platform..."
    
    cd "$GO_DIR"
    
    local output_name="$DIST_DIR/$APP_NAME"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        output_name="${output_name}.exe"
    fi
    
    go build -ldflags "$LDFLAGS" -o "$output_name" ./cmd/capture
    
    print_info "Build complete: $output_name"
    
    # Show binary info
    if command_exists ls; then
        ls -lh "$output_name"
    fi
}

# Build for macOS
build_macos() {
    print_step "Building for macOS..."
    
    cd "$GO_DIR"
    
    # Intel (AMD64)
    print_info "Building for Intel (x86_64)..."
    GOOS=darwin GOARCH=amd64 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-darwin-amd64" ./cmd/capture
    
    # Apple Silicon (ARM64)
    print_info "Building for Apple Silicon (arm64)..."
    GOOS=darwin GOARCH=arm64 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-darwin-arm64" ./cmd/capture
    
    # Universal binary (if on macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_info "Creating universal binary..."
        if command_exists lipo; then
            lipo -create \
                "$DIST_DIR/${APP_NAME}-darwin-amd64" \
                "$DIST_DIR/${APP_NAME}-darwin-arm64" \
                -output "$DIST_DIR/${APP_NAME}-darwin-universal"
            print_info "Universal binary created"
        fi
    fi
    
    print_info "macOS builds complete"
}

# Build for Linux
build_linux() {
    print_step "Building for Linux..."
    
    cd "$GO_DIR"
    
    # AMD64
    print_info "Building for AMD64..."
    GOOS=linux GOARCH=amd64 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-linux-amd64" ./cmd/capture
    
    # ARM64
    print_info "Building for ARM64..."
    GOOS=linux GOARCH=arm64 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-linux-arm64" ./cmd/capture
    
    # 386
    print_info "Building for 386..."
    GOOS=linux GOARCH=386 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-linux-386" ./cmd/capture
    
    print_info "Linux builds complete"
}

# Build for Windows
build_windows() {
    print_step "Building for Windows..."
    
    cd "$GO_DIR"
    
    # AMD64
    print_info "Building for AMD64..."
    GOOS=windows GOARCH=amd64 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-windows-amd64.exe" ./cmd/capture
    
    # ARM64
    print_info "Building for ARM64..."
    GOOS=windows GOARCH=arm64 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-windows-arm64.exe" ./cmd/capture
    
    # 386
    print_info "Building for 386..."
    GOOS=windows GOARCH=386 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-windows-386.exe" ./cmd/capture
    
    print_info "Windows builds complete"
}

# Build for FreeBSD
build_freebsd() {
    print_step "Building for FreeBSD..."
    
    cd "$GO_DIR"
    
    GOOS=freebsd GOARCH=amd64 go build -ldflags "$LDFLAGS" \
        -o "$DIST_DIR/${APP_NAME}-freebsd-amd64" ./cmd/capture
    
    print_info "FreeBSD build complete"
}

# Build all platforms
build_all() {
    print_step "Building for all platforms..."
    
    setup
    
    build_macos
    build_linux
    build_windows
    build_freebsd
    
    print_info "All builds complete!"
    
    # List all builds
    echo ""
    print_step "Built binaries:"
    ls -lh "$DIST_DIR/$APP_NAME"* 2>/dev/null || true
}

# Package builds
package() {
    print_step "Packaging builds..."
    
    cd "$DIST_DIR"
    
    # Create archives for each platform
    for file in *; do
        if [[ -f "$file" ]] && [[ -x "$file" ]] && [[ ! "$file" == *.tar.gz ]] && [[ ! "$file" == *.zip ]]; then
            if [[ "$file" == *.exe ]]; then
                print_info "Creating zip archive for $file..."
                zip "${file%.exe}-${VERSION}.zip" "$file"
            else
                print_info "Creating tar.gz archive for $file..."
                tar -czf "${file}-${VERSION}.tar.gz" "$file"
            fi
        fi
    done
    
    # Create checksums
    print_info "Creating checksums..."
    if command_exists sha256sum; then
        sha256sum *.{tar.gz,zip} > "${APP_NAME}-${VERSION}-checksums.txt" 2>/dev/null || true
    elif command_exists shasum; then
        shasum -a 256 *.{tar.gz,zip} > "${APP_NAME}-${VERSION}-checksums.txt" 2>/dev/null || true
    fi
    
    print_info "Packaging complete!"
}

# Install locally
install_local() {
    print_step "Installing locally..."
    
    if ! command_exists go; then
        print_error "Go not found"
        exit 1
    fi
    
    cd "$GO_DIR"
    go install -ldflags "$LDFLAGS" ./cmd/capture
    
    print_info "Installed to $(go env GOPATH)/bin/$APP_NAME"
}

# Run tests
test() {
    print_step "Running tests..."
    
    cd "$GO_DIR"
    
    # Run go tests
    go test -v ./...
    
    # Run Ginkgo tests if available
    if command_exists ginkgo; then
        ginkgo -v ./test/
    fi
    
    print_info "Tests complete"
}

# Clean build artifacts
clean() {
    print_step "Cleaning build artifacts..."
    
    rm -rf "$DIST_DIR"
    cd "$GO_DIR" && go clean -cache
    
    print_info "Clean complete"
}

# Show help
show_help() {
    echo "Build script for Capture TUI Go application"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  current    Build for current platform (default)"
    echo "  macos      Build for macOS (Intel + Apple Silicon)"
    echo "  linux      Build for Linux (AMD64, ARM64, 386)"
    echo "  windows    Build for Windows (AMD64, ARM64, 386)"
    echo "  freebsd    Build for FreeBSD"
    echo "  all        Build for all platforms"
    echo "  package    Package existing builds into archives"
    echo "  install    Install locally using 'go install'"
    echo "  test       Run tests"
    echo "  clean      Clean build artifacts"
    echo "  help       Show this help"
    echo ""
    echo "Environment variables:"
    echo "  VERSION    Set version (default: $VERSION)"
    echo "  LDFLAGS    Additional linker flags"
}

# Main
main() {
    local command="${1:-current}"
    
    # Allow VERSION override
    if [[ -n "$VERSION" ]] && [[ "$VERSION" != "1.0.0" ]]; then
        VERSION="$VERSION"
        LDFLAGS="-s -w -X main.Version=$VERSION"
    fi
    
    print_info "Capture TUI Go Builder v$VERSION"
    print_info "Working directory: $GO_DIR"
    
    case "$command" in
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
        windows|win)
            setup
            build_windows
            ;;
        freebsd)
            setup
            build_freebsd
            ;;
        all)
            build_all
            ;;
        package)
            package
            ;;
        install)
            install_local
            ;;
        test)
            test
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    print_info "Done!"
}

main "$@"
