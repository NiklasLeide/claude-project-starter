@echo off
setlocal enabledelayedexpansion

echo.
echo  === Projects ===
echo.

set i=0

:: Collect from ~/projects/
for /f "tokens=*" %%d in ('wsl ls ~/projects/ 2^>nul') do (
    set /a i+=1
    set "proj[!i!]=%%d"
    set "path[!i!]=~/projects/%%d"
    set "seen_%%d=1"
    echo   !i!. %%d
)

:: Collect from /mnt/c/Users/nikla/projects/, skip duplicates
for /f "tokens=*" %%d in ('wsl ls /mnt/c/Users/nikla/projects/ 2^>nul') do (
    if not defined seen_%%d (
        set /a i+=1
        set "proj[!i!]=%%d"
        set "path[!i!]=/mnt/c/Users/nikla/projects/%%d"
        set "seen_%%d=1"
        echo   !i!. %%d
    )
)

:: Collect from ~/tools/, skip duplicates
for /f "tokens=*" %%d in ('wsl ls ~/tools/ 2^>nul') do (
    if not defined seen_%%d (
        set /a i+=1
        set "proj[!i!]=%%d"
        set "path[!i!]=~/tools/%%d"
        set "seen_%%d=1"
        echo   !i!. %%d
    )
)

:: Add ~/lifecoach-app-repo as a named entry, skip if duplicate
if not defined seen_lifecoach-app-repo (
    set /a i+=1
    set "proj[!i!]=lifecoach-app-repo"
    set "path[!i!]=~/lifecoach-app-repo"
    set "seen_lifecoach-app-repo=1"
    echo   !i!. lifecoach-app-repo
)

if %i%==0 (
    echo   No projects found.
)

echo.
echo   N. Start new project
echo   U. Update project (refresh slash commands + commit.sh)
echo.

set /p choice="Pick a number, N, or U: "

if /i "%choice%"=="N" (
    wsl -e bash -lic "newproject"
    exit /b
)

if /i "%choice%"=="U" goto :update

:: Validate choice
if %choice% LSS 1 goto :invalid
if %choice% GTR %i% goto :invalid

set "selected=!proj[%choice%]!"
set "selpath=!path[%choice%]!"
echo.
echo Opening %selected% in VS Code...
wsl -e bash -c "code --new-window %selpath%"
exit /b

:update
echo.
set /p upick="Which project number to update? "
if %upick% LSS 1 goto :invalid
if %upick% GTR %i% goto :invalid
set "uppath=!path[%upick%]!"
echo.
echo Updating !proj[%upick%]!...
wsl -e bash -lic "python3 ~/tools/claude-project-starter/new_project.py --update !uppath!"
exit /b

:invalid
echo Invalid choice.
exit /b
