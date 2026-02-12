"""OpenClaw-Godot: Python bridge for autonomous Godot development."""

__version__ = "0.1.0"

from .capture import ScreenshotCapture
from .input import InputInjector
from .godot import GodotProject, GodotRunner

__all__ = [
    "ScreenshotCapture",
    "InputInjector", 
    "GodotProject",
    "GodotRunner",
]
