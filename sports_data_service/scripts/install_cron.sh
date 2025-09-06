#!/bin/bash

# Script cài đặt cron jobs cho Sports Data Service
# Chạy với quyền root: sudo ./install_cron.sh

echo "🚀 Cài đặt cron jobs cho Sports Data Service..."

# Lấy đường dẫn hiện tại
CURRENT_DIR=$(pwd)
SPORTS_SERVICE_DIR="$CURRENT_DIR"

# Kiểm tra quyền root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Vui lòng chạy script này với quyền root (sudo)"
    exit 1
fi

# Kiểm tra thư mục sports_data_service
if [ ! -d "$SPORTS_SERVICE_DIR" ]; then
    echo "❌ Không tìm thấy thư mục sports_data_service"
    exit 1
fi

echo "📁 Thư mục Sports Data Service: $SPORTS_SERVICE_DIR"

# Tạo script cron wrapper
CRON_SCRIPT="$SPORTS_SERVICE_DIR/scripts/cron_wrapper.sh"

cat > "$CRON_SCRIPT" << 'EOF'
#!/bin/bash

# Cron wrapper script cho Sports Data Service
# Được gọi bởi cron jobs

SPORTS_SERVICE_DIR="$1"
COMMAND="$2"
LOG_FILE="$SPORTS_SERVICE_DIR/logs/cron_$COMMAND.log"

# Tạo thư mục logs nếu chưa có
mkdir -p "$SPORTS_SERVICE_DIR/logs"

# Chuyển đến thư mục sports_data_service
cd "$SPORTS_SERVICE_DIR"

# Thực hiện command và log output
echo "$(date): Bắt đầu thực hiện $COMMAND" >> "$LOG_FILE"

case "$COMMAND" in
    "sync_sports_data")
        python manage.py sync_sports_data >> "$LOG_FILE" 2>&1
        ;;
    "sync_odds_data")
        python manage.py sync_odds_data >> "$LOG_FILE" 2>&1
        ;;
    "health_check")
        python manage.py check >> "$LOG_FILE" 2>&1
        ;;
    *)
        echo "$(date): Command không hợp lệ: $COMMAND" >> "$LOG_FILE"
        exit 1
        ;;
esac

echo "$(date): Hoàn thành $COMMAND" >> "$LOG_FILE"
EOF

# Cấp quyền thực thi cho script
chmod +x "$CRON_SCRIPT"

echo "✅ Đã tạo cron wrapper script: $CRON_SCRIPT"

# Tạo cron jobs
echo "📅 Đang tạo cron jobs..."

# Xóa cron jobs cũ nếu có
(crontab -l 2>/dev/null | grep -v "sports_data_service") | crontab -

# Thêm cron jobs mới
(crontab -l 2>/dev/null; cat << EOF
# Sports Data Service - Đồng bộ dữ liệu thể thao mỗi 5 phút
*/5 * * * * $CRON_SCRIPT $SPORTS_SERVICE_DIR sync_sports_data

# Sports Data Service - Đồng bộ tỷ lệ cược mỗi 10 phút
*/10 * * * * $CRON_SCRIPT $SPORTS_SERVICE_DIR sync_odds_data

# Sports Data Service - Health check mỗi giờ
0 * * * * $CRON_SCRIPT $SPORTS_SERVICE_DIR health_check

# Sports Data Service - Đồng bộ đầy đủ mỗi ngày lúc 6:00 AM
0 6 * * * $CRON_SCRIPT $SPORTS_SERVICE_DIR sync_sports_data

# Sports Data Service - Đồng bộ odds đầy đủ mỗi ngày lúc 6:30 AM
30 6 * * * $CRON_SCRIPT $SPORTS_SERVICE_DIR sync_odds_data
EOF
) | crontab -

echo "✅ Đã tạo cron jobs thành công!"

# Hiển thị cron jobs hiện tại
echo "📋 Cron jobs hiện tại:"
crontab -l | grep "sports_data_service"

# Tạo thư mục logs
mkdir -p "$SPORTS_SERVICE_DIR/logs"
chmod 755 "$SPORTS_SERVICE_DIR/logs"

echo "📁 Đã tạo thư mục logs: $SPORTS_SERVICE_DIR/logs"

# Test cron jobs
echo "🧪 Đang test cron jobs..."

# Test sync_sports_data
echo "   Testing sync_sports_data..."
$CRON_SCRIPT "$SPORTS_SERVICE_DIR" sync_sports_data

# Test sync_odds_data
echo "   Testing sync_odds_data..."
$CRON_SCRIPT "$SPORTS_SERVICE_DIR" sync_odds_data

echo "✅ Test cron jobs hoàn thành!"

# Hiển thị hướng dẫn
echo ""
echo "🎉 Cài đặt cron jobs hoàn thành!"
echo ""
echo "📋 Cron Jobs đã được tạo:"
echo "   • Đồng bộ dữ liệu thể thao: Mỗi 5 phút"
echo "   • Đồng bộ tỷ lệ cược: Mỗi 10 phút"
echo "   • Health check: Mỗi giờ"
echo "   • Đồng bộ đầy đủ: Mỗi ngày 6:00 AM"
echo "   • Đồng bộ odds đầy đủ: Mỗi ngày 6:30 AM"
echo ""
echo "📁 Log files:"
echo "   • $SPORTS_SERVICE_DIR/logs/cron_sync_sports_data.log"
echo "   • $SPORTS_SERVICE_DIR/logs/cron_sync_odds_data.log"
echo "   • $SPORTS_SERVICE_DIR/logs/cron_health_check.log"
echo ""
echo "🔧 Quản lý cron jobs:"
echo "   • Xem cron jobs: crontab -l"
echo "   • Chỉnh sửa cron jobs: crontab -e"
echo "   • Xóa tất cả cron jobs: crontab -r"
echo ""
echo "📊 Kiểm tra logs:"
echo "   • tail -f $SPORTS_SERVICE_DIR/logs/cron_sync_sports_data.log"
echo "   • tail -f $SPORTS_SERVICE_DIR/logs/cron_sync_odds_data.log"
