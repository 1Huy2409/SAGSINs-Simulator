#!/bin/bash

echo "======================================"
echo "🚀 SAGSINs System Startup"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Start Docker containers
echo "📦 Starting Docker containers..."
cd docker
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker containers started${NC}"
else
    echo -e "${RED}❌ Failed to start Docker containers${NC}"
    exit 1
fi

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if sagsins-server is running
if docker ps | grep -q sagsins-server; then
    echo -e "${GREEN}✅ SAGSINs Server is running${NC}"
else
    echo -e "${RED}❌ SAGSINs Server failed to start${NC}"
    echo "Check logs with: docker logs sagsins-server"
fi

cd ..

echo ""
echo "======================================"
echo "✅ System is ready!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Start Backend:"
echo "   cd wep-app/backend && npm start"
echo ""
echo "2. Start Frontend (in another terminal):"
echo "   cd wep-app/frontend && npm run dev -- --host"
echo ""
echo "3. Open browser:"
echo "   http://localhost:5173"
echo ""
echo "======================================"
echo ""
echo "📊 Monitor Docker logs:"
echo "   docker logs sagsins-server -f"
echo ""
echo "🛑 Stop system:"
echo "   cd docker && docker-compose down"
echo ""
