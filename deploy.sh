#!/bin/bash

# Laniakea Intelligent Protocol - Deployment Script
# Self-Developing Blockchain with Internal Developer Intelligence

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="laniakea-intelligent-protocol"
VERSION="2.0.0"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} ${timestamp} - $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} ${timestamp} - $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${timestamp} - $message"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} ${timestamp} - $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - $message"
            ;;
        *)
            echo -e "${CYAN}[LOG]${NC} ${timestamp} - $message"
            ;;
    esac
}

# Print banner
print_banner() {
    echo -e "${PURPLE}"
    echo "========================================================================"
    echo "🧠 LANIAKEA INTELLIGENT PROTOCOL - DEPLOYMENT SCRIPT"
    echo "========================================================================"
    echo "🔬 Self-Developing Blockchain with Internal Developer Intelligence"
    echo "🧬 Evolution Engine: ACTIVE"
    echo "🔒 Intelligent Security: ENABLED"
    echo "⚡ Performance Optimization: ACTIVE"
    echo "🌌 Cosmic Intelligence: ONLINE"
    echo "========================================================================"
    echo -e "${NC}"
}

# Check system requirements
check_requirements() {
    log "INFO" "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log "ERROR" "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log "ERROR" "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check available memory
    MEMORY_AVAILABLE=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$MEMORY_AVAILABLE" -lt 2048 ]; then
        log "WARN" "Available memory is less than 2GB. Performance may be affected."
    fi
    
    # Check available disk space
    DISK_AVAILABLE=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$DISK_AVAILABLE" -lt 10 ]; then
        log "WARN" "Available disk space is less than 10GB. Deployment may fail."
    fi
    
    log "SUCCESS" "System requirements check completed"
}

# Setup environment
setup_environment() {
    log "INFO" "Setting up environment..."
    
    # Create necessary directories
    mkdir -p logs data blockchain_data models backups
    mkdir -p init-scripts monitoring/grafana/provisioning nginx/ssl
    
    # Set permissions
    chmod 755 logs data blockchain_data models backups
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log "INFO" "Creating .env file with default configuration..."
        cat > .env << EOF
# Laniakea Intelligent Protocol Environment Configuration
NODE_ENV=production
NODE_ID=laniakea-intelligent-node
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://laniakea_user:laniakea_password@postgres:5432/laniakea_intelligent
REDIS_URL=redis://redis:6379/0

# Security Configuration
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# AI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Monitoring Configuration
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *

# Evolution Configuration
EVOLUTION_ENABLED=true
EVOLUTION_RATE=120
LEARNING_RATE=0.01

# Performance Configuration
MAX_CPU_USAGE=80
MAX_MEMORY_USAGE=80
MAX_DISK_USAGE=90

# Feature Flags
QUANTUM_COMPUTING=false
METVERSE_INTEGRATION=false
AI_AUTONOMOUS_AGENTS=true
SELF_DEVELOPING_CODE=true
EOF
        log "SUCCESS" ".env file created with secure defaults"
    else
        log "INFO" ".env file already exists"
    fi
    
    # Create init scripts for PostgreSQL
    if [ ! -f init-scripts/init.sql ]; then
        log "INFO" "Creating PostgreSQL initialization script..."
        cat > init-scripts/init.sql << EOF
-- Laniakea Intelligent Protocol Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database schema
CREATE SCHEMA IF NOT EXISTS laniakea_intelligent;
SET search_path TO laniakea_intelligent, public;

-- Create tables for intelligent data
CREATE TABLE IF NOT EXISTS evolution_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evolution_type VARCHAR(100),
    patterns_updated INTEGER,
    performance_improvement FLOAT,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS intelligence_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_id VARCHAR(255) UNIQUE NOT NULL,
    pattern_type VARCHAR(100),
    evolution_factor FLOAT,
    adaptation_rate FLOAT,
    performance_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_usage FLOAT,
    network_io FLOAT,
    evolution_cycles INTEGER,
    system_status JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_evolution_history_timestamp ON evolution_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_intelligence_patterns_type ON intelligence_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA laniakea_intelligent TO laniakea_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA laniakea_intelligent TO laniakea_user;
EOF
        log "SUCCESS" "PostgreSQL initialization script created"
    fi
    
    # Create Nginx configuration
    if [ ! -f nginx/nginx.conf ]; then
        log "INFO" "Creating Nginx configuration..."
        cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream laniakea_backend {
        server laniakea-intelligent:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://laniakea_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /health {
            proxy_pass http://laniakea_backend/health;
            access_log off;
        }
    }
}
EOF
        log "SUCCESS" "Nginx configuration created"
    fi
    
    log "SUCCESS" "Environment setup completed"
}

