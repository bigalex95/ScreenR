"""
Audio capture functionality using pyaudio with better error handling
"""
import pyaudio
import numpy as np
import threading
import queue
import wave
import tempfile
import os
from typing import Optional, List, Dict, Any


class AudioCapture:
    def __init__(self, sample_rate: int = 44100, channels: int = 2, chunk_size: int = 1024):
        """
        Initialize audio capture
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1=mono, 2=stereo)
            chunk_size: Number of frames per buffer
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        
        self.audio = None
        self.stream = None
        self.recording = False
        self.audio_queue = queue.Queue()
        self.capture_thread = None
        
        # Audio file for temporary storage
        self.temp_audio_file = None
        self.wave_file = None
        
        # Initialize PyAudio with error handling
        self._init_audio()
        
    def _init_audio(self):
        """Initialize PyAudio with proper error handling"""
        try:
            self.audio = pyaudio.PyAudio()
            print("✅ PyAudio initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize PyAudio: {e}")
            self.audio = None
    
    def get_audio_devices(self) -> List[Dict[str, Any]]:
        """Get list of available audio input devices with better filtering"""
        if not self.audio:
            return []
        
        devices = []
        try:
            for i in range(self.audio.get_device_count()):
                try:
                    device_info = self.audio.get_device_info_by_index(i)
                    
                    # Only include devices that can record
                    if device_info.get('maxInputChannels', 0) > 0:
                        # Test if device is actually usable
                        if self._test_device(i):
                            devices.append({
                                'index': i,
                                'name': device_info.get('name', f'Device {i}'),
                                'channels': device_info.get('maxInputChannels', 0),
                                'sample_rate': device_info.get('defaultSampleRate', 44100),
                                'host_api': device_info.get('hostApi', 0)
                            })
                except Exception as e:
                    print(f"Warning: Error getting device {i} info: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error listing audio devices: {e}")
            
        return devices
    
    def _test_device(self, device_index: int) -> bool:
        """Test if an audio device is actually usable"""
        try:
            # Try to open a test stream
            test_stream = self.audio.open(
                format=self.format,
                channels=1,  # Use mono for testing
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                start=False  # Don't start the stream
            )
            test_stream.close()
            return True
        except Exception:
            return False
    
    def start_capture(self, device_index: Optional[int] = None) -> bool:
        """
        Start audio capture with better error handling
        
        Args:
            device_index: Index of audio device to use (None for default)
            
        Returns:
            True if capture started successfully, False otherwise
        """
        if not self.audio:
            print("❌ PyAudio not available")
            return False
            
        try:
            # Create temporary file for audio storage
            self.temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            self.wave_file = wave.open(self.temp_audio_file.name, 'wb')
            self.wave_file.setnchannels(self.channels)
            self.wave_file.setsampwidth(self.audio.get_sample_size(self.format))
            self.wave_file.setframerate(self.sample_rate)
            
            # Try different configurations if the specified one fails
            configs_to_try = [
                # Original configuration
                {
                    'format': self.format,
                    'channels': self.channels,
                    'rate': self.sample_rate,
                    'device_index': device_index
                },
                # Fallback to mono
                {
                    'format': self.format,
                    'channels': 1,
                    'rate': self.sample_rate,
                    'device_index': device_index
                },
                # Fallback to default device
                {
                    'format': self.format,
                    'channels': 1,
                    'rate': self.sample_rate,
                    'device_index': None
                }
            ]
            
            for config in configs_to_try:
                try:
                    print(f"Trying audio config: {config}")
                    
                    self.stream = self.audio.open(
                        format=config['format'],
                        channels=config['channels'],
                        rate=config['rate'],
                        input=True,
                        input_device_index=config['device_index'],
                        frames_per_buffer=self.chunk_size
                    )
                    
                    # Update instance variables to match successful config
                    self.channels = config['channels']
                    self.wave_file.setnchannels(self.channels)
                    
                    print(f"✅ Audio capture started with {self.channels} channel(s)")
                    break
                    
                except Exception as e:
                    print(f"❌ Audio config failed: {e}")
                    if self.stream:
                        self.stream.close()
                        self.stream = None
                    continue
            
            if not self.stream:
                print("❌ Failed to open any audio configuration")
                return False
            
            self.recording = True
            self.capture_thread = threading.Thread(target=self._capture_audio)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting audio capture: {e}")
            self.recording = False
            return False
    
    def _capture_audio(self):
        """Internal method to capture audio in a separate thread"""
        print("🎤 Audio capture thread started")
        frames_captured = 0
        
        while self.recording and self.stream:
            try:
                audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Write to WAV file
                if self.wave_file:
                    self.wave_file.writeframes(audio_data)
                
                # Convert to numpy array and add to queue for real-time processing
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                self.audio_queue.put(audio_array)
                
                frames_captured += 1
                if frames_captured % 100 == 0:
                    print(f"🎤 Captured {frames_captured} audio frames")
                
            except Exception as e:
                print(f"❌ Error capturing audio data: {e}")
                break
        
        print(f"🎤 Audio capture finished: {frames_captured} frames")
    
    def get_audio_frame(self) -> Optional[np.ndarray]:
        """
        Get the next audio frame from the queue
        
        Returns:
            numpy array of audio data, or None if no data available
        """
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_capture(self):
        """Stop audio capture"""
        print("🎤 Stopping audio capture...")
        self.recording = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.wave_file:
            self.wave_file.close()
            self.wave_file = None
        
        if self.temp_audio_file:
            self.temp_audio_file.close()
    
    def get_temp_audio_file(self) -> Optional[str]:
        """Get path to temporary audio file"""
        if self.temp_audio_file:
            return self.temp_audio_file.name
        return None
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_capture()
        
        # Clean up temporary file
        if self.temp_audio_file:
            try:
                os.unlink(self.temp_audio_file.name)
            except OSError:
                pass
        
        if self.audio:
            self.audio.terminate()
            self.audio = None