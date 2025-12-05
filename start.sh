#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Odoo 19 Fleet Vessels - Quick Start${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"
echo ""

# Check if port 8069 is available
if lsof -Pi :8069 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠ Warning: Port 8069 is already in use${NC}"
    echo "You may need to stop the service using this port or change the port in docker-compose.yml"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Docker Compose
echo -e "${BLUE}Starting Docker containers...${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Containers started successfully!${NC}"
    echo ""
    echo -e "${BLUE}Waiting for Odoo to initialize...${NC}"
    echo "This may take a few minutes on first run..."
    echo ""
    
    # Wait for Odoo to be ready
    sleep 10
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Odoo is starting up!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Access Odoo at: ${BLUE}http://localhost:8069${NC}"
    echo ""
    echo -e "Default credentials:"
    echo -e "  Email:    ${YELLOW}admin${NC}"
    echo -e "  Password: ${YELLOW}admin${NC}"
    echo ""
    echo -e "To view logs: ${BLUE}docker-compose logs -f odoo${NC}"
    echo -e "To stop:      ${BLUE}docker-compose down${NC}"
    echo ""
    echo -e "${YELLOW}Note: First startup may take 2-3 minutes to initialize the database${NC}"
    echo ""
else
    echo -e "${RED}❌ Failed to start containers${NC}"
    echo "Check the error messages above"
    exit 1
fi
