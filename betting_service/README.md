# BETTING SERVICE - Microservice

## Overview

Betting Service is a microservice responsible for managing all P2P betting activities in the system.

## Main Features

- **Core Functionality**: Core functionality of the service
- **API Management**: API endpoints management
- **Data Processing**: Data processing capabilities
- **Integration**: Integration with other services
- **Monitoring**: Monitoring and logging

## Installation and Setup

### Prerequisites

- Python 3.8+
- PostgreSQL/MySQL
- Redis (if needed)
- Docker (optional)

### Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

```bash
# Database
DB_NAME=betting_service_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=postgres
DB_PORT=5432

# Redis (if needed)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Security
SECRET_KEY=your-secret-key
DEBUG=True
```

### Running the Service

```bash
# Development
python manage.py runserver

# Production
gunicorn betting_service_project.wsgi:application --bind 0.0.0.0:8000
```

## API Endpoints

### Core Endpoints
- `GET /api/health/` - Health check
- `GET /api/status/` - Service status

### Service-Specific Endpoints
- Service-specific endpoints will be added here

## Project Structure

```
betting_service/
├── betting_service_project/     # Django project settings
├── [app_folders]/              # Django apps
├── documentation/               # Technical documentation
│   ├── implementation/         # Implementation docs
│   ├── security/              # Security docs
│   ├── testing/               # Testing docs
│   ├── guides/                # Usage guides
│   └── changelog/             # Change history
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

## Security Features

### Basic Security
- **Authentication**: User authentication
- **Authorization**: Access control
- **Input Validation**: Input validation
- **Rate Limiting**: Request rate limiting

## Monitoring and Logging

### Logging Configuration
- **Format**: JSON structured logging
- **Level**: INFO (root), DEBUG (service-specific)
- **Output**: Console and file logs

### Metrics
- **Health Checks**: Service health monitoring
- **Performance Metrics**: Performance tracking

## Testing

### Unit Tests
```bash
python manage.py test
```

### Integration Tests
```bash
python manage.py test --settings=betting_service_project.test_settings
```

## Deployment

### Docker
```bash
docker build -t betting_service .
docker run -p 8000:8000 betting_service
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## Troubleshooting

### Common Issues
1. **Database Connection**: Check database service and connection string
2. **Migration**: Run `python manage.py migrate`
3. **Dependencies**: Check `requirements.txt`

### Logs
```bash
# View service logs
tail -f logs/betting_service.log

# View Django logs
python manage.py runserver --verbosity=2
```

## Documentation

See detailed documentation in the [documentation/](./documentation/README.md) folder

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

- **Documentation**: [documentation/README.md](./documentation/README.md)
- **Issues**: GitHub Issues
- **Team**: Development Team
