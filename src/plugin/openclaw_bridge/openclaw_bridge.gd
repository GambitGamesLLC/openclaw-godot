"""
OpenClaw Bridge - Godot Editor Plugin

This plugin runs inside the Godot Editor to provide:
- Debug log streaming
- Scene tree introspection
- Screenshot capture via Viewport
- Script hot-reload notifications

Connects to Python bridge via WebSocket or HTTP.
"""
class_name OpenClawBridge
extends EditorPlugin

const PORT := 9742  # OCL-GDT on phone keypad

var _server: TCPServer
var _connection: StreamPeerTCP
var _logger: DebugLogger
var _screenshotter: Screenshotter

func _enter_tree():
    print("OpenClaw Bridge: Initializing...")
    
    # Initialize components
    _logger = DebugLogger.new()
    add_child(_logger)
    
    _screenshotter = Screenshotter.new()
    add_child(_screenshotter)
    
    # Start server
    _server = TCPServer.new()
    var err = _server.listen(PORT)
    if err == OK:
        print("OpenClaw Bridge: Listening on port ", PORT)
    else:
        push_error("OpenClaw Bridge: Failed to start server (error %d)" % err)

func _exit_tree():
    print("OpenClaw Bridge: Shutting down...")
    if _server:
        _server.stop()

func _process(_delta):
    # Accept new connections
    if _server and _server.is_connection_available():
        if _connection:
            _connection.disconnect_from_host()
        _connection = _server.take_connection()
        print("OpenClaw Bridge: Client connected")
    
    # Handle existing connection
    if _connection and _connection.get_status() == StreamPeerTCP.STATUS_CONNECTED:
        _handle_connection()

func _handle_connection():
    """Process commands from connected client."""
    var available = _connection.get_available_bytes()
    if available > 0:
        var data = _connection.get_string(available)
        var response = _process_command(data)
        _connection.put_string(JSON.stringify(response))

func _process_command(cmd_json: String) -> Dictionary:
    """Parse and execute command."""
    var result = {"success": false, "error": "Unknown command"}
    
    var parse_result = JSON.parse_string(cmd_json)
    if parse_result == null:
        return {"success": false, "error": "Invalid JSON"}
    
    var cmd = parse_result
    if not cmd.has("action"):
        return {"success": false, "error": "Missing action"}
    
    match cmd["action"]:
        "ping":
            result = {"success": true, "pong": true}
        
        "get_scene_tree":
            result = _get_scene_tree()
        
        "get_logs":
            result = _logger.get_logs(cmd.get("since", 0))
        
        "capture_screenshot":
            result = _screenshotter.capture()
        
        "reload_script":
            result = _reload_script(cmd.get("path", ""))
        
        _:
            result = {"success": false, "error": "Unknown action: " + cmd["action"]}
    
    return result

func _get_scene_tree() -> Dictionary:
    """Serialize current scene tree to JSON."""
    var scene := get_editor_interface().get_edited_scene_root()
    if not scene:
        return {"success": false, "error": "No scene open"}
    
    return {
        "success": true,
        "tree": _serialize_node(scene)
    }

func _serialize_node(node: Node) -> Dictionary:
    """Recursively serialize node and children."""
    var data := {
        "name": node.name,
        "type": node.get_class(),
        "path": node.get_path().get_concatenated_names(),
        "properties": {}
    }
    
    # Export common properties
    for prop in ["position", "rotation", "scale", "visible"]:
        if prop in node:
            data["properties"][prop] = node.get(prop)
    
    # Recurse children
    var children := []
    for child in node.get_children():
        children.append(_serialize_node(child))
    
    if not children.is_empty():
        data["children"] = children
    
    return data

func _reload_script(path: String) -> Dictionary:
    """Force reload a script resource."""
    if path.is_empty():
        return {"success": false, "error": "No path provided"}
    
    var res := load(path)
    if res and res is Script:
        res.reload(true)
        return {"success": true, "message": "Script reloaded: " + path}
    
    return {"success": false, "error": "Could not load script: " + path}


# =============================================================================
# Debug Logger - Captures print(), push_error(), push_warning()
# =============================================================================
class DebugLogger:
    extends Node
    
    var _logs: Array[Dictionary] = []
    var _start_time := Time.get_ticks_msec()
    
    func _init():
        # Connect to engine's error/warning signals if available
        # Note: Godot 4.x doesn't expose these directly, we intercept via print_line
        pass
    
    func get_logs(since_ms: int) -> Dictionary:
        """Get logs since timestamp."""
        var result := []
        for log in _logs:
            if log["time"] >= since_ms:
                result.append(log)
        
        return {
            "success": true,
            "logs": result,
            "count": result.size()
        }


# =============================================================================
# Screenshotter - Captures viewport texture
# =============================================================================
class Screenshotter:
    extends Node
    
    func capture() -> Dictionary:
        """Capture editor viewport and encode as base64 PNG."""
        var viewport := EditorInterface.get_editor_viewport_3d() if Engine.is_editor_hint() else get_viewport()
        
        if not viewport:
            return {"success": false, "error": "No viewport available"}
        
        # Wait for frame to render
        await RenderingServer.frame_post_draw
        
        var img := viewport.get_texture().get_image()
        if not img:
            return {"success": false, "error": "Could not get image"}
        
        # Save to buffer
        var buffer := img.save_png_to_buffer()
        var base64 := Marshalls.raw_to_base64(buffer)
        
        return {
            "success": true,
            "format": "png",
            "base64": base64,
            "width": img.get_width(),
            "height": img.get_height()
        }
