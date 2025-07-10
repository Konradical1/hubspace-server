#!/usr/bin/env python3
"""
Hubspace Smart Light Control API Server
FastAPI server for controlling Hubspace smart lights via HTTP API

Installation:
    pip install -r requirements.txt

Usage:
    python hubspace_server.py
    or
    uvicorn hubspace_server:app --host 0.0.0.0 --port 8000
"""

import os
import asyncio
import threading
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from hubspace import Hubspace

# Load environment variables
load_dotenv()

# Configuration
HUBSPACE_EMAIL = os.getenv("HUBSPACE_EMAIL", "fischerpaxton@gmail.com")
HUBSPACE_PASSWORD = os.getenv("HUBSPACE_PASSWORD", "EagleAva4!")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "SECRET123")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Initialize FastAPI app
app = FastAPI(
    title="Hubspace Light Control API",
    description="API for controlling Hubspace smart lights",
    version="1.0.0"
)

# Global variables
hubspace_client = None
light_devices = []

# Pydantic models
class LightControlRequest(BaseModel):
    name: Optional[str] = Field(None, description="Name of the light to control (if omitted, affects all lights)")
    action: Optional[str] = Field(None, description="Power action: 'ON' or 'OFF'")
    brightness: Optional[int] = Field(None, ge=0, le=100, description="Brightness level 0-100")
    color: Optional[str] = Field(None, description="Color in hex format (e.g., '#FF0000')")

class DeviceResult(BaseModel):
    name: str
    device_id: str
    success: bool
    message: str
    power_state: Optional[str] = None
    brightness: Optional[int] = None
    color: Optional[str] = None

class ControlResponse(BaseModel):
    success: bool
    message: str
    results: List[DeviceResult]
    timestamp: float

# Authentication dependency
async def verify_token(authorization: str = Header(None)):
    """Verify the authorization token"""
    if not authorization or authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
    return True

# Hubspace client management
def initialize_hubspace():
    """Initialize Hubspace client and fetch devices"""
    global hubspace_client, light_devices
    
    try:
        print("🔐 Initializing Hubspace client...")
        print(f"📧 Using email: {HUBSPACE_EMAIL}")
        print(f"🔑 Password length: {len(HUBSPACE_PASSWORD) if HUBSPACE_PASSWORD else 0}")
        
        hubspace_client = Hubspace(HUBSPACE_EMAIL, HUBSPACE_PASSWORD)
        
        print("📱 Fetching devices...")
        all_devices = hubspace_client.getDevices()
        print(f"📦 Total devices found: {len(all_devices)}")
        
        # Filter for light devices
        light_devices = []
        for device in all_devices:
            name = device.getName()
            dev_type = device.getDeviceClass()
            print(f"🔍 Device: {name} (Type: {dev_type})")
            if name and dev_type and dev_type.lower() == 'light':
                light_devices.append(device)
                print(f"✅ Found light: {name}")
        
        print(f"💡 Total lights found: {len(light_devices)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Hubspace: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return False

def get_device_attributes(device):
    """Get current device attributes"""
    try:
        attributes = device.getAttributes()
        result = {}
        
        # Find power attribute (ID 1)
        power_attr = next((attr for attr in attributes if attr['id'] == 1), None)
        if power_attr:
            result['power'] = "ON" if power_attr['value'] == '1' else "OFF"
        
        # Find brightness attribute (ID 2)
        brightness_attr = next((attr for attr in attributes if attr['id'] == 2), None)
        if brightness_attr:
            result['brightness'] = int(brightness_attr['value'])
        
        # Find color attribute (ID 4)
        color_attr = next((attr for attr in attributes if attr['id'] == 4), None)
        if color_attr:
            result['color'] = f"#{color_attr['value']}"
        
        return result
    except Exception as e:
        print(f"Error getting attributes for {device.getName()}: {e}")
        return {}

def control_device_thread(device, action=None, brightness=None, color=None):
    """Control a single device in a thread"""
    device_name = device.getName()
    device_id = device.getID()
    result = DeviceResult(
        name=device_name,
        device_id=device_id,
        success=False,
        message=""
    )
    
    try:
        # Get current state
        current_attrs = get_device_attributes(device)
        result.power_state = current_attrs.get('power')
        result.brightness = current_attrs.get('brightness')
        result.color = current_attrs.get('color')
        
        # Control power
        if action:
            if action.upper() == "ON":
                device.writeAction(1, "01")  # Attribute ID 1 = power, "01" = ON
                result.power_state = "ON"
            elif action.upper() == "OFF":
                device.writeAction(1, "00")  # Attribute ID 1 = power, "00" = OFF
                result.power_state = "OFF"
        
        # Control brightness (ID 2)
        if brightness is not None:
            # Convert percentage to hex (0-100 -> 00-64)
            brightness_hex = f"{brightness:02X}"
            device.writeAction(2, brightness_hex)
            result.brightness = brightness
        
        # Control color (ID 4)
        if color:
            # Remove # if present and ensure 6 characters
            color_clean = color.replace('#', '').upper()
            if len(color_clean) == 6:
                device.writeAction(4, color_clean)
                result.color = f"#{color_clean}"
        
        result.success = True
        result.message = f"Successfully controlled {device_name}"
        
    except Exception as e:
        result.message = f"Error controlling {device_name}: {str(e)}"
        result.success = False
    
    return result

# API endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize Hubspace on startup"""
    if not initialize_hubspace():
        raise Exception("Failed to initialize Hubspace client")

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Hubspace Light Control API",
        "version": "1.0.0",
        "lights_available": len(light_devices),
        "endpoints": {
            "GET /": "API information",
            "GET /lights": "List all available lights",
            "POST /control": "Control lights (requires authorization)"
        }
    }

