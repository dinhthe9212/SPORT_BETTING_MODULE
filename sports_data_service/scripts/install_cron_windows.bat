@echo off
REM Script cài đặt cron jobs cho Sports Data Service trên Windows
REM Chạy với quyền Administrator

echo 🚀 Cài đặt cron jobs cho Sports Data Service trên Windows...

REM Lấy đường dẫn hiện tại
set CURRENT_DIR=%CD%
set SPORTS_SERVICE_DIR=%CURRENT_DIR%

REM Kiểm tra quyền Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Vui lòng chạy script này với quyền Administrator
    pause
    exit /b 1
)

REM Kiểm tra thư mục sports_data_service
if not exist "%SPORTS_SERVICE_DIR%" (
    echo ❌ Không tìm thấy thư mục sports_data_service
    pause
    exit /b 1
)

echo 📁 Thư mục Sports Data Service: %SPORTS_SERVICE_DIR%

REM Tạo thư mục logs
if not exist "%SPORTS_SERVICE_DIR%\logs" (
    mkdir "%SPORTS_SERVICE_DIR%\logs"
    echo ✅ Đã tạo thư mục logs
)

REM Tạo script batch cho sync_sports_data
set SYNC_SCRIPT=%SPORTS_SERVICE_DIR%\scripts\sync_sports_data.bat
echo @echo off > "%SYNC_SCRIPT%"
echo cd /d "%SPORTS_SERVICE_DIR%" >> "%SYNC_SCRIPT%"
echo echo [%date% %time%] Bắt đầu đồng bộ dữ liệu thể thao... >> "%SPORTS_SERVICE_DIR%\logs\cron_sync_sports_data.log" >> "%SYNC_SCRIPT%"
echo python manage.py sync_sports_data >> "%SPORTS_SERVICE_DIR%\logs\cron_sync_sports_data.log" 2^>^&1 >> "%SYNC_SCRIPT%"
echo echo [%date% %time%] Hoàn thành đồng bộ dữ liệu thể thao >> "%SPORTS_SERVICE_DIR%\logs\cron_sync_sports_data.log" >> "%SYNC_SCRIPT%"

REM Tạo script batch cho sync_odds_data
set ODDS_SCRIPT=%SPORTS_SERVICE_DIR%\scripts\sync_odds_data.bat
echo @echo off > "%ODDS_SCRIPT%"
echo cd /d "%SPORTS_SERVICE_DIR%" >> "%ODDS_SCRIPT%"
echo echo [%date% %time%] Bắt đầu đồng bộ tỷ lệ cược... >> "%SPORTS_SERVICE_DIR%\logs\cron_sync_odds_data.log" >> "%ODDS_SCRIPT%"
echo python manage.py sync_odds_data >> "%SPORTS_SERVICE_DIR%\logs\cron_sync_odds_data.log" 2^>^&1 >> "%ODDS_SCRIPT%"
echo echo [%date% %time%] Hoàn thành đồng bộ tỷ lệ cược >> "%SPORTS_SERVICE_DIR%\logs\cron_sync_odds_data.log" >> "%ODDS_SCRIPT%"

REM Tạo script batch cho health_check
set HEALTH_SCRIPT=%SPORTS_SERVICE_DIR%\scripts\health_check.bat
echo @echo off > "%HEALTH_SCRIPT%"
echo cd /d "%SPORTS_SERVICE_DIR%" >> "%HEALTH_SCRIPT%"
echo echo [%date% %time%] Bắt đầu health check... >> "%SPORTS_SERVICE_DIR%\logs\cron_health_check.log" >> "%HEALTH_SCRIPT%"
echo python manage.py check >> "%SPORTS_SERVICE_DIR%\logs\cron_health_check.log" 2^>^&1 >> "%HEALTH_SCRIPT%"
echo echo [%date% %time%] Hoàn thành health check >> "%SPORTS_SERVICE_DIR%\logs\cron_health_check.log" >> "%HEALTH_SCRIPT%"

echo ✅ Đã tạo các script batch

REM Tạo file PowerShell script để cài đặt Task Scheduler
set PS_SCRIPT=%SPORTS_SERVICE_DIR%\scripts\install_tasks.ps1

