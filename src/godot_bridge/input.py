"""Input injection for Godot windows using PyAutoGUI."""

import time
from typing import Optional, Tuple

import pyautogui


class InputInjector:
    """Inject keyboard and mouse input into Godot windows."""

    def __init__(self):
        # Fail-safe: move mouse to corner to abort
        pyautogui.FAILSAFE = True
        # Small delay between actions for reliability
        pyautogui.PAUSE = 0.05

    def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: "left", "right", or "middle"
        """
        pyautogui.click(x, y, button=button)

    def move_to(self, x: int, y: int, duration: float = 0.0) -> None:
        """Move mouse to coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
        """
        pyautogui.moveTo(x, y, duration=duration)

    def key_press(self, key: str) -> None:
        """Press a key.
        
        Args:
            key: Key name (e.g., "space", "enter", "esc", "a", "1")
        """
        pyautogui.press(key)

    def key_down(self, key: str) -> None:
        """Hold a key down.
        
        Args:
            key: Key name
        """
        pyautogui.keyDown(key)

    def key_up(self, key: str) -> None:
        """Release a key.
        
        Args:
            key: Key name
        """
        pyautogui.keyUp(key)

    def type_text(self, text: str, interval: float = 0.01) -> None:
        """Type text.
        
        Args:
            text: Text to type
            interval: Seconds between keystrokes
        """
        pyautogui.typewrite(text, interval=interval)

    def hotkey(self, *keys: str) -> None:
        """Press key combination (e.g., Ctrl+C).
        
        Args:
            *keys: Key names in order (e.g., "ctrl", "c")
        """
        pyautogui.hotkey(*keys)

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Scroll mouse wheel.
        
        Args:
            clicks: Number of clicks (positive=up, negative=down)
            x: Optional X position to scroll at
            y: Optional Y position to scroll at
        """
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x, y)
        else:
            pyautogui.scroll(clicks)

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            (x, y) tuple
        """
        return pyautogui.position()

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions.
        
        Returns:
            (width, height) tuple
        """
        return pyautogui.size()

    def wait(self, seconds: float) -> None:
        """Sleep for duration.
        
        Args:
            seconds: Time to sleep
        """
        time.sleep(seconds)

    def find_on_screen(
        self, 
        image_path: str, 
        confidence: float = 0.9,
        grayscale: bool = False
    ) -> Optional[Tuple[int, int, int, int]]:
        """Find image on screen.
        
        Args:
            image_path: Path to image to search for
            confidence: Match confidence (0.0-1.0)
            grayscale: Convert to grayscale for matching
            
        Returns:
            (left, top, width, height) of match or None
        """
        try:
            location = pyautogui.locateOnScreen(
                image_path, 
                confidence=confidence,
                grayscale=grayscale
            )
            return location if location else None
        except Exception:
            return None

    def click_image(
        self, 
        image_path: str, 
        confidence: float = 0.9,
        button: str = "left"
    ) -> bool:
        """Click on image if found on screen.
        
        Args:
            image_path: Path to image to click
            confidence: Match confidence
            button: Mouse button
            
        Returns:
            True if clicked, False if not found
        """
        location = self.find_on_screen(image_path, confidence)
        if location:
            center = pyautogui.center(location)
            self.click(center.x, center.y, button)
            return True
        return False
