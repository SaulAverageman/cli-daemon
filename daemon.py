import socket
import os
import json
import sys
import huge_cli # Pre-loaded

SOCKET_PATH = "/tmp/authentik_fast.sock"

# A helper class to redirect print() to the socket
class SocketWriter:
    def __init__(self, conn):
        self.conn = conn
    def write(self, data):
        # Send everything printed back to the CLI client
        if data:
            self.conn.sendall(data.encode())
    def flush(self):
        pass # Required for file-like objects

def start_daemon():
    if os.path.exists(SOCKET_PATH): os.remove(SOCKET_PATH)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    os.chmod(SOCKET_PATH, 0o666)
    server.listen(5)
    
    print("Daemon: Hot and listening...")

    while True:
        conn, _ = server.accept()
        try:
            raw_data = conn.recv(4096).decode()
            if not raw_data: continue
            
            args = json.loads(raw_data)
            sys.argv = ["huge_cli.py"] + args

            # REDIRECT OUTPUT HERE
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = sys.stderr = SocketWriter(conn)

            try:
                huge_cli.main()
            finally:
                # Always restore the terminal output for the daemon
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
        except Exception as e:
            conn.sendall(f"Daemon Error: {e}\n".encode())
        finally:
            conn.close()

if __name__ == "__main__":
    start_daemon()