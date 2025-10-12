#!/usr/bin/env python3
"""
Quick test script to check if screen capture is working
"""
import sys
sys.path.append('/home/bigalex95/Projects/Pet_Projects/ScreenR')

from recorder.screen_capture import ScreenCapture
import time

def test_screen_capture():
    print("Testing screen capture...")
    
    capture = ScreenCapture()
    
    if not capture.sct:
        print("❌ Failed to initialize screen capture")
        return False
    
    print("✅ Screen capture initialized")
    print(f"Monitor info: {capture.monitor_info}")
    
    # Set recording area
    capture.set_recording_area('fullscreen')
    print(f"Recording dimensions: {capture.get_recording_dimensions()}")
    
    # Try to capture a frame
    print("Capturing test frame...")
    frame = capture.capture_frame()
    
    if frame is not None:
        print(f"✅ Successfully captured frame: {frame.shape}")
        return True
    else:
        print("❌ Failed to capture frame")
        return False
    
    capture.cleanup()

if __name__ == "__main__":
    success = test_screen_capture()
    sys.exit(0 if success else 1)