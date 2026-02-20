@echo off
cd /d "%~dp0"
echo Starting Health Recommendation System...
echo Current directory: %CD%
echo.

REM Check if manage.py exists
if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Please run this script from the project directory.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Create static directory if it doesn't exist
if not exist "static" mkdir static

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Start server in a new window first (so it's ready before we open browser)
echo.
echo ========================================
echo Starting Django development server...
echo ========================================
echo.
echo Server will be available at:`
echo Click here: http://127.0.0.1:8080/
start "" http://127.0.0.1:8080/

echo.
echo Starting server in new window...
start "Django Server" cmd /k "call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8080"

REM Wait for server to be ready before opening browser
echo Waiting for server to start (5 seconds)...
ping 127.0.0.1 -n 6 > nul

echo Opening browser in external window...
REM Try to find and launch Microsoft Edge directly
REM Using localhost instead of 127.0.0.1 to avoid Cursor URL handler interception
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" "http://localhost:8080/"
) else if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" "http://localhost:8080/"
) else (
    REM Fallback: Use Python script (uses default browser)
    start /MIN "" python open_browser.py
)

echo.
echo ========================================
echo Browser opened! Server is running in the other window.
echo Close the "Django Server" window to stop the server.
echo ========================================
pause
