"""OpenClaw-Godot: Python bridge for autonomous Godot development."""

__version__ = "0.1.0"

from .capture import ScreenshotCapture
from .godot import GodotProject, GodotRunner

# InputInjector requires tkinter - import only when needed
# from .input import InputInjector

__all__ = [
    "ScreenshotCapture",
    # "InputInjector",  # Requires tkinter
    "GodotProject",
    "GodotRunner",
]
