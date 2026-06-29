@echo off
setlocal
cd /d "%~dp0"

:: Add local portable Node.js to PATH if it exists
if exist "node_portable" (
    set "PATH=%CD%\node_portable;%PATH%"
)

echo ===================================================
echo   Starting GRC Compliance Assistant
echo ===================================================

:: Check and activate Python Virtual Environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment [.venv]...
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment [venv]...
    call "venv\Scripts\activate.bat"
) else (
    echo WARNING: Virtual environment not found. Running using system Python.
)

:: Check if Node.js/npm is available
where npm >nul 2>nul
if errorlevel 1 (
    echo Node.js/npm was not detected on this machine.
    echo The enterprise React UI requires Node.js.
    echo.
    goto streamlit_flow
)

:react_flow
echo Node.js/npm detected. Building React Enterprise UI...
if not exist "frontend\node_modules" (
    echo Installing React package dependencies...
    pushd frontend
    call npm install
    popd
)
echo Compiling React frontend assets...
pushd frontend
call npm run build
popd

if not exist "frontend\dist" (
    echo WARNING: React compilation folder dist not found.
    echo Falling back to Streamlit UI.
    echo.
    goto streamlit_flow
)

echo.
echo ===================================================
echo   FastAPI backend is serving the React Enterprise UI
echo   URL: http://127.0.0.1:8000
echo ===================================================
echo.
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
goto :eof

:streamlit_flow
echo ===================================================
echo   Launching Python Streamlit Workspace fallback
echo ===================================================
echo.
:: Start FastAPI backend in another window (port 8000)
start "GRC Backend API" cmd /k "uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
:: Start Streamlit UI in the foreground
streamlit run app.py
goto :eof
