@echo off
setlocal enabledelayedexpansion

:: Get version from pyproject.toml
for /f "tokens=2 delims==" %%A in ('findstr /i "version" pyproject.toml ^| findstr /v "#"' ) do (
    set version=%%~A
    set version=!version:"=!
)

if not defined version (
    echo Could not extract version from pyproject.toml
    exit /b 1
)

echo Detected version: v%version%
set /p commit_msg=Enter commit message: 

git add .
git commit -m "%commit_msg%"
git tag v%version%
git push origin main
git push origin v%version%

echo.
echo ✅ Released v%version% to main!
