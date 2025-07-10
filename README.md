# Hubspace Smart Light Control

A simple Python script to control your Hubspace smart lights directly from your computer, using the open-source [`hubspace`](https://github.com/jan-leila/hubspace-py) library.

## Features

- 🔐 Secure authentication with Hubspace
- 📱 List all your smart devices
- 💡 Turn devices on/off
- 📊 Get device status and state
- 🐍 Clean, beginner-friendly Python code

## Setup

### Prerequisites

- Python 3.8 or higher
- macOS (tested on Mac Mini M4)
- Virtual environment (recommended)

### Installation

1. **Clone or download the files to your computer**

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv hubspace_env
   source hubspace_env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Update your credentials:**
   Open `hubspace_control.py` and update the email and password:
   ```python
   email = "your-email@example.com"
   password = "your-password"
   ```

## Usage

### Basic Usage

Run the script to control your lights:

```bash
python hubspace_control.py
```

The script will:
1. Authenticate with Hubspace
2. List all your devices
3. Turn the first device on, then off as a demo
4. Show device status

### Example Output

```
🔐 Authenticating with Hubspace and fetching devices...

🏠 Found devices:
----------------------------------------
1. Living Room Light (ID: light_001)
   Type: light

2. Kitchen Light (ID: light_002)
   Type: light

3. Bedroom Switch (ID: switch_001)
   Type: switch

💡 Controlling device: Living Room Light
🔆 Turning device ON...
✅ Turned ON!
🌙 Turning device OFF...
✅ Turned OFF!
📊 Getting device state...
Device state: {'power': False, 'brightness': 0}

✅ Script completed successfully!
```

## Customization

### Control Specific Devices

You can modify the script to control specific devices:

```python
# Get all devices
devices = hubspace.getDevices()

# Find a specific device by name
kitchen_light = None
for device in devices:
    if "kitchen" in device.getName().lower():
        kitchen_light = device
        break

if kitchen_light:
    # Turn on kitchen light
    kitchen_light.writeAction('power', True)
```

### Add More Commands

The `Device` class supports various commands:

```python
# Turn device on/off
device.writeAction('power', True)   # Turn on
device.writeAction('power', False)  # Turn off

# Get device state
state = device.getState()
print(f"Device is {'ON' if state.get('power') else 'OFF'}")
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your email and password
   - Make sure your Hubspace account is active
   - Try logging into the Hubspace app first

2. **No Devices Found**
   - Ensure you have Hubspace devices set up
   - Check that devices are connected to your account
   - Try refreshing the device list in the Hubspace app

3. **Network Errors**
   - Check your internet connection
   - Ensure you can access hubspace.com
   - Try again in a few minutes

4. **Import Errors**
   - Make sure you're in the correct directory
   - Verify all files are present: `hubspace_control.py`
   - Check that dependencies are installed: `pip list`

## Security Notes

⚠️ **Important Security Considerations:**

1. **Don't hardcode passwords** in production code
2. **Use environment variables** for sensitive data:
   ```python
   import os
   email = os.getenv('HUBSPACE_EMAIL')
   password = os.getenv('HUBSPACE_PASSWORD')
   ```
3. **Keep your credentials secure** and don't share them
4. **Consider using a config file** for development

## File Structure

```
Hubspace/
├── hubspace_control.py     # Main script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Dependencies

- `hubspace`: For Hubspace device control

## Contributing

Feel free to improve this script! Some ideas:
- Add support for dimming lights
- Add color control for RGB lights
- Create a GUI interface
- Add scheduling capabilities
- Support for more device types

## License

This is a simple educational script. Use at your own risk and respect Hubspace's terms of service. 