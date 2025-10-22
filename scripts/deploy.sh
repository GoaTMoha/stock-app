#!/bin/bash
# Production deployment script for Stock Manager App

set -e

echo "🚀 Starting Stock Manager App deployment..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run this script as root"
    exit 1
fi

# Configuration
APP_NAME="stock-app"
APP_DIR="/opt/$APP_NAME"
SERVICE_USER="www-data"
PYTHON_VERSION="3.12"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if running on supported OS
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_warning "This script is designed for Linux systems"
    fi
    
    print_status "System requirements check passed"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    sudo apt-get update
    sudo apt-get install -y \
        python3-pip \
        python3-venv \
        nginx \
        postgresql \
        postgresql-contrib \
        redis-server \
        git \
        curl
    
    print_status "System dependencies installed"
}

# Create application directory
setup_app_directory() {
    print_status "Setting up application directory..."
    
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$SERVICE_USER $APP_DIR
    
    print_status "Application directory created: $APP_DIR"
}

# Clone and setup application
setup_application() {
    print_status "Setting up application..."
    
    cd $APP_DIR
    
    # Clone repository (replace with actual repository URL)
    if [ ! -d ".git" ]; then
        print_status "Cloning repository..."
        git clone <repository-url> .
    else
        print_status "Updating repository..."
        git pull origin main
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    print_status "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_status "Application setup completed"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Create PostgreSQL database and user
    sudo -u postgres psql << EOF
CREATE DATABASE stock_db;
CREATE USER stock_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE stock_db TO stock_user;
\q
EOF
    
    # Set up application database
    cd $APP_DIR
    source venv/bin/activate
    
    # Set environment variables for database setup
    export FLASK_ENV=production
    export DATABASE_URL="postgresql://stock_user:secure_password_here@localhost/stock_db"
    export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
    
    # Initialize database
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    
    print_status "Database setup completed"
}

# Create configuration files
create_config_files() {
    print_status "Creating configuration files..."
    
    cd $APP_DIR
    
    # Create .env file
    cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
DATABASE_URL=postgresql://stock_user:secure_password_here@localhost/stock_db
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
RATELIMIT_STORAGE_URL=redis://localhost:6379
LOG_LEVEL=WARNING
BCRYPT_LOG_ROUNDS=13
EOF
    
    # Create Gunicorn configuration
    cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True

accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

proc_name = "stock_manager_app"

limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
EOF
    
    # Create logs directory
    mkdir -p logs
    sudo chown $SERVICE_USER:$SERVICE_USER logs
    
    print_status "Configuration files created"
}

# Setup systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    sudo tee /etc/systemd/system/stock-app.service > /dev/null << EOF
[Unit]
Description=Stock Manager App
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py run:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable stock-app
    
    print_status "Systemd service created"
}

# Setup Nginx
setup_nginx() {
    print_status "Setting up Nginx..."
    
    sudo tee /etc/nginx/sites-available/stock-app > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    access_log /var/log/nginx/stock_app_access.log;
    error_log /var/log/nginx/stock_app_error.log;
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/stock-app /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    
    print_status "Nginx configured"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    sudo systemctl start postgresql
    sudo systemctl start redis-server
    sudo systemctl start stock-app
    sudo systemctl start nginx
    
    print_status "Services started"
}

# Verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Wait for service to start
    sleep 5
    
    # Check service status
    if sudo systemctl is-active --quiet stock-app; then
        print_status "Stock App service is running"
    else
        print_error "Stock App service failed to start"
        sudo systemctl status stock-app
        exit 1
    fi
    
    # Check health endpoint
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_status "Health check passed"
    else
        print_warning "Health check failed - check logs"
    fi
    
    print_status "Deployment verification completed"
}

# Main deployment function
main() {
    print_status "Starting Stock Manager App deployment..."
    
    check_requirements
    install_system_deps
    setup_app_directory
    setup_application
    setup_database
    create_config_files
    setup_systemd_service
    setup_nginx
    start_services
    verify_deployment
    
    print_status "🎉 Deployment completed successfully!"
    print_status "Application is available at: http://your-domain.com"
    print_status "Health check: http://your-domain.com/health"
    print_warning "Remember to:"
    print_warning "1. Update DNS records to point to this server"
    print_warning "2. Configure SSL certificate (Let's Encrypt recommended)"
    print_warning "3. Update database credentials in .env file"
    print_warning "4. Configure firewall rules"
}

# Run main function
main "$@"
