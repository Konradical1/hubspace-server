# Hubspace Light Control API Server

A FastAPI server for controlling Hubspace smart lights via HTTP API with support for power, brightness, and color control.

## Features

- 🔐 **Secure Authentication** - Token-based API access
- 💡 **Power Control** - Turn lights ON/OFF
- 🌟 **Brightness Control** - Adjust brightness (0-100%)
- 🎨 **Color Control** - Set RGB colors via hex values
- ⚡ **Threaded Operations** - Control multiple lights simultaneously
- 🌐 **Public Access** - Cloudflare tunnel for external access
- 📊 **Real-time Status** - Get current state of all lights

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install cloudflared (macOS)
brew install cloudflare/cloudflare/cloudflared

# Or download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

### 2. Configure Environment

Copy the environment template and edit with your credentials:

```bash
cp env_template.txt .env
nano .env
```

Required fields:
```env
HUBSPACE_EMAIL=your-email@example.com
HUBSPACE_PASSWORD=your-password
SECRET_TOKEN=your-secret-token
```

### 3. Run the Server

**Option A: Use the launcher script (recommended)**
```bash
chmod +x run_server.sh
./run_server.sh
```

**Option B: Manual start**
```bash
python hubspace_server.py
```

The server will be available at:
- **Local**: http://localhost:8000
- **Public**: https://your-tunnel-url.cloudflare.com

## API Endpoints

### Authentication

All API calls require the `Authorization` header:
```
Authorization: Bearer SECRET123
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/lights` | List all available lights |
| `POST` | `/control` | Control lights |
| `GET` | `/health` | Health check |

### Control Lights

**POST** `/control`

Request body (all fields optional):
```json
{
  "name": "KonradLamp",        // Optional: specific light name
  "action": "ON",              // Optional: "ON" or "OFF"
  "brightness": 75,            // Optional: 0-100
  "color": "#FF0000"           // Optional: hex color
}
```

**Examples:**

Turn all lights ON:
```bash
curl -X POST https://your-api-url/control \
  -H "Authorization: Bearer SECRET123" \
  -H "Content-Type: application/json" \
  -d '{"action": "ON"}'
```

Turn specific light OFF:
```bash
curl -X POST https://your-api-url/control \
  -H "Authorization: Bearer SECRET123" \
  -H "Content-Type: application/json" \
  -d '{"name": "KonradLamp", "action": "OFF"}'
```

Set brightness and color:
```bash
curl -X POST https://your-api-url/control \
  -H "Authorization: Bearer SECRET123" \
  -H "Content-Type: application/json" \
  -d '{"brightness": 75, "color": "#FF0000"}'
```

## Response Format

```json
{
  "success": true,
  "message": "Controlled 4/4 devices successfully",
  "results": [
    {
      "name": "KonradLamp",
      "device_id": "8bcb78ee4cd33742",
      "success": true,
      "message": "Successfully controlled KonradLamp",
      "power_state": "ON",
      "brightness": 75,
      "color": "#FF0000"
    }
  ],
  "timestamp": 1640995200.123
}
```

## Integration with n8n

### HTTP Request Node Configuration

**URL**: `https://your-api-url/control`

**Headers**:
```
Authorization: Bearer SECRET123
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "action": "ON",
  "brightness": 100,
  "color": "#00FF00"
}
```

### Example Workflows

1. **Motion Detection**: Turn on lights when motion detected
2. **Time-based**: Schedule lights to turn on/off
3. **Weather**: Adjust brightness based on weather conditions
4. **Calendar**: Turn on lights for meetings
5. **Voice Commands**: Control lights via voice assistants

## File Structure

```
Hubspace/
├── hubspace_server.py      # Main FastAPI server
├── run_server.sh           # Launcher script
├── requirements.txt        # Python dependencies
├── env_template.txt        # Environment template
├── .env                   # Environment variables (create from template)
└── README_API.md          # This file
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your Hubspace credentials in `.env`
   - Verify your account is active

2. **No Lights Found**
   - Ensure you have Hubspace devices set up
   - Check device connectivity in Hubspace app

3. **Server Won't Start**
   - Check if port 8000 is available
   - Verify all dependencies are installed

4. **Tunnel Issues**
   - Install cloudflared: `brew install cloudflare/cloudflare/cloudflared`
   - Check internet connection

### Debug Mode

Enable detailed logging by modifying `hubspace_server.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Change the default token** in `.env`
2. **Use HTTPS** in production
3. **Limit access** to your API
4. **Monitor usage** and logs
5. **Keep credentials secure**

## Development

### Local Development

```bash
# Install in development mode
pip install -e .

# Run with auto-reload
uvicorn hubspace_server:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test lights endpoint
curl http://localhost:8000/lights

# Test control endpoint
curl -X POST http://localhost:8000/control \
  -H "Authorization: Bearer SECRET123" \
  -H "Content-Type: application/json" \
  -d '{"action": "ON"}'
```

## License

This project is for educational purposes. Use at your own risk and respect Hubspace's terms of service. 