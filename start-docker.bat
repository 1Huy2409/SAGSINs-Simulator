@echo off
echo ======================================
echo 🚀 SAGSINs System Startup
echo ======================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Start Docker containers
echo 📦 Starting Docker containers...
cd docker
docker-compose up -d

if errorlevel 1 (
    echo ❌ Failed to start Docker containers
    exit /b 1
)

echo ✅ Docker containers started
echo.

echo ⏳ Waiting for services to be ready...
timeout /t 5 /nobreak >nul

REM Check if sagsins-server is running
docker ps | findstr sagsins-server >nul
if errorlevel 1 (
    echo ❌ SAGSINs Server failed to start
    echo Check logs with: docker logs sagsins-server
) else (
    echo ✅ SAGSINs Server is running
)

cd ..

echo.
echo ======================================
echo ✅ System is ready!
echo ======================================
echo.
echo Next steps:
echo.
echo 1. Start Backend:
echo    cd wep-app\backend ^&^& npm start
echo.
echo 2. Start Frontend (in another terminal):
echo    cd wep-app\frontend ^&^& npm run dev -- --host
echo.
echo 3. Open browser:
echo    http://localhost:5173
echo.
echo ======================================
echo.
echo 📊 Monitor Docker logs:
echo    docker logs sagsins-server -f
echo.
echo 🛑 Stop system:
echo    cd docker ^&^& docker-compose down
echo.

pause
