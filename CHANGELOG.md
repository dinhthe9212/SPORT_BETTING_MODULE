# Changelog

Tất cả các thay đổi quan trọng của dự án SPORT_BETTING_MODULE sẽ được ghi lại trong file này.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án tuân thủ [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- **Shared Module**: Tạo module chung với base_settings, common_models, utils, middleware, constants
- **Betting Service**: Service quản lý cá cược với đầy đủ tính năng
- **Carousel Service**: Service hiển thị nội dung động với WebSocket support
- **Individual Bookmaker Service**: Service quản lý nhà cái cá nhân
- **Risk Management Service**: Service quản lý rủi ro và ngưỡng
- **Saga Orchestrator**: Service điều phối giao dịch phân tán
- **Sports Data Service**: Service cung cấp dữ liệu thể thao real-time
- **Docker Support**: Docker Compose setup cho toàn bộ hệ thống
- **Nginx Configuration**: Reverse proxy và load balancing
- **Makefile**: Commands để quản lý dự án
- **Environment Templates**: File .env.example cho tất cả services
- **Health Checks**: Endpoints kiểm tra trạng thái services
- **API Documentation**: Tài liệu API đầy đủ
- **Integration Guide**: Hướng dẫn tích hợp chi tiết

### Changed
- **Standardized Configuration**: Chuẩn hóa cấu hình cho tất cả services
- **Database Setup**: Tách database riêng cho từng service
- **Redis Configuration**: Sử dụng Redis DB khác nhau cho từng service
- **Logging System**: Hệ thống logging thống nhất với JSON format
- **Security Middleware**: Middleware bảo mật chung cho tất cả services
- **Error Handling**: Xử lý lỗi thống nhất với ResponseFormatter

### Fixed
- **Import Errors**: Sửa lỗi import shared module
- **Database Connections**: Sửa cấu hình kết nối database
- **Service Communication**: Sửa giao tiếp giữa các services
- **Configuration Issues**: Sửa các vấn đề cấu hình
- **Dependencies**: Cập nhật và chuẩn hóa dependencies

### Security
- **API Keys**: Hệ thống API keys cho service-to-service communication
- **Rate Limiting**: Giới hạn request rate
- **Security Headers**: Thêm security headers
- **Input Validation**: Validation đầu vào
- **SQL Injection Protection**: Bảo vệ khỏi SQL injection

## [0.9.0] - 2024-01-10

### Added
- **Initial Project Structure**: Cấu trúc dự án ban đầu
- **Basic Services**: Các service cơ bản
- **Database Models**: Models cơ bản cho từng service
- **API Endpoints**: Endpoints cơ bản
- **Basic Authentication**: Xác thực cơ bản

### Changed
- **Project Organization**: Tổ chức lại cấu trúc dự án
- **Code Quality**: Cải thiện chất lượng code

### Fixed
- **Initial Bugs**: Sửa các lỗi ban đầu
- **Configuration Issues**: Sửa vấn đề cấu hình

## [0.8.0] - 2024-01-05

### Added
- **Project Planning**: Lập kế hoạch dự án
- **Architecture Design**: Thiết kế kiến trúc
- **Technology Stack**: Lựa chọn công nghệ
- **Requirements Analysis**: Phân tích yêu cầu

### Changed
- **Project Scope**: Điều chỉnh phạm vi dự án
- **Timeline**: Cập nhật timeline

---

## Legend

- **Added** cho các tính năng mới
- **Changed** cho các thay đổi trong chức năng hiện có
- **Deprecated** cho các tính năng sắp bị loại bỏ
- **Removed** cho các tính năng đã bị loại bỏ
- **Fixed** cho các lỗi đã được sửa
- **Security** cho các cải tiến bảo mật
