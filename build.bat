@echo off

if not exist main.spec (
    echo Error: main.spec not found
    pause
    exit /b 1
)

if not exist .venv\Scripts\pyinstaller.exe (
    echo Error: pyinstaller not found in .venv
    pause
    exit /b 1
)

echo Building with main.spec...
.venv\Scripts\pyinstaller.exe main.spec --clean --noconfirm --distpath .


if not exist output (
    echo Build failed: Output directory not found
    pause
    exit /b 1
)

rmdir /s /q "lib"
xcopy output . /s /e /v /q /y
rmdir /s /q "build" "output"

echo Build completed successfully!

pause