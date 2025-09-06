import os

# Middleware Configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sports_data.middleware.ip_whitelist.IPWhitelistMiddleware',  # IP Whitelisting
    'sports_data.api_versioning.APIVersionMiddleware',  # API Versioning
]

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_EXPIRY = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRY', 15))  # 15 phút
JWT_REFRESH_TOKEN_EXPIRY = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRY', 7))  # 7 ngày

# IP Whitelist Configuration
IP_WHITELIST = [
    '127.0.0.1',           # Localhost
    '::1',                  # IPv6 localhost
    '192.168.1.0/24',      # Local network
    '10.0.0.0/8',          # Private network
    '172.16.0.0/12',       # Private network
]
