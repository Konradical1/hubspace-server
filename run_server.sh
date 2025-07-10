#!/bin/bash

# Hubspace Light Control API Server Launcher
# This script installs dependencies, starts the FastAPI server, and creates a public tunnel

set -e  # Exit on any error

echo "🚀 Hubspace Light Control API Server Launcher"
echo "=============================================="

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

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Detected macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew is not installed. Please install it first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install cloudflared via Homebrew
    print_status "Installing cloudflared via Homebrew..."
    brew install cloudflare/cloudflare/cloudflared
    print_success "cloudflared installed"
else
    print_warning "Not on macOS. You may need to install cloudflared manually:"
    echo "  Visit: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not available. Please install Python with pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp env_template.txt .env
    print_status "Please edit .env file with your credentials:"
    echo "  nano .env"
    echo ""
    echo "Required fields:"
    echo "  HUBSPACE_EMAIL=your-email@example.com"
    echo "  HUBSPACE_PASSWORD=your-password"
    echo "  SECRET_TOKEN=your-secret-token"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Load environment variables
if [ -f ".env" ]; then
    print_status "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
    print_success "Environment variables loaded"
else
    print_error ".env file not found!"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    print_status "Shutting down..."
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    if [ ! -z "$TUNNEL_PID" ]; then
        kill $TUNNEL_PID 2>/dev/null || true
    fi
    print_success "Cleanup complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the FastAPI server in the background
print_status "Starting FastAPI server..."
python hubspace_server.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    print_error "Server failed to start. Check the logs above."
    exit 1
fi

print_success "FastAPI server started on http://localhost:8000"

# Start Cloudflare tunnel
print_status "Starting Cloudflare tunnel..."
cloudflared tunnel --url http://localhost:8000 &
TUNNEL_PID=$!

# Wait for tunnel to establish
sleep 5

# Get tunnel URL
TUNNEL_URL=$(cloudflared tunnel --url http://localhost:8000 --no-autoupdate 2>&1 | grep -o 'https://[^[:space:]]*' | head -1)

if [ -z "$TUNNEL_URL" ]; then
    print_warning "Could not get tunnel URL automatically. You can access the server locally at:"
    echo "  http://localhost:8000"
    echo ""
    echo "To get a public URL, run:"
    echo "  cloudflared tunnel --url http://localhost:8000"
else
    print_success "Public tunnel URL: $TUNNEL_URL"
    echo ""
    echo "🌐 Your API is now available at:"
    echo "  $TUNNEL_URL"
    echo ""
    echo "📋 API Endpoints:"
    echo "  GET  $TUNNEL_URL/           - API information"
    echo "  GET  $TUNNEL_URL/lights      - List all lights"
    echo "  POST $TUNNEL_URL/control     - Control lights"
    echo "  GET  $TUNNEL_URL/health      - Health check"
    echo ""
    echo "🔑 Authorization:"
    echo "  Header: Authorization: Bearer $SECRET_TOKEN"
    echo ""
    echo "📝 Example curl commands:"
    echo "  # Turn all lights ON"
    echo "  curl -X POST $TUNNEL_URL/control \\"
    echo "    -H \"Authorization: Bearer $SECRET_TOKEN\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"action\": \"ON\"}'"
    echo ""
    echo "  # Turn specific light OFF"
    echo "  curl -X POST $TUNNEL_URL/control \\"
    echo "    -H \"Authorization: Bearer $SECRET_TOKEN\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"name\": \"KonradLamp\", \"action\": \"OFF\"}'"
    echo ""
    echo "  # Set brightness and color"
    echo "  curl -X POST $TUNNEL_URL/control \\"
    echo "    -H \"Authorization: Bearer $SECRET_TOKEN\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"brightness\": 75, \"color\": \"#FF0000\"}'"
    echo ""
    echo "🔄 Server is running. Press Ctrl+C to stop."
fi

# Keep script running
wait 