@echo off
REM Build Go application for Windows
REM Usage: scripts\build-go.bat [target]
REM Targets: current, windows, all, clean

setlocal EnableDelayedExpansion

REM Configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "GO_DIR=%PROJECT_ROOT%\capture-tui-go"
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "VERSION=1.0.0"
set "APP_NAME=capture"
set "LDFLAGS=-s -w -X main.Version=%VERSION%"

echo [INFO] Capture TUI Go Builder v%VERSION%

REM Check Go
where go >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Go not found. Please install Go.
    exit /b 1
)

for /f "tokens=3" %%i in ('go version') do (
    echo [INFO] Go version: %%i
)

REM Create dist directory
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

REM Parse arguments
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=current"

if "%TARGET%"=="current" (
    echo [STEP] Building for current platform...
    
    cd /d "%GO_DIR%"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%.exe" ./cmd/capture
    
    if errorlevel 1 (
        echo [ERROR] Build failed
        exit /b 1
    )
    
    echo [INFO] Build complete: %DIST_DIR%\%APP_NAME%.exe
    dir "%DIST_DIR%\%APP_NAME%.exe"
)

if "%TARGET%"=="windows" (
    echo [STEP] Building for Windows...
    
    cd /d "%GO_DIR%"
    
    echo [INFO] Building for AMD64...
    set "GOOS=windows"
    set "GOARCH=amd64"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%-windows-amd64.exe" ./cmd/capture
    
    echo [INFO] Building for ARM64...
    set "GOOS=windows"
    set "GOARCH=arm64"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%-windows-arm64.exe" ./cmd/capture
    
    echo [INFO] Building for 386...
    set "GOOS=windows"
    set "GOARCH=386"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%-windows-386.exe" ./cmd/capture
    
    echo [INFO] Windows builds complete
)

if "%TARGET%"=="all" (
    echo [STEP] Building for all platforms...
    
    cd /d "%GO_DIR%"
    
    REM Windows
    echo [INFO] Building for Windows AMD64...
    set "GOOS=windows"
    set "GOARCH=amd64"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%-windows-amd64.exe" ./cmd/capture
    
    REM Linux
    echo [INFO] Building for Linux AMD64...
    set "GOOS=linux"
    set "GOARCH=amd64"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%-linux-amd64" ./cmd/capture
    
    echo [INFO] Building for Linux ARM64...
    set "GOOS=linux"
    set "GOARCH=arm64"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%-linux-arm64" ./cmd/capture
    
    REM macOS
    echo [INFO] Building for macOS AMD64...
    set "GOOS=darwin"
    set "GOARCH=amd64"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%-darwin-amd64" ./cmd/capture
    
    echo [INFO] Building for macOS ARM64...
    set "GOOS=darwin"
    set "GOARCH=arm64"
    go build -ldflags "%LDFLAGS%" -o "%DIST_DIR%\%APP_NAME%-darwin-arm64" ./cmd/capture
    
    echo [INFO] All builds complete
)

if "%TARGET%"=="package" (
    echo [STEP] Packaging builds...
    
    cd /d "%DIST_DIR%"
    
    for %%f in (*-windows-*.exe) do (
        echo [INFO] Creating zip archive for %%f...
        tar -acf "%%~nf-%VERSION%.zip" "%%f"
    )
    
    for %%f in (*-linux-* *-darwin-*) do (
        if exist "%%f" (
            echo [INFO] Skipping %%f (use WSL or Git Bash for tar.gz)
        )
    )
    
    echo [INFO] Packaging complete
)

if "%TARGET%"=="install" (
    echo [STEP] Installing locally...
    
    cd /d "%GO_DIR%"
    go install -ldflags "%LDFLAGS%" ./cmd/capture
    
    if errorlevel 1 (
        echo [ERROR] Install failed
        exit /b 1
    )
    
    for /f "tokens=*" %%i in ('go env GOPATH') do (
        echo [INFO] Installed to %%i\bin\%APP_NAME%.exe
    )
)

if "%TARGET%"=="test" (
    echo [STEP] Running tests...
    
    cd /d "%GO_DIR%"
    go test -v ./...
    
    if errorlevel 1 (
        echo [ERROR] Tests failed
        exit /b 1
    )
    
    echo [INFO] Tests complete
)

if "%TARGET%"=="clean" (
    echo [STEP] Cleaning build artifacts...
    
    rmdir /s /q "%DIST_DIR%" 2>nul
    cd /d "%GO_DIR%"
    go clean -cache
    
    echo [INFO] Clean complete
)

if "%TARGET%"=="help" (
    echo Build script for Capture TUI Go application
    echo.
    echo Usage: %0 [command]
    echo.
    echo Commands:
    echo   current    Build for current platform (default)
    echo   windows    Build for Windows (AMD64, ARM64, 386)
    echo   all        Build for all platforms
    echo   package    Package existing builds into archives
    echo   install    Install locally using 'go install'
    echo   test       Run tests
    echo   clean      Clean build artifacts
    echo   help       Show this help
)

echo.
echo [INFO] Done!
exit /b 0
