#!/bin/bash

# RAG Mini-Platform Startup Script
# This script helps you start the entire RAG platform with Docker

set -e

echo "🚀 Starting RAG Mini-Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if .env file exists
check_env() {
    print_status "Checking environment configuration..."
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Please edit .env file and add your GROQ_API_KEY"
            print_warning "Then run this script again."
            exit 1
        else
            print_error "env.example not found. Please create .env file manually."
            exit 1
        fi
    fi
    
    # Check if GROQ_API_KEY is set
    if ! grep -q "GROQ_API_KEY=" .env || grep -q "GROQ_API_KEY=your_actual_api_key_here" .env; then
        print_warning "GROQ_API_KEY not set in .env file"
        print_warning "Please edit .env file and add your actual Groq API key"
        exit 1
    fi
    
    print_success "Environment configuration is valid"
}

# Check if ports are available
check_ports() {
    print_status "Checking port availability..."
    
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 3000 is already in use"
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 8000 is already in use"
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Ports are available"
}

# Start the application
start_app() {
    print_status "Starting RAG Mini-Platform..."
    
    # Build and start services
    docker-compose up --build -d
    
    print_success "Services started successfully!"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend
    print_status "Waiting for backend service..."
    timeout=60
    counter=0
    while [ $counter -lt $timeout ]; do
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            print_success "Backend is ready!"
            break
        fi
        sleep 2
        counter=$((counter + 2))
        echo -n "."
    done
    
    if [ $counter -eq $timeout ]; then
        print_error "Backend failed to start within $timeout seconds"
        print_status "Checking logs..."
        docker-compose logs backend
        exit 1
    fi
    
    # Wait for frontend
    print_status "Waiting for frontend service..."
    counter=0
    while [ $counter -lt $timeout ]; do
        if curl -s http://localhost:3000/health > /dev/null 2>&1; then
            print_success "Frontend is ready!"
            break
        fi
        sleep 2
        counter=$((counter + 2))
        echo -n "."
    done
    
    if [ $counter -eq $timeout ]; then
        print_error "Frontend failed to start within $timeout seconds"
        print_status "Checking logs..."
        docker-compose logs frontend
        exit 1
    fi
    
    echo
}

# Show status
show_status() {
    print_status "Checking service status..."
    docker-compose ps
}

# Show access information
show_access_info() {
    echo
    print_success "🎉 RAG Mini-Platform is now running!"
    echo
    echo "📱 Access your application:"
    echo "   Frontend UI:     http://localhost:3000"
    echo "   Backend API:     http://localhost:8000"
    echo "   API Docs:        http://localhost:8000/docs"
    echo "   Health Check:    http://localhost:8000/"
    echo
    echo "🔧 Management commands:"
    echo "   View logs:       docker-compose logs -f"
    echo "   Stop services:   docker-compose down"
    echo "   Restart:         docker-compose restart"
    echo "   Status:          docker-compose ps"
    echo
}

# Main execution
main() {
    echo "=========================================="
    echo "   RAG Mini-Platform Startup Script"
    echo "=========================================="
    echo
    
    check_docker
    check_env
    check_ports
    start_app
    wait_for_services
    show_status
    show_access_info
}

# Handle script arguments
case "${1:-}" in
    "stop")
        print_status "Stopping RAG Mini-Platform..."
        docker-compose down
        print_success "Services stopped"
        ;;
    "restart")
        print_status "Restarting RAG Mini-Platform..."
        docker-compose down
        docker-compose up --build -d
        print_success "Services restarted"
        ;;
    "logs")
        print_status "Showing logs..."
        docker-compose logs -f
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  (no args)  Start the application"
        echo "  stop       Stop all services"
        echo "  restart    Restart all services"
        echo "  logs       Show application logs"
        echo "  status     Show service status"
        echo "  help       Show this help message"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
