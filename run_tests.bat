@echo off
echo Running Log Archive Tool Tests...
echo ================================

python -m pytest test_log_archive.py -v
if errorlevel 1 (
    echo.
    echo Tests failed!
    pause
    exit /b 1
)

echo.
echo All tests passed!
pause