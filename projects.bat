@echo off
setlocal enabledelayedexpansion

echo.
echo  === Projects ===
echo.

:: Collect folder names from ~/projects/ via WSL
set i=0
for /f "tokens=*" %%d in ('wsl ls ~/projects/') do (
    set /a i+=1
    set "proj[!i!]=%%d"
    echo   !i!. %%d
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
echo.
echo Opening %selected% in VS Code...
wsl -e bash -c "code --new-window ~/projects/%selected%"
exit /b

:invalid
echo Invalid choice.
exit /b
