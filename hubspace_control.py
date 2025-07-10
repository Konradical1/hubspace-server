#!/usr/bin/env python3
"""
Hubspace Smart Light Control Script (using hubspace-py)
A simple script to control your Hubspace smart lights from your computer

Usage:
    python hubspace_control.py

Features:
    - Authenticate with Hubspace
    - List all your devices
    - Turn devices on/off in sync
    - Get device status
"""

from hubspace import Hubspace
import time
import threading

# Your Hubspace account credentials
# ⚠️  SECURITY NOTE: In a real application, don't hardcode passwords!
# Consider using environment variables or a config file
email = "fischerpaxton@gmail.com"
password = "EagleAva4!"  # Consider not hardcoding passwords

# Create Hubspace client instance
hubspace = Hubspace(email, password)

def control_device(device, power_state, device_name):
    """Control a single device in a separate thread"""
    try:
        if power_state == "ON":
            device.writeAction(1, "01")  # Attribute ID 1 = power, "01" = ON
            print(f"   ✅ {device_name} turned ON!")
        else:
            device.writeAction(1, "00")  # Attribute ID 1 = power, "00" = OFF
            print(f"   ✅ {device_name} turned OFF!")
        return True
    except Exception as e:
        print(f"   ❌ Failed to turn {power_state} {device_name}: {e}")
        return False

try:
    print("🔐 Authenticating with Hubspace and fetching devices...")
    # Get all device objects
    devices = hubspace.getDevices()
    if not devices:
        print("❌ No devices found! Make sure you have Hubspace devices set up.")
        exit(1)

    # Display all found devices
    print("\n🏠 Found devices:")
    print("-" * 40)
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device.getName()} (ID: {device.getID()})")
        print(f"   Type: {device.getDeviceClass()}")
        print()

    # Find all light devices
    light_devices = []
    for device in devices:
        name = device.getName()
        dev_type = device.getDeviceClass()
        if name and dev_type and dev_type.lower() == 'light':
            light_devices.append(device)
            print(f"✅ Found light: {name}")

    if not light_devices:
        print("❌ No light devices found to control!")
        exit(1)

    print(f"\n💡 Found {len(light_devices)} light(s) to control")

    # Turn ON all lights in sync
    print("\n🔆 Turning ON all lights simultaneously...")
    threads = []
    for device in light_devices:
        thread = threading.Thread(
            target=control_device, 
            args=(device, "ON", device.getName())
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Wait a moment to see them all on
    print("\n⏰ Waiting 3 seconds to see all lights ON...")
    time.sleep(3)

    # Turn OFF all lights in sync
    print("\n🌙 Turning OFF all lights simultaneously...")
    threads = []
    for device in light_devices:
        thread = threading.Thread(
            target=control_device, 
            args=(device, "OFF", device.getName())
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Get and display device states
    print("\n📊 Getting device states...")
    for device in light_devices:
        try:
            attributes = device.getAttributes()
            # Find the power attribute (ID 1)
            power_attr = next((attr for attr in attributes if attr['id'] == 1), None)
            if power_attr:
                power_state = "ON" if power_attr['value'] == '1' else "OFF"
                print(f"   {device.getName()}: Power is {power_state} (value: {power_attr['value']})")
            else:
                print(f"   {device.getName()}: Could not determine power state")
        except Exception as e:
            print(f"   {device.getName()}: Error getting state - {e}")

    print("\n✅ Script completed successfully!")

except Exception as e:
    print(f"❌ An error occurred: {str(e)}")
    print("💡 This might be due to:")
    print("   - Incorrect email/password")
    print("   - Network connectivity issues")
    print("   - Hubspace API changes")
    print("   - No devices found in your account") 