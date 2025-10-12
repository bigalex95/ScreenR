#!/usr/bin/env python3
"""
Test audio capture functionality
"""
import sys
sys.path.append('/home/bigalex95/Projects/Pet_Projects/ScreenR')

from recorder.audio_capture import AudioCapture
import time

def test_audio_capture():
    print("🎤 Testing audio capture...")
    
    # Initialize audio capture
    audio_capture = AudioCapture()
    
    # Get available devices
    devices = audio_capture.get_audio_devices()
    print(f"Available audio devices: {len(devices)}")
    for i, device in enumerate(devices):
        print(f"  {i}: {device['name']} ({device['channels']} channels)")
    
    if not devices:
        print("❌ No audio devices found")
        return False
    
    # Try to start capture with the first available device
    print("🎤 Starting audio capture test...")
    success = audio_capture.start_capture(devices[0]['index'] if devices else None)
    
    if not success:
        print("❌ Failed to start audio capture")
        return False
    
    print("✅ Audio capture started, recording for 3 seconds...")
    
    # Record for 3 seconds
    frames_captured = 0
    start_time = time.time()
    
    while time.time() - start_time < 3.0:
        frame = audio_capture.get_audio_frame()
        if frame is not None:
            frames_captured += 1
        time.sleep(0.01)  # Small delay
    
    # Stop capture
    audio_capture.stop_capture()
    
    print(f"✅ Audio test completed: {frames_captured} frames captured")
    
    # Check if audio file was created
    audio_file = audio_capture.get_temp_audio_file()
    if audio_file:
        import os
        file_size = os.path.getsize(audio_file)
        print(f"✅ Audio file created: {audio_file} ({file_size} bytes)")
    else:
        print("❌ No audio file created")
    
    audio_capture.cleanup()
    return frames_captured > 0

if __name__ == "__main__":
    success = test_audio_capture()
    sys.exit(0 if success else 1)