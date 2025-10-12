"""
Video encoding functionality using OpenCV
"""
import cv2
import numpy as np
import threading
import queue
import time
from typing import Optional, Tuple, Dict, Any
from pathlib import Path


class VideoEncoder:
    def __init__(self, output_path: str, fps: float = 30.0, quality: str = 'high'):
        """
        Initialize video encoder
        
        Args:
            output_path: Path where the video file will be saved
            fps: Frames per second for the output video
            quality: Video quality ('low', 'medium', 'high')
        """
        self.output_path = output_path
        self.fps = fps
        self.quality = quality
        
        self.writer = None
        self.frame_queue = queue.Queue(maxsize=100)  # Limit queue size to prevent memory issues
        self.recording = False
        self.encode_thread = None
        self.frame_size = None
        
        # Quality settings
        self.quality_settings = {
            'low': {'bitrate': 1000000, 'crf': 28},      # 1 Mbps
            'medium': {'bitrate': 3000000, 'crf': 23},   # 3 Mbps  
            'high': {'bitrate': 8000000, 'crf': 18}      # 8 Mbps
        }
    
    def _get_codec_and_container(self) -> Tuple[str, str]:
        """Get appropriate codec and container based on platform and availability"""
        output_path = Path(self.output_path)
        
        # Try different codecs in order of preference
        codecs_to_try = [
            ('mp4v', '.mp4'),  # MPEG-4 (widely supported)
            ('XVID', '.avi'),  # Xvid codec
            ('MJPG', '.avi'),  # Motion JPEG (fallback)
        ]
        
        for codec, ext in codecs_to_try:
            # Update file extension if needed
            if output_path.suffix.lower() != ext:
                self.output_path = str(output_path.with_suffix(ext))
            
            # Test if codec is available
            test_writer = cv2.VideoWriter()
            fourcc = cv2.VideoWriter_fourcc(*codec)
            
            if test_writer.open('test.avi', fourcc, 1, (100, 100)):
                test_writer.release()
                return codec, ext
        
        # Ultimate fallback
        return 'MJPG', '.avi'
    
    def start_encoding(self, frame_size: Tuple[int, int]):
        """
        Start video encoding
        
        Args:
            frame_size: (width, height) of video frames
        """
        self.frame_size = frame_size
        
        try:
            # Get codec and ensure proper file extension
            codec, _ = self._get_codec_and_container()
            fourcc = cv2.VideoWriter_fourcc(*codec)
            
            # Create video writer
            self.writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                self.fps,
                frame_size
            )
            
            if not self.writer.isOpened():
                raise Exception(f"Failed to open video writer with codec {codec}")
            
            self.recording = True
            self.encode_thread = threading.Thread(target=self._encode_frames)
            self.encode_thread.daemon = True
            self.encode_thread.start()
            
            print(f"✅ Video encoding started: {self.output_path}")
            
        except Exception as e:
            print(f"❌ Error starting video encoder: {e}")
            self.recording = False
    
    def add_frame(self, frame: np.ndarray) -> bool:
        """
        Add a frame to the encoding queue
        
        Args:
            frame: RGB frame as numpy array
            
        Returns:
            True if frame was added successfully, False if queue is full
        """
        if not self.recording:
            return False
        
        try:
            # Convert RGB to BGR (OpenCV uses BGR)
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Resize frame if necessary
            if self.frame_size and (bgr_frame.shape[1], bgr_frame.shape[0]) != self.frame_size:
                bgr_frame = cv2.resize(bgr_frame, self.frame_size)
            
            # Add timestamp to frame for debugging
            timestamp = time.time()
            self.frame_queue.put((bgr_frame, timestamp), block=False)
            return True
            
        except queue.Full:
            print("⚠️  Frame queue is full, dropping frame")
            return False
        except Exception as e:
            print(f"❌ Error adding frame: {e}")
            return False
    
    def _encode_frames(self):
        """Internal method to encode frames in a separate thread"""
        frame_count = 0
        start_time = time.time()
        
        while self.recording or not self.frame_queue.empty():
            try:
                # Get frame from queue with timeout
                frame_data = self.frame_queue.get(timeout=1.0)
                if frame_data is None:
                    break
                
                frame, timestamp = frame_data
                
                # Write frame to video file
                self.writer.write(frame)
                frame_count += 1
                
                # Progress logging every 100 frames
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    actual_fps = frame_count / elapsed if elapsed > 0 else 0
                    print(f"📹 Encoded {frame_count} frames (avg FPS: {actual_fps:.1f})")
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error encoding frame: {e}")
                break
        
        print(f"✅ Video encoding finished: {frame_count} frames encoded")
    
    def stop_encoding(self):
        """Stop video encoding"""
        self.recording = False
        
        # Wait for encoding thread to finish
        if self.encode_thread:
            self.encode_thread.join(timeout=5.0)
        
        # Clean up
        if self.writer:
            self.writer.release()
            self.writer = None
        
        print(f"✅ Video saved to: {self.output_path}")
    
    def get_queue_size(self) -> int:
        """Get current size of the frame queue"""
        return self.frame_queue.qsize()
    
    def is_recording(self) -> bool:
        """Check if encoder is currently recording"""
        return self.recording