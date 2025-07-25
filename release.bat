@echo off
setlocal enabledelayedexpansion

:: Extract version from pyproject.toml
for /f "tokens=2 delims==" %%A in ('findstr /i "version" pyproject.toml ^| findstr /v "#"') do (
    set raw_version=%%~A
    set raw_version=!raw_version:"=!
    set raw_version=!raw_version: =!  :: <-- ADD THIS LINE to remove spaces
)

if not defined raw_version (
    echo ❌ Could not extract version from pyproject.toml
    exit /b 1
)

set tag=v%raw_version%
echo Detected version: %tag%

set /p commit_msg=Enter commit message: 

git add .
git commit -m "%commit_msg%"
git tag %tag%
git push origin main
git push origin %tag%

echo.
echo ✅ Released %tag% to main!