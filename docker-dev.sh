#!/bin/bash

# Docker development utility script for Netrun Systems
# Usage: ./docker-dev.sh [command]

set -e

CONTAINER_NAME="netrun-app"
IMAGE_NAME="netrun-app"

case "${1:-help}" in
    "build")
        echo "🔨 Building Docker image..."
        docker build -t $IMAGE_NAME .
        echo "✅ Build complete"
        ;;
    
    "start")
        echo "🚀 Starting application with Docker Compose..."
        docker-compose up -d
        echo "✅ Application started at http://localhost:8000"
        ;;
    
    "stop")
        echo "🛑 Stopping application..."
        docker-compose down
        echo "✅ Application stopped"
        ;;
    
    "restart")
        echo "🔄 Restarting application..."
        docker-compose down
        docker-compose up -d
        echo "✅ Application restarted at http://localhost:8000"
        ;;
    
    "logs")
        echo "📋 Showing application logs..."
        docker-compose logs -f
        ;;
    
    "shell")
        echo "🐚 Opening shell in container..."
        docker-compose exec netrun-app bash
        ;;
    
    "test")
        echo "🧪 Running application tests..."
        echo "Testing health endpoint..."
        sleep 3
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Health check passed"
        else
            echo "❌ Health check failed"
            exit 1
        fi
        
        echo "Testing main page..."
        if curl -f http://localhost:8000/ > /dev/null 2>&1; then
            echo "✅ Main page accessible"
        else
            echo "❌ Main page failed"
            exit 1
        fi
        
        echo "Testing contact page..."
        if curl -f http://localhost:8000/contact > /dev/null 2>&1; then
            echo "✅ Contact page accessible"
        else
            echo "❌ Contact page failed"
            exit 1
        fi
        
        echo "✅ All tests passed!"
        ;;
    
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down
        docker rmi $IMAGE_NAME 2>/dev/null || true
        docker system prune -f
        echo "✅ Cleanup complete"
        ;;
    
    "debug")
        echo "🔍 Debug information:"
        echo "Container status:"
        docker-compose ps
        echo ""
        echo "Application routes:"
        docker-compose exec netrun-app python -c "from app import app; print([str(rule) for rule in app.url_map.iter_rules()])" 2>/dev/null || echo "Container not running"
        echo ""
        echo "Recent logs:"
        docker-compose logs --tail=20 netrun-app 2>/dev/null || echo "No logs available"
        ;;
    
    "deploy-prep")
        echo "📦 Preparing for Azure deployment..."
        echo "Building production image..."
        docker build -t $IMAGE_NAME .
        
        echo "Testing production build..."
        docker run -d --name ${CONTAINER_NAME}-test -p 8001:8000 $IMAGE_NAME
        sleep 5
        
        if curl -f http://localhost:8001/health > /dev/null 2>&1; then
            echo "✅ Production build test passed"
            docker stop ${CONTAINER_NAME}-test
            docker rm ${CONTAINER_NAME}-test
        else
            echo "❌ Production build test failed"
            docker stop ${CONTAINER_NAME}-test 2>/dev/null || true
            docker rm ${CONTAINER_NAME}-test 2>/dev/null || true
            exit 1
        fi
        
        echo "✅ Ready for Azure deployment"
        echo "Updated requirements.txt and fixed Flask/Werkzeug compatibility"
        ;;
    
    "help"|*)
        echo "🐳 Docker Development Utility for Netrun Systems"
        echo ""
        echo "Usage: ./docker-dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  build        Build the Docker image"
        echo "  start        Start the application with docker-compose"
        echo "  stop         Stop the application"
        echo "  restart      Restart the application"
        echo "  logs         Show application logs"
        echo "  shell        Open a shell in the container"
        echo "  test         Run basic functionality tests"
        echo "  clean        Clean up Docker resources"
        echo "  debug        Show debug information"
        echo "  deploy-prep  Prepare and test for Azure deployment"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./docker-dev.sh start"
        echo "  ./docker-dev.sh logs"
        echo "  ./docker-dev.sh test"
        ;;
esac