echo # PowerShell script để cài đặt Task Scheduler cho Sports Data Service > "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo Write-Host "🚀 Cài đặt Task Scheduler cho Sports Data Service..." >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo # Xóa tasks cũ nếu có >> "%PS_SCRIPT%"
echo Get-ScheduledTask -TaskName "SportsDataService*" -ErrorAction SilentlyContinue ^| Remove-ScheduledTask -Confirm:$false >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo # Tạo task đồng bộ dữ liệu thể thao mỗi 5 phút >> "%PS_SCRIPT%"
echo $action = New-ScheduledTaskAction -Execute "%SYNC_SCRIPT%" >> "%PS_SCRIPT%"
echo $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365) >> "%PS_SCRIPT%"
echo $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable >> "%PS_SCRIPT%"
echo Register-ScheduledTask -TaskName "SportsDataService_SyncSportsData" -Action $action -Trigger $trigger -Settings $settings -Description "Đồng bộ dữ liệu thể thao mỗi 5 phút" >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo # Tạo task đồng bộ tỷ lệ cược mỗi 10 phút >> "%PS_SCRIPT%"
echo $action = New-ScheduledTaskAction -Execute "%ODDS_SCRIPT%" >> "%PS_SCRIPT%"
echo $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 365) >> "%PS_SCRIPT%"
echo Register-ScheduledTask -TaskName "SportsDataService_SyncOddsData" -Action $action -Trigger $trigger -Settings $settings -Description "Đồng bộ tỷ lệ cược mỗi 10 phút" >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo # Tạo task health check mỗi giờ >> "%PS_SCRIPT%"
echo $action = New-ScheduledTaskAction -Execute "%HEALTH_SCRIPT%" >> "%PS_SCRIPT%"
echo $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365) >> "%PS_SCRIPT%"
echo Register-ScheduledTask -TaskName "SportsDataService_HealthCheck" -Action $action -Trigger $trigger -Settings $settings -Description "Health check mỗi giờ" >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo # Tạo task đồng bộ đầy đủ mỗi ngày lúc 6:00 AM >> "%PS_SCRIPT%"
echo $action = New-ScheduledTaskAction -Execute "%SYNC_SCRIPT%" >> "%PS_SCRIPT%"
echo $trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM >> "%PS_SCRIPT%"
echo Register-ScheduledTask -TaskName "SportsDataService_DailySync" -Action $action -Trigger $trigger -Settings $settings -Description "Đồng bộ đầy đủ mỗi ngày 6:00 AM" >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo # Tạo task đồng bộ odds đầy đủ mỗi ngày lúc 6:30 AM >> "%PS_SCRIPT%"
echo $action = New-ScheduledTaskAction -Execute "%ODDS_SCRIPT%" >> "%PS_SCRIPT%"
echo $trigger = New-ScheduledTaskTrigger -Daily -At 6:30AM >> "%PS_SCRIPT%"
echo Register-ScheduledTask -TaskName "SportsDataService_DailyOddsSync" -Action $action -Trigger $trigger -Settings $settings -Description "Đồng bộ odds đầy đủ mỗi ngày 6:30 AM" >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo Write-Host "✅ Đã tạo tất cả Task Scheduler tasks" >> "%PS_SCRIPT%"
echo Write-Host "📋 Danh sách tasks đã tạo:" >> "%PS_SCRIPT%"
echo Get-ScheduledTask -TaskName "SportsDataService*" ^| Select-Object TaskName, State, NextRunTime >> "%PS_SCRIPT%"

echo ✅ Đã tạo PowerShell script: %PS_SCRIPT%

echo.
echo 🎯 Để hoàn thành cài đặt, hãy thực hiện các bước sau:
echo.
echo 1. Mở PowerShell với quyền Administrator
echo 2. Chạy lệnh: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
echo 3. Chạy lệnh: & "%PS_SCRIPT%"
echo.
echo 📋 Cron Jobs sẽ được tạo:
echo    • Đồng bộ dữ liệu thể thao: Mỗi 5 phút
echo    • Đồng bộ tỷ lệ cược: Mỗi 10 phút
echo    • Health check: Mỗi giờ
echo    • Đồng bộ đầy đủ: Mỗi ngày 6:00 AM
echo    • Đồng bộ odds đầy đủ: Mỗi ngày 6:30 AM
echo.
echo 📁 Log files:
echo    • %SPORTS_SERVICE_DIR%\logs\cron_sync_sports_data.log
echo    • %SPORTS_SERVICE_DIR%\logs\cron_sync_odds_data.log
echo    • %SPORTS_SERVICE_DIR%\logs\cron_health_check.log
echo.
echo 🔧 Quản lý Task Scheduler:
echo    • Mở Task Scheduler: taskschd.msc
echo    • Xem tasks: Get-ScheduledTask -TaskName "SportsDataService*"
echo    • Xóa task: Unregister-ScheduledTask -TaskName "TaskName"
echo.
echo 📊 Kiểm tra logs:
echo    • type "%SPORTS_SERVICE_DIR%\logs\cron_sync_sports_data.log"
echo    • type "%SPORTS_SERVICE_DIR%\logs\cron_sync_odds_data.log"

pause
