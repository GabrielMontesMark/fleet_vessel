#!/bin/bash

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping Odoo Fleet Vessels environment...${NC}"
echo ""

docker-compose down

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${YELLOW}✓ Containers stopped${NC}"
    echo ""
    read -p "Do you want to remove all data (volumes)? This will delete the database! (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        echo -e "${YELLOW}✓ All data removed${NC}"
    fi
else
    echo -e "${RED}❌ Failed to stop containers${NC}"
    exit 1
fi
