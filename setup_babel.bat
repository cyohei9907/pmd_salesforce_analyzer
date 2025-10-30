@echo off
echo Installing Node.js dependencies for JavaScript AST parser...
cd /d "%~dp0"

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed or not in PATH
    pause
    exit /b 1
)

echo Node.js version:
node --version

echo npm version:
npm --version

echo.
echo Installing dependencies...
npm install

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Installation completed successfully!
    echo ========================================
    echo.
    echo You can now use the Babel parser for LWC JavaScript files.
) else (
    echo.
    echo ERROR: Installation failed
    pause
    exit /b 1
)

pause
