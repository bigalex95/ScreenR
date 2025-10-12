"""
Screen capture functionality using mss library
"""
import mss
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional, Tuple
import threading


class ScreenCapture:
    def __init__(self):
        self.sct = None
        self.recording_area = None
        self.monitor_info = None
        self._thread_local = threading.local()
        self._init_capture()
    
    def _init_capture(self):
        """Initialize screen capture - called once"""
        try:
            self.sct = mss.mss()
            self.monitor_info = self._get_monitor_info()
        except Exception as e:
            print(f"Error initializing screen capture: {e}")
            self.sct = None
    
    def _get_thread_local_sct(self):
        """Get thread-local mss instance"""
        if not hasattr(self._thread_local, 'sct'):
            try:
                self._thread_local.sct = mss.mss()
            except Exception as e:
                print(f"Error creating thread-local screen capture: {e}")
                return None
        return self._thread_local.sct
    
    def _get_monitor_info(self) -> Dict[str, Any]:
        """Get information about all available monitors"""
        if not self.sct:
            return {'count': 0, 'monitors': [], 'all_monitors': None}
            
        monitors = self.sct.monitors
        return {
            'count': len(monitors) - 1,  # Exclude the first 'all monitors' entry
            'monitors': monitors[1:],    # Individual monitors
            'all_monitors': monitors[0]   # All monitors combined
        }
    
    def set_recording_area(self, area_type: str, custom_area: Optional[Dict] = None):
        """
        Set the area to record
        
        Args:
            area_type: 'fullscreen' or 'custom'
            custom_area: Dict with 'top', 'left', 'width', 'height' for custom area
        """
        if not self.monitor_info:
            return
            
        if area_type == 'fullscreen':
            self.recording_area = self.monitor_info['all_monitors']
        elif area_type == 'custom' and custom_area:
            self.recording_area = {
                'top': custom_area['top'],
                'left': custom_area['left'],
                'width': custom_area['width'],
                'height': custom_area['height']
            }
        else:
            # Default to primary monitor
            if self.monitor_info['monitors']:
                self.recording_area = self.monitor_info['monitors'][0]
            else:
                # Fallback area
                self.recording_area = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the screen
        
        Returns:
            numpy array representing the captured frame, or None if capture fails
        """
        try:
            if not self.recording_area:
                self.set_recording_area('fullscreen')
            
            # Get thread-local screen capture instance
            sct = self._get_thread_local_sct()
            if not sct:
                return None
            
            # Capture the screen
            screenshot = sct.grab(self.recording_area)
            
            # Convert to numpy array
            frame = np.array(screenshot)
            
            # Convert from BGRA to RGB (mss returns BGRA format)
            frame = frame[:, :, [2, 1, 0]]  # BGR to RGB
            
            return frame
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def get_recording_dimensions(self) -> Tuple[int, int]:
        """Get the dimensions of the recording area"""
        if not self.recording_area:
            self.set_recording_area('fullscreen')
        
        if self.recording_area:
            return self.recording_area['width'], self.recording_area['height']
        else:
            return 1920, 1080  # Fallback dimensions
    
    def cleanup(self):
        """Clean up resources"""
        if self.sct:
            self.sct.close()
            self.sct = None
        
        # Clean up thread-local instances
        if hasattr(self._thread_local, 'sct'):
            try:
                self._thread_local.sct.close()
            except:
                pass