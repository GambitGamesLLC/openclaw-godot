"""Godot project and runner management."""

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class GodotProject:
    """Represents a Godot project directory."""

    path: Path

    def __post_init__(self):
        self.path = Path(self.path)
        if not self.is_valid:
            raise ValueError(f"Not a valid Godot project: {self.path}")

    @property
    def is_valid(self) -> bool:
        """Check if directory contains project.godot."""
        return (self.path / "project.godot").exists()

    @property
    def project_file(self) -> Path:
        """Path to project.godot file."""
        return self.path / "project.godot"

    @property
    def name(self) -> str:
        """Extract project name from project.godot."""
        try:
            content = self.project_file.read_text()
            # Simple parse: config/name="Project Name"
            for line in content.split("\n"):
                if 'config/name=' in line:
                    return line.split('"')[1]
        except Exception:
            pass
        return self.path.name

    def list_scripts(self) -> List[Path]:
        """Find all .gd files in project."""
        return list(self.path.rglob("*.gd"))

    def list_scenes(self) -> List[Path]:
        """Find all .tscn files in project."""
        return list(self.path.rglob("*.tscn"))

    def read_script(self, script_path: str) -> str:
        """Read GDScript file contents.
        
        Args:
            script_path: Relative path (e.g., "scripts/player.gd")
            
        Returns:
            File contents as string
        """
        full_path = self.path / script_path
        return full_path.read_text()

    def write_script(self, script_path: str, content: str) -> Path:
        """Write GDScript file.
        
        Args:
            script_path: Relative path (e.g., "scripts/player.gd")
            content: Script content
            
        Returns:
            Path to written file
        """
        full_path = self.path / script_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        return full_path


class GodotRunner:
    """Run Godot projects and capture output."""

    def __init__(self, godot_path: str = "godot"):
        self.godot_path = godot_path
        self.process: Optional[subprocess.Popen] = None
        self.output: List[str] = []
        self.errors: List[str] = []

    def verify_godot(self) -> bool:
        """Check if Godot is installed and accessible."""
        try:
            result = subprocess.run(
                [self.godot_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def run_headless(
        self,
        project: GodotProject,
        scene: Optional[str] = None,
        quit_after: Optional[int] = None,
        fixed_fps: int = 60
    ) -> subprocess.Popen:
        """Run project in headless mode.
        
        Args:
            project: GodotProject to run
            scene: Optional specific scene to run
            quit_after: Quit after N frames (for testing)
            fixed_fps: Fixed FPS for deterministic playback
            
        Returns:
            Running subprocess
        """
        cmd = [
            self.godot_path,
            "--headless",
            "--debug",
            "--path", str(project.path),
            "--fixed-fps", str(fixed_fps)
        ]
        
        if quit_after:
            cmd.extend(["--quit-after", str(quit_after)])
        
        if scene:
            cmd.append(scene)

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        return self.process

    def run_with_display(
        self,
        project: GodotProject,
        scene: Optional[str] = None
    ) -> subprocess.Popen:
        """Run project with display (for interactive testing).
        
        Args:
            project: GodotProject to run
            scene: Optional specific scene to run
            
        Returns:
            Running subprocess
        """
        cmd = [
            self.godot_path,
            "--debug",
            "--path", str(project.path)
        ]
        
        if scene:
            cmd.append(scene)

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        return self.process

    def get_output(self, timeout: float = 0.5) -> Dict[str, List[str]]:
        """Get accumulated output from running process.
        
        Args:
            timeout: Time to wait for new output
            
        Returns:
            Dict with 'stdout' and 'stderr' lists
        """
        if not self.process:
            return {"stdout": [], "stderr": []}

        # Non-blocking read of available output
        import select
        
        stdout_lines = []
        stderr_lines = []
        
        if self.process.stdout:
            ready, _, _ = select.select([self.process.stdout], [], [], timeout)
            if ready:
                line = self.process.stdout.readline()
                if line:
                    stdout_lines.append(line.strip())
        
        if self.process.stderr:
            ready, _, _ = select.select([self.process.stderr], [], [], timeout)
            if ready:
                line = self.process.stderr.readline()
                if line:
                    stderr_lines.append(line.strip())

        self.output.extend(stdout_lines)
        self.errors.extend(stderr_lines)
        
        return {
            "stdout": stdout_lines,
            "stderr": stderr_lines
        }

    def stop(self) -> Dict[str, Any]:
        """Stop running process and collect final output.
        
        Returns:
            Dict with 'stdout', 'stderr', 'returncode'
        """
        if not self.process:
            return {"stdout": [], "stderr": [], "returncode": None}

        # Kill process
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()

        # Collect remaining output
        stdout, stderr = self.process.communicate()
        
        return {
            "stdout": stdout.split("\n") if stdout else [],
            "stderr": stderr.split("\n") if stderr else [],
            "returncode": self.process.returncode
        }

    def is_running(self) -> bool:
        """Check if process is still running."""
        if not self.process:
            return False
        return self.process.poll() is None

    def get_all_logs(self) -> str:
        """Get all accumulated logs as single string."""
        return "\n".join(self.output + self.errors)
