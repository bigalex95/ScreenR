"""
Main recorder manager that coordinates screen capture, audio capture, and video encoding
"""
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from .screen_capture import ScreenCapture
from .audio_capture import AudioCapture
from .video_encoder import VideoEncoder
from .audio_video_muxer import AudioVideoMuxer


class RecorderManager:
    def __init__(self):
        self.screen_capture = ScreenCapture()
        self.audio_capture = AudioCapture()
        self.video_encoder = None
        self.audio_video_muxer = AudioVideoMuxer()
        
        self.recording = False
        self.paused = False
        self.capture_thread = None
        
        # Recording settings
        self.settings = {
            'fps': 30.0,
            'quality': 'high',
            'audio_enabled': True,
            'audio_device': None,
            'output_directory': str(Path.home() / 'Videos'),
            'area_type': 'fullscreen',
            'custom_area': None
        }
        
        # Callbacks for UI updates
        self.status_callback = None
        self.progress_callback = None
        
        # Recording statistics
        self.stats = {
            'start_time': None,
            'frames_captured': 0,
            'frames_dropped': 0,
            'recording_duration': 0
        }
        
        # File paths for current recording
        self.current_video_path = None
        self.current_audio_path = None
    
    def set_settings(self, **kwargs):
        """Update recording settings"""
        for key, value in kwargs.items():
            if key in self.settings:
                self.settings[key] = value
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def _notify_status(self, status: str):
        """Notify status change via callback"""
        if self.status_callback:
            self.status_callback(status)
        print(f"📹 Status: {status}")
    
    def _notify_progress(self):
        """Notify progress via callback"""
        if self.progress_callback:
            self.progress_callback(self.stats.copy())
    
    def get_available_audio_devices(self):
        """Get list of available audio input devices"""
        return self.audio_capture.get_audio_devices()
    
    def start_recording(self, output_filename: Optional[str] = None) -> bool:
        """
        Start recording
        
        Args:
            output_filename: Custom filename for output video (optional)
            
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.recording:
            self._notify_status("Already recording")
            return False
        
        try:
            # Generate output filename if not provided
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"screen_recording_{timestamp}"
            
            # Ensure output directory exists
            output_dir = Path(self.settings['output_directory'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Set up file paths
            video_filename = f"{output_filename}_video.mp4"
            final_filename = f"{output_filename}.mp4"
            
            self.current_video_path = str(output_dir / video_filename)
            final_output_path = str(output_dir / final_filename)
            
            # Set up screen capture area
            self.screen_capture.set_recording_area(
                self.settings['area_type'],
                self.settings['custom_area']
            )
            
            # Get recording dimensions
            width, height = self.screen_capture.get_recording_dimensions()
            
            # Initialize video encoder
            self.video_encoder = VideoEncoder(
                self.current_video_path,
                self.settings['fps'],
                self.settings['quality']
            )
            
            # Start video encoding
            self.video_encoder.start_encoding((width, height))
            
            # Start audio capture if enabled
            audio_started = False
            if self.settings['audio_enabled']:
                print("🎤 Starting audio capture...")
                audio_started = self.audio_capture.start_capture(self.settings['audio_device'])
                if audio_started:
                    print("✅ Audio capture started")
                else:
                    print("⚠️  Audio capture failed, continuing with video only")
            
            # Reset statistics
            self.stats = {
                'start_time': time.time(),
                'frames_captured': 0,
                'frames_dropped': 0,
                'recording_duration': 0,
                'output_file': final_output_path,
                'audio_enabled': audio_started
            }
            
            # Start recording thread
            self.recording = True
            self.paused = False
            self.capture_thread = threading.Thread(target=self._recording_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            self._notify_status(f"Recording started: {final_filename}")
            return True
            
        except Exception as e:
            self._notify_status(f"Failed to start recording: {e}")
            print(f"❌ Error starting recording: {e}")
            return False
    
    def pause_recording(self):
        """Pause recording"""
        if self.recording and not self.paused:
            self.paused = True
            self._notify_status("Recording paused")
    
    def resume_recording(self):
        """Resume recording"""
        if self.recording and self.paused:
            self.paused = False
            self._notify_status("Recording resumed")
    
    def stop_recording(self):
        """Stop recording"""
        if not self.recording:
            return
        
        self._notify_status("Stopping recording...")
        self.recording = False
        self.paused = False
        
        # Wait for recording thread to finish
        if self.capture_thread:
            self.capture_thread.join(timeout=5.0)
        
        # Stop video encoder
        if self.video_encoder:
            self.video_encoder.stop_encoding()
        
        # Stop audio capture and get audio file
        self.current_audio_path = None
        if self.stats.get('audio_enabled', False):
            self.audio_capture.stop_capture()
            self.current_audio_path = self.audio_capture.get_temp_audio_file()
        
        # Calculate final stats
        if self.stats['start_time']:
            self.stats['recording_duration'] = time.time() - self.stats['start_time']
        
        # Mux audio and video if both are available
        final_output = self._finalize_recording()
        self.stats['output_file'] = final_output
        
        self._notify_status("Recording stopped")
        self._notify_progress()
    
    def _finalize_recording(self) -> str:
        """Finalize recording by muxing audio and video"""
        if not self.current_video_path:
            return ""
        
        # If no audio or audio-video muxing not available, return video file
        if not self.current_audio_path:
            print("ℹ️  No audio captured, finalizing video-only recording")
            return self.current_video_path
        
        # Generate final output path
        video_path = Path(self.current_video_path)
        final_path = video_path.parent / video_path.name.replace('_video.mp4', '.mp4')
        
        # Mux audio and video
        result = self.audio_video_muxer.mux_with_fallback(
            self.current_video_path,
            self.current_audio_path,
            str(final_path)
        )
        
        return result
    
    def _recording_loop(self):
        """Main recording loop"""
        target_frame_time = 1.0 / self.settings['fps']
        last_frame_time = time.time()
        
        while self.recording:
            loop_start = time.time()
            
            if not self.paused:
                # Capture screen frame
                frame = self.screen_capture.capture_frame()
                
                if frame is not None:
                    # Add frame to video encoder
                    if self.video_encoder and self.video_encoder.add_frame(frame):
                        self.stats['frames_captured'] += 1
                    else:
                        self.stats['frames_dropped'] += 1
                else:
                    self.stats['frames_dropped'] += 1
                
                # Update statistics periodically
                if self.stats['frames_captured'] % 30 == 0:  # Every second at 30fps
                    self.stats['recording_duration'] = time.time() - self.stats['start_time']
                    self._notify_progress()
            
            # Frame rate control
            elapsed = time.time() - loop_start
            sleep_time = target_frame_time - elapsed
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            last_frame_time = time.time()
    
    def get_recording_stats(self) -> Dict[str, Any]:
        """Get current recording statistics"""
        if self.stats['start_time']:
            self.stats['recording_duration'] = time.time() - self.stats['start_time']
        return self.stats.copy()
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.recording
    
    def is_paused(self) -> bool:
        """Check if recording is paused"""
        return self.paused
    
    def cleanup(self):
        """Clean up all resources"""
        if self.recording:
            self.stop_recording()
        
        self.screen_capture.cleanup()
        self.audio_capture.cleanup()
        
        if self.video_encoder:
            self.video_encoder.stop_encoding()