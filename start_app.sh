#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Waybill Extractor...${NC}"

# Start backend server
echo -e "${YELLOW}Starting backend server...${NC}"
cd backend
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!
echo -e "${GREEN}Backend server started with PID: ${BACKEND_PID}${NC}"

# Start frontend server
echo -e "${YELLOW}Starting frontend server...${NC}"
cd ../frontend
npm start &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend server started with PID: ${FRONTEND_PID}${NC}"

echo -e "${GREEN}Application started!${NC}"
echo -e "${YELLOW}Access the application at http://localhost:3000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Handle cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; echo -e '${RED}Servers stopped${NC}'" EXIT

# Wait for user to press Ctrl+C
wait 