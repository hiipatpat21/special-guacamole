@echo off
setlocal
pushd "%~dp0"
py -3 --version >nul 2>&1
if not errorlevel 1 (
    py -3 setup_env.py
) else (
    python setup_env.py
)
set "setup_exit=%ERRORLEVEL%"
echo.
if not "%setup_exit%"=="0" echo Setup failed. Install Python 3.10 or newer and check your internet connection.
popd
pause
exit /b %setup_exit%
