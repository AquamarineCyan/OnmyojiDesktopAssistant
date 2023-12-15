@echo off

if exist main.spec (
    echo find main.spec
    poetry run pyinstaller main.spec --clean --noconfirm --distpath .
) else (
    echo not find main.spec
    poetry run pyinstaller main.py --name "output" --contents-directory "lib" -w -i "buzhihuo.ico" --uac-admin --clean  --noconfirm --distpath .
)

if exist output (
    if exist output\output.exe (
        ren output\output.exe Onmyoji_Python.exe
    )
    rmdir /s /q "lib"
    xcopy output . /s /e /v /q /y
    rmdir /s /q "build" "output"
) else if exist main (
    ren main\main.exe Onmyoji_Python.exe
    rmdir /s /q "lib"
    xcopy main . /s /e /v /q /y
    rmdir /s /q "build" "main"
) else (
    echo build failed
)

if exist output.spec (
    ren output.spec main.spec
)

pause