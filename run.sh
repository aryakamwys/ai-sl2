#!/bin/bash

# AI Bojongsantozzz API Runner Script

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  AI Bojongsantozzz API Runner  ${NC}"
echo -e "${BLUE}=================================${NC}\n"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env file. Please update it with your credentials.${NC}"
    else
        echo -e "${RED}Error: .env.example not found!${NC}"
        exit 1
    fi
fi

# Function to run with Docker
run_docker() {
    echo -e "${BLUE}Starting with Docker...${NC}\n"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed!${NC}"
        exit 1
    fi
    
    docker-compose up --build
}

# Function to run locally
run_local() {
    echo -e "${BLUE}Starting locally...${NC}\n"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install -r requirements.txt
    
    # Run the application
    echo -e "${GREEN}Starting FastAPI server...${NC}\n"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to stop Docker containers
stop_docker() {
    echo -e "${BLUE}Stopping Docker containers...${NC}"
    docker-compose down
    echo -e "${GREEN}Stopped successfully!${NC}"
}

# Parse command line arguments
case "$1" in
    docker)
        run_docker
        ;;
    local)
        run_local
        ;;
    stop)
        stop_docker
        ;;
    *)
        echo "Usage: $0 {docker|local|stop}"
        echo ""
        echo "  docker - Run using Docker Compose"
        echo "  local  - Run locally with virtual environment"
        echo "  stop   - Stop Docker containers"
        echo ""
        exit 1
        ;;
esac

