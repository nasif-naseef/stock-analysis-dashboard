# Deployment Guide

## Development Environment

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/nasif-naseef/stock-analysis-dashboard.git
cd stock-analysis-dashboard
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API tokens
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Run database migrations**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Commands

```bash
# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Clean everything
docker-compose down -v --rmi all
```

## Production Deployment

### Prerequisites
- Docker & Docker Compose installed
- Domain name configured
- SSL certificate (Let's Encrypt recommended)

### Deployment Steps

1. **Prepare environment**
```bash
cp .env.production .env
# Edit .env with production values
```

2. **Build production images**
```bash
docker-compose -f docker-compose.prod.yml build
```

3. **Start production services**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. **Run migrations**
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

5. **Verify deployment**
```bash
docker-compose -f docker-compose.prod.yml ps
```

### SSL Configuration

Use a reverse proxy like Nginx or Traefik with Let's Encrypt:

```bash
# Example with Certbot
certbot --nginx -d yourdomain.com
```

### Monitoring

Check service health:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Backup

Backup database:
```bash
docker-compose exec db pg_dump -U stockuser stockdb > backup.sql
```

### Updates

```bash
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Database connection issues
```bash
docker-compose logs db
docker-compose exec db psql -U stockuser -d stockdb
```

### Backend not starting
```bash
docker-compose logs backend
docker-compose exec backend python -c "from app.database import engine; print(engine)"
```

### Frontend not loading
```bash
docker-compose logs frontend
# Check if backend is accessible
curl http://localhost:8000/health
```
