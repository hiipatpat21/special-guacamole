@echo off
setlocal
pushd "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run setup.bat first to create the Python environment on this computer.
    popd
    pause
    exit /b 1
)
".venv\Scripts\python.exe" simulation.py
set "simulation_exit=%ERRORLEVEL%"
echo.
popd
pause
exit /b %simulation_exit%
