# Hướng Dẫn Code Quality và Linting

## Tổng Quan

Dự án SPORT_BETTING_MODULE đã được tích hợp các công cụ code quality để đảm bảo mã nguồn nhất quán, dễ đọc và tuân thủ các tiêu chuẩn Python.

## Công Cụ Được Sử Dụng

### 1. Black - Code Formatter
- **Mục đích**: Tự động định dạng code Python
- **Cấu hình**: Line length = 88, target Python 3.11
- **File cấu hình**: `pyproject.toml`

### 2. Flake8 - Linter
- **Mục đích**: Kiểm tra lỗi code và phong cách
- **Cấu hình**: Max line length = 88, ignore E203, W503, E501
- **File cấu hình**: `.flake8` và `pyproject.toml`

### 3. isort - Import Sorter
- **Mục đích**: Sắp xếp và tổ chức import statements
- **Cấu hình**: Tương thích với Black, profile = "black"
- **File cấu hình**: `pyproject.toml`

## Cách Sử Dụng

### Lệnh Makefile

```bash
# Chạy tất cả kiểm tra code quality
make lint-all

# Chỉ chạy linting (Flake8)
make lint

# Format code với Black và isort
make format

# Kiểm tra formatting mà không thay đổi code
make format-check
```

### Lệnh Trực Tiếp

```bash
# Format code
black . --line-length=88
isort . --profile black

# Chạy linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Kiểm tra formatting
black . --check --line-length=88
isort . --check-only --profile black
```

## Cấu Hình Chi Tiết

### Black Configuration
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
  | migrations
  | __pycache__
)/
'''
```

### Flake8 Configuration
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = 
    .git,
    __pycache__,
    migrations,
    venv,
    env,
    .venv,
    .env,
    build,
    dist,
    *.egg-info
per-file-ignores =
    __init__.py:F401
    migrations/*:E501
    */migrations/*:E501
```

### isort Configuration
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_django = "django"
known_first_party = ["shared", "betting", "carousel", "individual_bookmaker", "risk_management", "saga_orchestrator", "sports_data"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "DJANGO", "FIRSTPARTY", "LOCALFOLDER"]
skip_glob = ["*/migrations/*"]
```

## Quy Trình Phát Triển

### 1. Trước Khi Commit
```bash
# Chạy tất cả kiểm tra
make lint-all

# Nếu có lỗi, format code
make format

# Chạy lại kiểm tra
make lint-all
```

### 2. Trong IDE/Editor
- Cài đặt extension cho Black, Flake8, isort
- Cấu hình auto-format on save
- Hiển thị linting errors real-time

### 3. CI/CD Pipeline
```yaml
# Thêm vào pipeline
- name: Code Quality Check
  run: make lint-all
```

## Lợi Ích

1. **Nhất quán**: Code style đồng nhất trong toàn bộ dự án
2. **Chất lượng**: Phát hiện lỗi sớm trong quá trình phát triển
3. **Dễ đọc**: Code được format theo chuẩn Python
4. **Bảo trì**: Dễ dàng review và maintain code
5. **Tự động hóa**: Giảm thời gian manual formatting

## Troubleshooting

### Lỗi Thường Gặp

1. **Black conflicts với isort**
   - Chạy `isort . --profile black` trước
   - Sau đó chạy `black .`

2. **Flake8 báo lỗi line length**
   - Kiểm tra cấu hình max-line-length = 88
   - Đảm bảo Black và Flake8 có cùng line length

3. **Import sorting conflicts**
   - Sử dụng `isort . --profile black` để tương thích với Black

### Cấu Hình IDE

#### VS Code
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.sortImports.args": ["--profile", "black"]
}
```

#### PyCharm
- Cài đặt Black, Flake8, isort plugins
- Cấu hình external tools
- Enable auto-format on save

## Cập Nhật

Để cập nhật các công cụ:

```bash
pip install --upgrade black flake8 isort
```

Kiểm tra version:
```bash
black --version
flake8 --version
isort --version
```
