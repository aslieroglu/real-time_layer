import os
import socket
import subprocess

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def kill_processes_on_port(port):
    """Find and kill processes using a specific port."""
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-t"], capture_output=True, text=True
        )
        pids = result.stdout.strip().split("\n")
        
        if pids and pids[0]:
            print(f"Found processes on port {port}: {pids}")
            for pid in pids:
                os.system(f"kill -9 {pid}")
            print(f"Successfully killed all processes on port {port}.")
        else:
            print(f"No processes found on port {port}.")
    except Exception as e:
        print(f"Error checking port {port}: {e}")

def cleanup_port(port):
    """Ensure the given port is free before use."""
    if is_port_in_use(port):
        print(f"Port {port} is in use. Cleaning up...")
        kill_processes_on_port(port)
    else:
        print(f"Port {port} is already free.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python clean_port.py <port>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    cleanup_port(port)
