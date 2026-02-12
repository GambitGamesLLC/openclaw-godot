"""Screenshot capture for Godot windows."""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import mss
import mss.tools
from PIL import Image


class ScreenshotCapture:
    """Capture screenshots of Godot windows using mss (Multi-Screen Shot)."""

    def __init__(self):
        self.sct = mss.mss()

    def capture_screen(self, monitor: int = 1) -> Image.Image:
        """Capture entire screen/monitor.
        
        Args:
            monitor: Monitor number (1 = primary, etc.)
            
        Returns:
            PIL Image
        """
        screenshot = self.sct.grab(self.sct.monitors[monitor])
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    def capture_window(
        self, 
        window_title: str = "Godot", 
        fallback_to_screen: bool = True
    ) -> Optional[Image.Image]:
        """Capture specific window by title.
        
        Uses xdotool on Linux to find window geometry, falls back
        to full screen capture if window not found.
        
        Args:
            window_title: Substring to match in window title
            fallback_to_screen: Capture full screen if window not found
            
        Returns:
            PIL Image or None if capture failed
        """
        try:
            # Get window ID
            result = subprocess.run(
                ["xdotool", "search", "--name", window_title],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                if fallback_to_screen:
                    return self.capture_screen()
                return None
            
            window_id = result.stdout.strip().split("\n")[0]
            
            # Get window geometry
            geo_result = subprocess.run(
                ["xdotool", "getwindowgeometry", window_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Parse geometry (format varies, this is simplified)
            # TODO: Parse actual window coordinates from xdotool output
            # For now, fall back to full screen
            return self.capture_screen()
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            if fallback_to_screen:
                return self.capture_screen()
            return None

    def capture_region(self, left: int, top: int, width: int, height: int) -> Image.Image:
        """Capture specific screen region.
        
        Args:
            left: X coordinate
            top: Y coordinate
            width: Region width
            height: Region height
            
        Returns:
            PIL Image
        """
        monitor = {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }
        screenshot = self.sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    def save_screenshot(
        self, 
        image: Image.Image, 
        path: Path,
        format: str = "PNG"
    ) -> Path:
        """Save screenshot to file.
        
        Args:
            image: PIL Image to save
            path: Output file path
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Path to saved file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, format=format)
        return path

    def close(self):
        """Release resources."""
        self.sct.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