# Build Docker images
build_images() {
    log "INFO" "Building Docker images..."
    
    # Build main application image
    log "INFO" "Building Laniakea Intelligent Protocol image..."
    docker build -f Dockerfile.intelligent -t laniakea-intelligent:$VERSION .
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Docker image built successfully"
    else
        log "ERROR" "Failed to build Docker image"
        exit 1
    fi
}

# Deploy services
deploy_services() {
    log "INFO" "Deploying services..."
    
    # Stop existing services if running
    log "INFO" "Stopping existing services..."
    docker-compose -f docker-compose.intelligent.yml down
    
    # Start services
    log "INFO" "Starting services..."
    docker-compose -f docker-compose.intelligent.yml up -d
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Services deployed successfully"
    else
        log "ERROR" "Failed to deploy services"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    log "INFO" "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    log "INFO" "Waiting for PostgreSQL..."
    timeout 60 bash -c 'until docker-compose -f docker-compose.intelligent.yml exec -T postgres pg_isready -U laniakea_user -d laniakea_intelligent; do sleep 2; done'
    
    # Wait for Redis
    log "INFO" "Waiting for Redis..."
    timeout 60 bash -c 'until docker-compose -f docker-compose.intelligent.yml exec -T redis redis-cli ping; do sleep 2; done'
    
    # Wait for main application
    log "INFO" "Waiting for Laniakea Intelligent Protocol..."
    timeout 120 bash -c 'until curl -f http://localhost:8000/health; do sleep 5; done'
    
    log "SUCCESS" "All services are ready"
}

# Run health checks
run_health_checks() {
    log "INFO" "Running health checks..."
    
    # Check main application
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "SUCCESS" "Laniakea Intelligent Protocol is healthy"
    else
        log "ERROR" "Laniakea Intelligent Protocol health check failed"
        return 1
    fi
    
    # Check database connection
    if docker-compose -f docker-compose.intelligent.yml exec -T postgres pg_isready -U laniakea_user -d laniakea_intelligent > /dev/null 2>&1; then
        log "SUCCESS" "PostgreSQL is healthy"
    else
        log "ERROR" "PostgreSQL health check failed"
        return 1
    fi
    
    # Check Redis connection
    if docker-compose -f docker-compose.intelligent.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log "SUCCESS" "Redis is healthy"
    else
        log "ERROR" "Redis health check failed"
        return 1
    fi
    
    log "SUCCESS" "All health checks passed"
}

# Show service status
show_status() {
    log "INFO" "Service Status:"
    docker-compose -f docker-compose.intelligent.yml ps
    
    echo ""
    log "INFO" "Service URLs:"
    echo -e "${CYAN}• Laniakea Intelligent Protocol:${NC} http://localhost:8000"
    echo -e "${CYAN}• Grafana Dashboard:${NC} http://localhost:3000 (admin/laniakea_admin)"
    echo -e "${CYAN}• Prometheus:${NC} http://localhost:9090"
    echo -e "${CYAN}• Jaeger Tracing:${NC} http://localhost:16686"
    echo -e "${CYAN}• Redis Commander:${NC} http://localhost:8081"
    echo -e "${CYAN}• pgAdmin:${NC} http://localhost:8080 (admin@laniakea.local/pgadmin_password)"
}

# Cleanup function
cleanup() {
    log "INFO" "Cleaning up temporary files..."
    # Add cleanup logic here if needed
}

# Main deployment function
deploy() {
    print_banner
    check_requirements
    setup_environment
    build_images
    deploy_services
    wait_for_services
    run_health_checks
    show_status
}

# Update function
update() {
    log "INFO" "Updating Laniakea Intelligent Protocol..."
    
    # Pull latest changes
    git pull origin main
    
    # Rebuild and redeploy
    build_images
    deploy_services
    wait_for_services
    run_health_checks
    
    log "SUCCESS" "Update completed successfully"
}

# Stop function
stop() {
    log "INFO" "Stopping Laniakea Intelligent Protocol..."
    docker-compose -f docker-compose.intelligent.yml down
    log "SUCCESS" "Services stopped"
}

# Restart function
restart() {
    log "INFO" "Restarting Laniakea Intelligent Protocol..."
    docker-compose -f docker-compose.intelligent.yml restart
    wait_for_services
    run_health_checks
    log "SUCCESS" "Services restarted"
}

# Logs function
show_logs() {
    docker-compose -f docker-compose.intelligent.yml logs -f --tail=100
}

# Help function
show_help() {
    echo "Laniakea Intelligent Protocol Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy the complete intelligent protocol"
    echo "  update     Update the existing deployment"
    echo "  stop       Stop all services"
    echo "  restart    Restart all services"
    echo "  logs       Show service logs"
    echo "  status     Show service status"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 update"
    echo "  $0 logs"
}

# Main script execution
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "update")
        update
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        log "ERROR" "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

# Cleanup on exit
trap cleanup EXIT

log "SUCCESS" "Script execution completed successfully!"