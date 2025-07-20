# Deployment Documentation - Draft_2 Project Management Platform

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Docker Deployment](#docker-deployment)
3. [Local Development Deployment](#local-development-deployment)
4. [Production Deployment Options](#production-deployment-options)
5. [Environment Configuration](#environment-configuration)
6. [Database Deployment](#database-deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Security Hardening](#security-hardening)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Scaling Considerations](#scaling-considerations)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Maintenance Procedures](#maintenance-procedures)

---

## 1. Deployment Overview

The Draft_2 Project Management Platform is a modern full-stack web application designed for containerized deployment with comprehensive project management capabilities.

### Technology Stack
- **Frontend**: React 19.1.0 with Vite 7.0.4, Material-UI 7.2.0
- **Backend**: Flask 3.0.0 with SQLAlchemy 2.0.23  
- **Database**: SQLite (development), PostgreSQL-ready (production)
- **Security**: bcrypt 4.1.2, paramiko 3.4.0
- **Containerization**: Docker with multi-stage builds

### Deployment Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │  Docker Container│    │    Database     │
│   (nginx/proxy) │────│                 │────│   (SQLite/PG)   │
│                 │    │  Flask:5000     │    │                 │
│                 │    │  Vite:5173      │    │                 │
│                 │    │  SSH:2200       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Infrastructure Requirements
- **Minimum**: 1 CPU, 2GB RAM, 10GB storage
- **Recommended**: 2+ CPUs, 4GB RAM, 50GB+ storage  
- **Production**: 4+ CPUs, 8GB RAM, 100GB+ storage
- **Network**: Ports 5000, 5173, 2200 accessible

### Security Considerations
- Non-root container execution
- Encrypted password storage (bcrypt)
- SSH server for secure connections
- Role-based access control (RBAC)
- Input validation and sanitization

---

## 2. Docker Deployment

### Current Dockerfile Analysis

The existing [`Dockerfile`](Dockerfile:1) implements security best practices:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY app/ ./app/
COPY config/ ./config/

# Set proper ownership
RUN chown -R appuser:appuser /home/appuser/app
USER appuser

# Expose SSH server port
EXPOSE 2200

# Start SSH server
CMD ["python", "app/server.py"]
```

### Container Build Process

#### Building the Image
```bash
# Basic build
docker build -t draft2-project-mgmt .

# Production build with version tag
docker build -t draft2-project-mgmt:v1.0.0 .

# Build with custom build args
docker build --build-arg PYTHON_VERSION=3.11 -t draft2-project-mgmt .
```

#### Image Optimization Strategies

**Multi-stage Build (Recommended)**
```dockerfile
# syntax=docker/dockerfile:1

# Build stage
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY ui/package*.json ./
RUN npm ci --only=production
COPY ui/ ./
RUN npm run build

# Production stage  
FROM python:3.11-slim AS production
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY app/ ./app/
COPY config/ ./config/
COPY --from=frontend-build /app/dist ./static/

RUN chown -R appuser:appuser /home/appuser/app
USER appuser

EXPOSE 5000 2200

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

CMD ["python", "app/api_server.py"]
```

### Port Configuration

| Port | Service | Description |
|------|---------|-------------|
| 5000 | Flask API | Backend REST API server |
| 5173 | Vite Dev Server | Frontend development server |
| 2200 | SSH Server | Secure shell access (paramiko) |

### Volume Mounting for Persistent Data

**Development Environment**
```bash
docker run -d \
  --name draft2-dev \
  -p 5000:5000 -p 2200:2200 -p 5173:5173 \
  -v $(pwd)/app:/home/appuser/app/app \
  -v $(pwd)/ui:/home/appuser/app/ui \
  -v draft2-db:/home/appuser/app/data \
  draft2-project-mgmt
```

**Production Environment**
```bash
docker run -d \
  --name draft2-prod \
  -p 5000:5000 -p 2200:2200 \
  -v draft2-data:/home/appuser/app/data \
  -v draft2-config:/home/appuser/app/config \
  -v draft2-logs:/home/appuser/app/logs \
  --restart unless-stopped \
  draft2-project-mgmt:v1.0.0
```

### Environment Variable Configuration

```bash
# Database configuration
AUTH_DB_PATH=/home/appuser/app/data/auth.db
DATABASE_URL=sqlite:///data/auth.db  # or postgresql://...

# Flask configuration
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key-here
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# SSH server configuration
SSH_HOST_KEY_PATH=/home/appuser/app/config/host_key.txt
SSH_PORT=2200

# Security settings
BCRYPT_LOG_ROUNDS=12
SESSION_TIMEOUT=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/appuser/app/logs/app.log
```

---

## 3. Local Development Deployment

### Prerequisites Installation

#### Python Environment (Backend)
```bash
# Install Python 3.11+
python --version  # Verify Python 3.11+

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Node.js Environment (Frontend)
```bash
# Install Node.js 18+
node --version  # Verify Node 18+
npm --version   # Verify npm

# Navigate to UI directory
cd ui/

# Install dependencies
npm install
```

#### Docker Environment
```bash
# Install Docker
docker --version
docker-compose --version

# Verify Docker is running
docker run hello-world
```

### Backend Setup (Flask Server)

#### Database Initialization
```bash
# Initialize database schema
python app/db.py

# Verify database creation
ls -la app/auth.db

# Create admin user (optional)
python -c "
from app.db import register_user
register_user('admin', 'secure_password', 'admin')
print('Admin user created')
"
```

#### Start Flask API Server
```bash
# Development mode
python app/api_server.py

# Production mode with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app.api_server:app
```

#### Verify Backend
```bash
# Test API endpoints
curl http://localhost:5000/api/users
curl http://localhost:5000/api/user-count

# Expected response format
{
  "count": 0
}
```

### Frontend Setup (React with Vite)

#### Start Development Server
```bash
cd ui/

# Start Vite development server
npm run dev

# Server will start on http://localhost:5173
```

#### Build for Production
```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

#### Verify Frontend
- Navigate to http://localhost:5173
- Verify authentication page loads
- Check developer console for errors
- Test API connectivity to http://localhost:5000

### Running in Development Mode

#### Option 1: Separate Processes
```bash
# Terminal 1 - Backend
python app/api_server.py

# Terminal 2 - Frontend  
cd ui && npm run dev

# Terminal 3 - SSH Server (if needed)
python app/server.py
```

#### Option 2: Docker Development
```bash
# Build development image
docker build -t draft2-dev .

# Run with development mounts
docker run -it --rm \
  -p 5000:5000 -p 5173:5173 -p 2200:2200 \
  -v $(pwd):/home/appuser/app \
  draft2-dev
```

---

## 4. Production Deployment Options

### Docker Compose Setup

#### Basic docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
      - "2200:2200"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/draft2_db
    depends_on:
      - db
    volumes:
      - app_data:/home/appuser/app/data
      - app_logs:/home/appuser/app/logs
    restart: unless-stopped
    
  frontend:
    build:
      context: ./ui
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - app
    restart: unless-stopped
      
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: draft2_db
      POSTGRES_USER: draft2_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
      - frontend
    restart: unless-stopped

volumes:
  app_data:
  app_logs:  
  postgres_data:
```

#### Deployment Commands
```bash
# Start all services
docker-compose up -d

# Scale application instances
docker-compose up -d --scale app=3

# View logs
docker-compose logs -f app

# Update application
docker-compose pull && docker-compose up -d
```

### Cloud Deployment

#### AWS Deployment (ECS)
```yaml
# ecs-task-definition.json
{
  "family": "draft2-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "draft2-app",
      "image": "your-registry/draft2-project-mgmt:latest",
      "portMappings": [
        {"containerPort": 5000, "protocol": "tcp"},
        {"containerPort": 2200, "protocol": "tcp"}
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "FLASK_ENV", "value": "production"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/draft2-app",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Azure Deployment (Container Instances)
```bash
# Create resource group
az group create --name draft2-rg --location eastus

# Deploy container instance
az container create \
  --resource-group draft2-rg \
  --name draft2-app \
  --image your-registry/draft2-project-mgmt:latest \
  --cpu 2 --memory 4 \
  --ports 5000 2200 \
  --environment-variables \
    FLASK_ENV=production \
    DATABASE_URL="postgresql://..." \
  --restart-policy Always
```

#### GCP Deployment (Cloud Run)
```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: draft2-app
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/draft2-project-mgmt:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          value: "postgresql://..."
        - name: FLASK_ENV  
          value: "production"
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
```

### VPS Deployment (Traditional Server)

#### Ubuntu 22.04 Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-repo/draft2-project-mgmt.git
cd draft2-project-mgmt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Deploy application
docker-compose up -d

# Configure nginx reverse proxy
sudo apt install nginx
sudo cp nginx.conf /etc/nginx/sites-available/draft2
sudo ln -s /etc/nginx/sites-available/draft2 /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### Kubernetes Deployment

#### Kubernetes Manifests
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: draft2-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: draft2
  template:
    metadata:
      labels:
        app: draft2
    spec:
      containers:
      - name: app
        image: draft2-project-mgmt:v1.0.0
        ports:
        - containerPort: 5000
        - containerPort: 2200
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: draft2-secrets
              key: database-url
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/ready  
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service  
metadata:
  name: draft2-service
spec:
  selector:
    app: draft2
  ports:
  - name: http
    port: 80
    targetPort: 5000
  - name: ssh
    port: 2200
    targetPort: 2200
  type: LoadBalancer
```

---

## 5. Environment Configuration

### Environment Variables Setup

#### Development Environment (.env.dev)
```bash
# Application settings
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Database configuration
AUTH_DB_PATH=app/auth.db
DATABASE_URL=sqlite:///app/auth.db

# Security settings
FLASK_SECRET_KEY=dev-secret-key-change-in-production
BCRYPT_LOG_ROUNDS=4  # Faster for development

# SSH server settings
SSH_PORT=2200
SSH_HOST_KEY_PATH=config/host_key.txt

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# Frontend configuration
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_ENV=development
```

#### Production Environment (.env.prod)
```bash
# Application settings
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Database configuration (PostgreSQL)
DATABASE_URL=postgresql://draft2_user:secure_password@db:5432/draft2_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30

# Security settings
FLASK_SECRET_KEY=your-super-secure-secret-key-here
BCRYPT_LOG_ROUNDS=12  # Production strength

# SSH server settings
SSH_PORT=2200
SSH_HOST_KEY_PATH=/home/appuser/app/config/host_key.txt

# Session management
SESSION_TIMEOUT=3600
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/appuser/app/logs/app.log
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Frontend configuration  
VITE_API_BASE_URL=https://api.yourdomain.com/api
VITE_APP_ENV=production

# Performance settings
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### Database Configuration

#### SQLite to PostgreSQL Migration

**Migration Script (migrate_to_postgres.py)**
```python
import os
import sqlite3
import psycopg2
from sqlalchemy import create_engine
from app.db import Base

def migrate_sqlite_to_postgres():
    # Source (SQLite)
    sqlite_db = 'app/auth.db'
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_conn.row_factory = sqlite3.Row
    
    # Destination (PostgreSQL)
    postgres_url = os.getenv('DATABASE_URL')
    postgres_engine = create_engine(postgres_url)
    
    # Create tables
    Base.metadata.create_all(postgres_engine)
    
    # Migrate data
    with postgres_engine.connect() as pg_conn:
        # Migrate users
        users = sqlite_conn.execute('SELECT * FROM users').fetchall()
        for user in users:
            pg_conn.execute(
                'INSERT INTO users (username, password_hash, created_at) VALUES (%s, %s, %s)',
                (user['username'], user['password_hash'], user['created_at'])
            )
        
        # Migrate other tables...
        pg_conn.commit()
    
    print("Migration completed successfully")

if __name__ == '__main__':
    migrate_sqlite_to_postgres()
```

### Secret Management

#### Using Docker Secrets
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    image: draft2-project-mgmt:latest
    secrets:
      - db_password
      - flask_secret_key
    environment:
      - DATABASE_URL=postgresql://draft2_user:$(cat /run/secrets/db_password)@db:5432/draft2_db
      - FLASK_SECRET_KEY_FILE=/run/secrets/flask_secret_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  flask_secret_key:
    file: ./secrets/flask_secret_key.txt
```

#### Using Kubernetes Secrets
```bash
# Create secrets
kubectl create secret generic draft2-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=flask-secret-key="your-secret-key"

# Use in deployment
env:
- name: FLASK_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: draft2-secrets
      key: flask-secret-key
```

### SSL/TLS Configuration

#### nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    location / {
        proxy_pass http://127.0.0.1:5173;  # Frontend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;  # Backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### CORS Configuration

#### Flask CORS Setup
```python
# app/api_server.py
from flask_cors import CORS

app = Flask(__name__)

# Production CORS configuration
if app.config['ENV'] == 'production':
    CORS(app, origins=['https://yourdomain.com'])
else:
    # Development CORS configuration
    CORS(app, origins=['http://localhost:5173'])
```

---

## 6. Database Deployment

### SQLite Setup for Development

#### Basic Configuration
```python
# app/db.py
import os
from sqlalchemy import create_engine

# Development database path
DB_PATH = os.getenv("AUTH_DB_PATH", "app/auth.db")
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)
```

#### Initialization Script
```bash
#!/bin/bash
# scripts/init_dev_db.sh

# Create database directory
mkdir -p app/

# Initialize database
python app/db.py

# Create admin user
python -c "
from app.db import register_user, init_db
init_db()
register_user('admin', 'admin123', 'admin')
register_user('user', 'user123', 'user')
print('Development users created')
"
```

### PostgreSQL Setup for Production

#### Docker PostgreSQL Service
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: draft2_db
      POSTGRES_USER: draft2_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    secrets:
      - db_password
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U draft2_user -d draft2_db"]
      interval: 30s
      timeout: 10s
      retries: 5

secrets:
  db_password:
    file: ./secrets/db_password.txt

volumes:
  postgres_data:
```

#### Production Database Configuration
```python
# app/config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class ProductionConfig:
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Connection pooling settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': QueuePool,
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'pool_pre_ping': True
    }

# Create production engine
engine = create_engine(
    ProductionConfig.DATABASE_URL,
    **ProductionConfig.SQLALCHEMY_ENGINE_OPTIONS
)
```

### Database Migration Procedures

#### Alembic Migration Setup
```bash
# Install Alembic
pip install alembic

# Initialize migration repository
alembic init migrations

# Configure alembic.ini
sqlalchemy.url = postgresql://draft2_user:password@localhost/draft2_db
```

#### Migration Scripts
```python
# migrations/env.py
from app.db import Base
target_metadata = Base.metadata

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Backup and Recovery Procedures

#### PostgreSQL Backup Script
```bash
#!/bin/bash
# scripts/backup_db.sh

BACKUP_DIR="/backups/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="draft2_db"
DB_USER="draft2_user"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME -F c -b -v -f "$BACKUP_DIR/backup_$TIMESTAMP.dump"

# Compress backup
gzip "$BACKUP_DIR/backup_$TIMESTAMP.dump"

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.dump.gz" -mtime +7 -delete

echo "Backup completed: backup_$TIMESTAMP.dump.gz"
```

#### Recovery Script
```bash
#!/bin/bash
# scripts/restore_db.sh

BACKUP_FILE=$1
DB_NAME="draft2_db"
DB_USER="draft2_user"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Drop existing database
dropdb -h localhost -U $DB_USER $DB_NAME

# Create new database
createdb -h localhost -U $DB_USER $DB_NAME

# Restore from backup
pg_restore -h localhost -U $DB_USER -d $DB_NAME -v "$BACKUP_FILE"

echo "Database restored from $BACKUP_FILE"
```

#### Automated Backup Schedule (cron)
```bash
# Add to crontab: crontab -e
# Daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_db.sh

# Weekly backup cleanup
0 3 * * 0 /path/to/scripts/cleanup_old_backups.sh
```

### Connection Pooling

#### SQLAlchemy Pool Configuration
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, StaticPool

# Production pooling
production_engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of permanent connections
    max_overflow=30,       # Additional connections allowed
    pool_timeout=30,       # Seconds to wait for connection
    pool_recycle=1800,     # Recreate connections after 30 minutes
    pool_pre_ping=True     # Validate connections before use
)

# Development pooling (SQLite)
development_engine = create_engine(
    "sqlite:///app/auth.db",
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 20
    }
)
```

---

## 7. CI/CD Pipeline

### GitHub Actions Workflow

#### Main Workflow (.github/workflows/deploy.yml)
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpassword
          POSTGRES_USER: testuser
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: Run tests
      env:
        DATABASE_URL: postgresql://testuser:testpassword@localhost:5432/testdb
      run: |
        pytest tests/ --cov=app --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add staging deployment commands
        
  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # Add production deployment commands
```

### Build Automation

#### Dockerfile Optimization for CI
```dockerfile
# syntax=docker/dockerfile:1

# Build arguments
ARG PYTHON_VERSION=3.11
ARG NODE_VERSION=20

# Frontend build stage
FROM node:${NODE_VERSION}-alpine AS frontend-builder
WORKDIR /app
COPY ui/package*.json ./
RUN npm ci --only=production
COPY ui/ ./
RUN npm run build

# Backend build stage
FROM python:${PYTHON_VERSION}-slim AS backend-builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:${PYTHON_VERSION}-slim AS production
LABEL org.opencontainers.image.source="https://github.com/your-org/draft2-project-mgmt"

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/appuser/app

# Copy Python packages
COPY --from=backend-builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY app/ ./app/
COPY config/ ./config/
COPY --from=frontend-builder /app/dist ./static/

# Set ownership
RUN chown -R appuser:appuser /home/appuser/app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

EXPOSE 5000 2200

CMD ["python", "app/api_server.py"]
```

### Testing Integration

#### Test Configuration (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests  
    e2e: End-to-end tests
    slow: Slow tests
```

#### Test Structure
```
tests/
├── conftest.py          # Test configuration
├── unit/
│   ├── test_db.py       # Database tests
│   ├── test_auth.py     # Authentication tests
│   └── test_api.py      # API tests
├── integration/
│   ├── test_user_flow.py
│   └── test_project_flow.py
└── e2e/
    ├── test_frontend.py
    └── test_complete_flow.py
```

### Deployment Automation

#### Deployment Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}
DOCKER_REGISTRY="ghcr.io/your-org/draft2-project-mgmt"

echo "Deploying to $ENVIRONMENT with tag $IMAGE_TAG"

# Pull latest image
docker pull "$DOCKER_REGISTRY:$IMAGE_TAG"

# Update docker-compose
export IMAGE_TAG
envsubst < docker-compose.$ENVIRONMENT.yml.template > docker-compose.$ENVIRONMENT.yml

# Deploy with zero downtime
docker-compose -f docker-compose.$ENVIRONMENT.yml up -d --no-deps app

# Health check
echo "Waiting for application to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:5000/api/health; then
        echo "Application is ready"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 10
done

# Cleanup old images
docker image prune -f

echo "Deployment completed successfully"
```

### Rollback Procedures

#### Rollback Script
```bash
#!/bin/bash
# scripts/rollback.sh

PREVIOUS_TAG=${1}
ENVIRONMENT=${2:-production}

if [ -z "$PREVIOUS_TAG" ]; then
    echo "Usage: $0 <previous_tag> [environment]"
    exit 1
fi

echo "Rolling back to $PREVIOUS_TAG in $ENVIRONMENT"

# Stop current deployment
docker-compose -f docker-compose.$ENVIRONMENT.yml down

# Deploy previous version
IMAGE_TAG=$PREVIOUS_TAG
export IMAGE_TAG
envsubst < docker-compose.$ENVIRONMENT.yml.template > docker-compose.$ENVIRONMENT.yml
docker-compose -f docker-compose.$ENVIRONMENT.yml up -d

echo "Rollback completed"
```

---

## 8. Security Hardening

### Container Security Best Practices

#### Secure Dockerfile
```dockerfile
# Use official, minimal base images
FROM python:3.11-slim AS base

# Update packages and remove package manager cache
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with specific UID/GID
RUN groupadd -r appgroup --gid=1001 && \
    useradd -r -g appgroup --uid=1001 --create-home --shell /bin/bash appuser

# Set secure directory permissions
WORKDIR /home/appuser/app
RUN chown -R appuser:appgroup /home/appuser && \
    chmod -R 750 /home/appuser

# Switch to non-root user
USER appuser

# Remove unnecessary capabilities
# In docker-compose or kubernetes, add:
# cap_drop: [ALL]
# cap_add: [CHOWN, SETGID, SETUID]
```

#### Container Runtime Security
```yaml
# docker-compose.yml security settings
version: '3.8'

services:
  app:
    build: .
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    read_only: true
    tmpfs:
      - /tmp
      - /home/appuser/app/logs
    user: "1001:1001"
    restart: unless-stopped
```

### Network Security Configuration

#### nginx Security Configuration
```nginx
server {
    # SSL/TLS Configuration
    listen 443 ssl http2;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    location /api/auth/ {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://backend;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend;
    }
    
    # Hide nginx version
    server_tokens off;
    
    # Prevent access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### Authentication and Authorization Setup

#### Enhanced Flask Security
```python
# app/security.py
from functools import wraps
from flask import request, jsonify, session
from datetime import datetime, timedelta
import jwt
import bcrypt
from app.db import get_user_by_username

class SecurityManager:
    def __init__(self, app):
        self.app = app
        self.secret_key = app.config['SECRET_KEY']
        self.token_expiry = timedelta(hours=1)
        
    def generate_token(self, username):
        """Generate JWT token with expiration"""
        payload = {
