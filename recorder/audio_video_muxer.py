"""
Audio-Video muxing functionality using FFmpeg subprocess
"""
import os
import subprocess
from pathlib import Path
from typing import Optional


class AudioVideoMuxer:
    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available on the system"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def mux_audio_video(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        Combine video and audio files into a single output file
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file  
            output_path: Path for output file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ffmpeg_available:
            print("❌ FFmpeg not available for audio-video muxing")
            return False
        
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False
            
        if not os.path.exists(audio_path):
            print(f"❌ Audio file not found: {audio_path}")
            return False
        
        try:
            print(f"🎬 Muxing audio and video...")
            print(f"   Video: {video_path}")
            print(f"   Audio: {audio_path}")
            print(f"   Output: {output_path}")
            
            # Use FFmpeg subprocess to combine video and audio
            cmd = [
                'ffmpeg',
                '-i', video_path,      # Input video
                '-i', audio_path,      # Input audio
                '-c:v', 'copy',        # Copy video stream as-is
                '-c:a', 'aac',         # Re-encode audio to AAC
                '-strict', 'experimental',
                '-y',                  # Overwrite output file
                output_path
            ]
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ Audio-video muxing completed: {output_path}")
                return True
            else:
                print(f"❌ FFmpeg error: {result.stderr}")
                return False
            
        except subprocess.TimeoutExpired:
            print("❌ FFmpeg timeout during audio-video muxing")
            return False
        except Exception as e:
            print(f"❌ Error during audio-video muxing: {e}")
            return False
    
    def mux_with_fallback(self, video_path: str, audio_path: Optional[str], 
                         output_path: str) -> str:
        """
        Mux audio and video with fallback to video-only
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file (can be None)
            output_path: Path for output file
            
        Returns:
            Path to the final output file
        """
        if not audio_path or not os.path.exists(audio_path):
            print("ℹ️  No audio file available, keeping video-only")
            return video_path
        
        # Check if audio file has content
        try:
            audio_size = os.path.getsize(audio_path)
            if audio_size < 1000:  # Less than 1KB indicates no real audio data
                print("ℹ️  Audio file too small, keeping video-only")
                return video_path
        except OSError:
            print("ℹ️  Cannot check audio file size, keeping video-only")
            return video_path
        
        # Try to mux
        if self.mux_audio_video(video_path, audio_path, output_path):
            # Clean up temporary files
            try:
                os.remove(video_path)  # Remove video-only file
                os.remove(audio_path)  # Remove audio file
            except OSError:
                pass
            return output_path
        else:
            print("⚠️  Audio-video muxing failed, keeping video-only")
            return video_path