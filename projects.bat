@echo off
setlocal enabledelayedexpansion

echo.
echo  === Projects ===
echo.

:: Collect unique folder names from both project directories via WSL
:: Output format: name|path (path is the directory the folder lives in)
set i=0
for /f "tokens=1,2 delims=|" %%a in ('wsl bash -c "( for d in ~/projects/*/; do [ -d \"$d\" ] && basename \"$d\"; done; for d in /mnt/c/Users/nikla/projects/*/; do [ -d \"$d\" ] && basename \"$d\"; done ) | sort -u | while read name; do if [ -d ~/projects/\"$name\" ]; then echo \"$name|~/projects/$name\"; else echo \"$name|/mnt/c/Users/nikla/projects/$name\"; fi; done"') do (
    set /a i+=1
    set "proj[!i!]=%%a"
    set "path[!i!]=%%b"
    echo   !i!. %%a
)

echo.
echo   N. Start new project
echo.

set /p choice="Pick a number (or N): "

if /i "%choice%"=="N" (
    wsl -e bash -lic "newproject"
    exit /b
)

:: Validate choice
if %choice% LSS 1 goto :invalid
if %choice% GTR %i% goto :invalid

set "selected=!proj[%choice%]!"
set "selpath=!path[%choice%]!"
echo.
echo Opening %selected% in VS Code...
wsl -e bash -c "code --new-window %selpath%"
exit /b

:invalid
echo Invalid choice.
exit /b