@app.get("/test-env")
async def test_environment():
    """Test endpoint to check environment variables"""
    return {
        "email_set": bool(HUBSPACE_EMAIL),
        "password_set": bool(HUBSPACE_PASSWORD),
        "email_length": len(HUBSPACE_EMAIL) if HUBSPACE_EMAIL else 0,
        "password_length": len(HUBSPACE_PASSWORD) if HUBSPACE_PASSWORD else 0,
        "email_preview": HUBSPACE_EMAIL[:10] + "..." if HUBSPACE_EMAIL and len(HUBSPACE_EMAIL) > 10 else HUBSPACE_EMAIL
    }

@app.get("/lights")
async def get_lights():
    """Get list of all available lights"""
    global hubspace_client, light_devices
    
    # Re-authenticate with Hubspace before fetching devices
    print("🔄 Re-authenticating with Hubspace for device list...")
    if not initialize_hubspace():
        raise HTTPException(status_code=500, detail="Failed to authenticate with Hubspace")
    
    lights = []
    for device in light_devices:
        attrs = get_device_attributes(device)
        lights.append({
            "name": device.getName(),
            "device_id": device.getID(),
            "power": attrs.get('power', 'UNKNOWN'),
            "brightness": attrs.get('brightness'),
            "color": attrs.get('color')
        })
    
    return {
        "lights": lights,
        "count": len(lights)
    }

@app.post("/control", response_model=ControlResponse)
async def control_lights(
    request: LightControlRequest,
    _: bool = Depends(verify_token)
):
    """Control lights with the specified parameters"""
    
    global hubspace_client, light_devices
    
    # Re-authenticate with Hubspace before each command
    print("🔄 Re-authenticating with Hubspace...")
    if not initialize_hubspace():
        raise HTTPException(status_code=500, detail="Failed to authenticate with Hubspace")
    
    print(f"🔍 Found {len(light_devices)} devices to control")
    
    # Validate request
    if not any([request.action, request.brightness is not None, request.color]):
        raise HTTPException(status_code=400, detail="At least one control parameter must be specified")
    
    if request.action and request.action.upper() not in ["ON", "OFF"]:
        raise HTTPException(status_code=400, detail="Action must be 'ON' or 'OFF'")
    
    if request.brightness is not None and (request.brightness < 0 or request.brightness > 100):
        raise HTTPException(status_code=400, detail="Brightness must be between 0 and 100")
    
    if request.color and not request.color.startswith('#'):
        raise HTTPException(status_code=400, detail="Color must be in hex format (e.g., '#FF0000')")
    
    # Filter devices by name if specified
    target_devices = light_devices
    if request.name:
        target_devices = [d for d in light_devices if d.getName().lower() == request.name.lower()]
        if not target_devices:
            raise HTTPException(status_code=404, detail=f"No light found with name '{request.name}'")
    
    print(f"🎯 Targeting {len(target_devices)} devices")
    
    # Control devices in threads
    threads = []
    results = []
    
    for device in target_devices:
        print(f"⚡ Controlling device: {device.getName()}")
        thread = threading.Thread(
            target=lambda d=device: results.append(
                control_device_thread(d, request.action, request.brightness, request.color)
            )
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Prepare response
    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    
    print(f"✅ Control complete: {success_count}/{total_count} devices successful")
    
    response = ControlResponse(
        success=success_count == total_count,
        message=f"Controlled {success_count}/{total_count} devices successfully",
        results=results,
        timestamp=time.time()
    )
    
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global hubspace_client, light_devices
    
    # Re-authenticate to get current status
    print("🔄 Re-authenticating with Hubspace for health check...")
    hubspace_connected = initialize_hubspace()
    
    return {
        "status": "healthy",
        "hubspace_connected": hubspace_connected,
        "lights_available": len(light_devices),
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Hubspace Light Control API Server...")
    print(f"📡 Server will be available at: http://{HOST}:{PORT}")
    print("🔑 Use the SECRET_TOKEN in Authorization header: Bearer SECRET123")
    uvicorn.run(app, host=HOST, port=PORT) 