@echo off
REM Build Python CLI application for Windows
REM Usage: scripts\build-python.bat [target]
REM Targets: current, package

setlocal EnableDelayedExpansion

REM Configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "VERSION=1.0.0"
set "APP_NAME=capture-python"

echo [INFO] Building Capture TUI Python CLI v%VERSION%

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python.
    exit /b 1
)

REM Create dist directory
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

REM Install dependencies
echo [INFO] Installing dependencies...
cd /d "%PROJECT_ROOT%"

pip install pyinstaller -q
if errorlevel 1 (
    echo [ERROR] Failed to install pyinstaller
    exit /b 1
)

pip install -e . -q
if errorlevel 1 (
    echo [ERROR] Failed to install project
    exit /b 1
)

REM Parse arguments
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=current"

if "%TARGET%"=="current" (
    echo [INFO] Building for Windows...
    
    pyinstaller ^
        --clean ^
        --onefile ^
        --name "%APP_NAME%-windows-amd64" ^
        --distpath "%DIST_DIR%" ^
        --workpath "%PROJECT_ROOT%\build" ^
        "%PROJECT_ROOT%\scripts\capture-python.spec"
    
    if errorlevel 1 (
        echo [ERROR] Build failed
        exit /b 1
    )
    
    echo [INFO] Build complete: %DIST_DIR%\%APP_NAME%-windows-amd64.exe
)

if "%TARGET%"=="package" (
    echo [INFO] Packaging builds...
    
    cd /d "%DIST_DIR%"
    
    for %%f in (*.exe) do (
        echo [INFO] Creating zip archive for %%f...
        tar -acf "%%~nf-%VERSION%.zip" "%%f"
    )
    
    echo [INFO] Packaging complete
)

echo [INFO] Done!
exit /b 0
