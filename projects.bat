@echo off
setlocal enabledelayedexpansion

:: projects.bat — Windows-native project launcher (no WSL).
:: Lists project folders under %USERPROFILE%\projects and %USERPROFILE%\tools,
:: then: number = open in VS Code, N = new project, U = update a project.
:: Every error path calls pause so the window never blinks-and-dies.

echo.
echo  === Projects ===
echo.

set i=0

:: Collect from %USERPROFILE%\projects
for /f "delims=" %%d in ('dir /b /ad "%USERPROFILE%\projects" 2^>nul') do (
    if not defined seen_%%d (
        set /a i+=1
        set "proj[!i!]=%%d"
        set "path[!i!]=%USERPROFILE%\projects\%%d"
        set "seen_%%d=1"
        echo   !i!. %%d
    )
)

:: Collect from %USERPROFILE%\tools, skip duplicates
for /f "delims=" %%d in ('dir /b /ad "%USERPROFILE%\tools" 2^>nul') do (
    if not defined seen_%%d (
        set /a i+=1
        set "proj[!i!]=%%d"
        set "path[!i!]=%USERPROFILE%\tools\%%d"
        set "seen_%%d=1"
        echo   !i!. %%d
    )
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
    python "%~dp0new_project.py"
    if errorlevel 1 pause
    exit /b
)

if /i "%choice%"=="U" goto :update

:: Numeric choice -> open in VS Code
if not defined path[%choice%] goto :invalid
set "selpath=!path[%choice%]!"
echo.
echo Opening !proj[%choice%]! in VS Code...
code "!selpath!"
if errorlevel 1 (
    echo Failed to open VS Code ^(is 'code' on PATH?^).
    pause
)
exit /b

:update
echo.
set /p upick="Which project number to update? "
if not defined path[%upick%] goto :invalid
set "uppath=!path[%upick%]!"
echo.
echo Updating !proj[%upick%]!...
python "%~dp0new_project.py" --update "!uppath!"
if errorlevel 1 pause
exit /b

:invalid
echo Invalid choice.
pause
exit /b
