# 🚀 Hướng dẫn sử dụng GitHub cho SPORT_BETTING_MODULE

## 📋 Tổng quan

Dự án SPORT_BETTING_MODULE đã được đưa lên GitHub tại: https://github.com/dinhthe9212/SPORT_BETTING_MODULE

## 🔧 Các bước đã thực hiện

### 1. ✅ Khởi tạo Git Repository
- Khởi tạo Git repository trong thư mục dự án
- Cấu hình remote origin trỏ đến GitHub repository

### 2. ✅ Bảo mật thông tin nhạy cảm
- Cập nhật `.gitignore` để loại trừ file `.env` và các file nhạy cảm khác
- Đảm bảo file `.env` chứa mật khẩu và API keys không được commit

### 3. ✅ Tạo tài liệu dự án
- Tạo file `LICENSE` với MIT License
- Cập nhật `README.md` với thông tin repository GitHub
- Giữ nguyên file `.env.example` làm template

### 4. ✅ Commit và Push
- Commit tất cả code với message mô tả chi tiết
- Push code lên GitHub repository

## 🎯 Cách sử dụng GitHub Repository

### Clone dự án từ GitHub

```bash
# Clone repository về máy local
git clone https://github.com/dinhthe9212/SPORT_BETTING_MODULE.git
cd SPORT_BETTING_MODULE

# Cài đặt dependencies
pip install -r requirements.txt

# Copy file environment
cp .env.example .env

# Chỉnh sửa file .env với thông tin thực tế
nano .env
```

### Cập nhật code lên GitHub

```bash
# Thêm thay đổi vào staging area
git add .

# Commit với message mô tả
git commit -m "feat: thêm tính năng mới"

# Push lên GitHub
git push origin main
```

### Tạo Branch mới cho tính năng

```bash
# Tạo và chuyển sang branch mới
git checkout -b feature/tên-tính-năng

# Làm việc trên branch này
# ... code changes ...

# Commit thay đổi
git add .
git commit -m "feat: mô tả tính năng"

# Push branch lên GitHub
git push origin feature/tên-tính-năng

# Tạo Pull Request trên GitHub
```

### Đồng bộ với GitHub

```bash
# Lấy thay đổi mới nhất từ GitHub
git pull origin main

# Xem trạng thái repository
git status

# Xem lịch sử commit
git log --oneline
```

## 🔒 Bảo mật

### File không được commit
- `.env` - Chứa thông tin nhạy cảm
- `.env.local` - Environment local
- `.env.production` - Environment production
- `logs/` - File log
- `__pycache__/` - Python cache
- `*.pyc` - Python compiled files

### Các file quan trọng
- `.env.example` - Template cho environment variables
- `README.md` - Tài liệu chính của dự án
- `LICENSE` - Giấy phép sử dụng
- `requirements.txt` - Dependencies Python

## 📚 Tài liệu GitHub

### Issues
- Tạo issue để báo lỗi: https://github.com/dinhthe9212/SPORT_BETTING_MODULE/issues
- Sử dụng labels để phân loại: bug, enhancement, documentation

### Pull Requests
- Tạo PR để đóng góp code
- Sử dụng template có sẵn
- Yêu cầu review trước khi merge

### Wiki
- Tài liệu chi tiết: https://github.com/dinhthe9212/SPORT_BETTING_MODULE/wiki
- Hướng dẫn cài đặt và sử dụng
- API documentation

## 🚀 Deployment từ GitHub

### Sử dụng GitHub Actions (CI/CD)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy
        run: |
          # Script deployment
```

### Clone và chạy trên server
```bash
# Trên server production
git clone https://github.com/dinhthe9212/SPORT_BETTING_MODULE.git
cd SPORT_BETTING_MODULE

# Cấu hình environment
cp .env.example .env
nano .env  # Cập nhật với thông tin production

# Chạy với Docker
docker-compose -f docker-compose.production.yml up -d
```

## 📊 Monitoring và Analytics

### GitHub Insights
- Xem thống kê commit, contributors
- Theo dõi traffic và downloads
- Phân tích code quality

### Dependencies
- Kiểm tra security vulnerabilities
- Cập nhật dependencies tự động
- Quản lý package versions

## 🤝 Collaboration

### Fork và Contribute
1. Fork repository về tài khoản của bạn
2. Clone fork về máy local
3. Tạo branch mới cho tính năng
4. Commit và push lên fork
5. Tạo Pull Request về repository gốc

### Code Review
- Review code trước khi merge
- Sử dụng comments để thảo luận
- Yêu cầu approval từ maintainers

## 📞 Hỗ trợ

- **Repository**: https://github.com/dinhthe9212/SPORT_BETTING_MODULE
- **Issues**: https://github.com/dinhthe9212/SPORT_BETTING_MODULE/issues
- **Wiki**: https://github.com/dinhthe9212/SPORT_BETTING_MODULE/wiki
- **Releases**: https://github.com/dinhthe9212/SPORT_BETTING_MODULE/releases

---

**Lưu ý**: Luôn cập nhật tài liệu khi có thay đổi code và đảm bảo tuân thủ các quy tắc bảo mật khi làm việc với GitHub.
