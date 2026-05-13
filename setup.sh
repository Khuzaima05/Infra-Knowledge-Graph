#!/bin/bash
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Infra Knowledge Graph - Setup Script                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker found${NC}"
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}📋 Creating .env file from .env.example${NC}"
    cp .env.example .env
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p backend/cloned_repos
mkdir -p logs

# Build containers
echo -e "${YELLOW}🔨 Building Docker containers...${NC}"
docker-compose build --progress plain

# Start containers
echo -e "${YELLOW}🚀 Starting containers...${NC}"
docker-compose up -d

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 5

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Failed to start containers${NC}"
    docker-compose logs
    exit 1
fi

echo -e "${GREEN}✅ Containers started${NC}"

# Initialize database
echo -e "${YELLOW}📊 Initializing database...${NC}"
docker-compose exec -T backend python scripts/init_db.py

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅ Setup Complete!                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📚 Access the Application:${NC}"
echo -e "  ${YELLOW}Frontend:${NC}     ${BLUE}http://localhost:3000${NC}"
echo -e "  ${YELLOW}Backend API:${NC}  ${BLUE}http://localhost:8000${NC}"
echo -e "  ${YELLOW}API Docs:${NC}     ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo -e "  ${YELLOW}View logs:${NC}         ${BLUE}docker-compose logs -f${NC}"
echo -e "  ${YELLOW}Stop services:${NC}     ${BLUE}docker-compose down${NC}"
echo -e "  ${YELLOW}Restart services:${NC}  ${BLUE}docker-compose restart${NC}"
echo -e "  ${YELLOW}Clean rebuild:${NC}     ${BLUE}./cleanup.sh && ./setup.sh${NC}"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo -e "  README.md      - Main documentation"
echo -e "  DEVELOPMENT.md - Development guide"
echo -e "  API.md         - API documentation"
echo ""
