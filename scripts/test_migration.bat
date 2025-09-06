@echo off
REM Test script để kiểm tra migration strategy trên Windows

echo [%time%] Starting Migration Strategy Test
echo =====================================

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [%time%] ERROR: docker-compose is not installed or not in PATH
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [%time%] ERROR: .env file not found. Please copy .env.example to .env and configure it.
    exit /b 1
)

echo [%time%] 1. Testing Migration Service...
docker-compose up migration_service
if errorlevel 1 (
    echo [%time%] ERROR: Migration service failed
    exit /b 1
)
echo [%time%] Migration service completed successfully

echo [%time%] 2. Starting all services...
docker-compose up -d

echo [%time%] 3. Waiting for services to be ready...
timeout /t 30 /nobreak >nul

echo [%time%] 4. Testing service scaling...
docker-compose up -d --scale betting_service=3

echo [%time%] Waiting for scaling to complete...
timeout /t 15 /nobreak >nul

echo [%time%] 5. Checking service status...
docker-compose ps

echo [%time%] 6. Checking Redis locks...
docker-compose exec -T redis redis-cli KEYS "*migration*"

echo [%time%] 7. Test completed!
echo =====================================
echo [%time%] Migration Strategy Test Completed Successfully!
echo =====================================

set /p cleanup="Do you want to cleanup test environment? (y/N): "
if /i "%cleanup%"=="y" (
    echo [%time%] Cleaning up test environment...
    docker-compose down -v
    docker system prune -f
    echo [%time%] Cleanup completed
) else (
    echo [%time%] Test environment left running. Use 'make clean' to cleanup later.
)

pause
