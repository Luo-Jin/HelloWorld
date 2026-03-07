#!/bin/bash

# Flask App Server Control Script
# Usage: ./server.sh [start|stop|restart|status]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PORT=8080

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to start the server
start_server() {
    echo -e "${YELLOW}Starting Flask server on port $PORT...${NC}"
    
    # Check if server is already running
    if ps aux | grep -v grep | grep "flask --app app" > /dev/null; then
        echo -e "${RED}Server is already running!${NC}"
        echo "Use './server.sh restart' to restart the server"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    set -a && [ -f .env ] && source .env || true && set +a && .venv/bin/flask --app app --debug run --port=$PORT &
    
    # Give it a moment to start
    sleep 2
    
    # Verify it started
    if curl -s http://localhost:$PORT/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server started successfully on http://localhost:$PORT${NC}"
        return 0
    else
        echo -e "${RED}✗ Server failed to start${NC}"
        return 1
    fi
}

# Function to stop the server
stop_server() {
    echo -e "${YELLOW}Stopping Flask server...${NC}"
    
    # Kill Flask processes
    pkill -f "flask --app app" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        sleep 1
        echo -e "${GREEN}✓ Server stopped${NC}"
        return 0
    else
        echo -e "${RED}✗ No server process found${NC}"
        return 1
    fi
}

# Function to check server status
status_server() {
    if ps aux | grep -v grep | grep "flask --app app" > /dev/null; then
        PID=$(pgrep -f "flask --app app" | head -1)
        echo -e "${GREEN}✓ Server is running (PID: $PID) on port $PORT${NC}"
        echo -e "  URL: ${GREEN}http://localhost:$PORT${NC}"
        return 0
    else
        echo -e "${RED}✗ Server is not running${NC}"
        return 1
    fi
}

# Main script logic
case "${1:-status}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        echo -e "${YELLOW}Restarting Flask server...${NC}"
        stop_server
        sleep 1
        start_server
        ;;
    status)
        status_server
        ;;
    *)
        echo "Flask App Server Control Script"
        echo ""
        echo "Usage: $0 [start|stop|restart|status]"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Flask server on port $PORT"
        echo "  stop    - Stop the Flask server"
        echo "  restart - Restart the Flask server"
        echo "  status  - Check if server is running"
        echo ""
        exit 1
        ;;
esac
