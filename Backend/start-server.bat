@echo off
echo ==========================================
echo     PUBLIC SERVICES BACKEND SERVER
echo ==========================================
echo.
echo Starting backend server on port 8888...
echo Server will be available at: http://192.168.1.231:8888
echo.
echo Waiting 3 seconds before starting...
timeout /t 3 /nobreak > nul
echo.

REM Check if node_modules exists, if not install dependencies
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    echo.
)

REM Set environment to development
set NODE_ENV=development
set PORT=8888

echo Environment set to: %NODE_ENV%
echo Port set to: %PORT%
echo.

REM Start the server
npm run dev

pause
