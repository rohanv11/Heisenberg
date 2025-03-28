import logging
import sys
import socket
import subprocess

from app.config.settings import DEBUG_PORT


logger = logging.getLogger(__name__)

def is_port_in_use(port):
    """Check if a given port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0

def setup_debugger():
    """
    Conditionally sets up the debugger if DEBUG_MODE is enabled.
    This function will install debugpy if needed and configure the debugger.
    """
    logger.info(f"Debug mode enabled on port {DEBUG_PORT}")

    # Check if debugpy is installed
    try:
        import debugpy
        logger.info("debugpy is already installed")
    except ImportError:
        logger.info("Installing debugpy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "debugpy"])
        import debugpy
    
    # Check if the debug port is already in use
    if is_port_in_use(DEBUG_PORT):
        logger.warning(f"Port {DEBUG_PORT} is already in use. Debugger might already be running.")
        return  # Skip re-initializing debugpy to prevent crashes

    # Configure debugpy
    logger.info(f"Starting debugger on port {DEBUG_PORT}, waiting for client connection...")
    debugpy.listen(("0.0.0.0", DEBUG_PORT))
    debugpy.wait_for_client()  # Pause execution until VSCode connects
    logger.info("Debugger client connected")

