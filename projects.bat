@echo off
setlocal enabledelayedexpansion

echo.
echo  === Projects ===
echo.

set i=0

:: Collect from ~/projects/ (WSL home)
for /f "tokens=*" %%d in ('wsl ls ~/projects/ 2^>nul') do (
    set /a i+=1
    set "proj[!i!]=%%d"
    set "path[!i!]=~/projects/%%d"
    set "seen_%%d=1"
    echo   !i!. %%d
)

:: Collect from Windows projects folder, skip duplicates
for /f "tokens=*" %%d in ('wsl ls /mnt/c/Users/nikla/projects/ 2^>nul') do (
    if not defined seen_%%d (
        set /a i+=1
        set "proj[!i!]=%%d"
        set "path[!i!]=/mnt/c/Users/nikla/projects/%%d"
        echo   !i!. %%d
    )
)

if %i%==0 (
    echo   No projects found.
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
