import socket
import os
import json
import sys
import huge_cli  # Pre-loaded

SOCKET_PATH = "/tmp/authentik_fast.sock"


# A helper class to redirect print() to the socket
class SocketWriter:
    def __init__(self, conn):
        self.conn = conn

    def write(self, data):
        # Handle both string and bytes
        if data:
            if isinstance(data, bytes):
                self.conn.sendall(data)
            else:
                self.conn.sendall(data.encode())

    def flush(self):
        pass


def start_daemon():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    os.chmod(SOCKET_PATH, 0o666)
    server.listen(5)

    print("Daemon: Hot and listening...")
    while True:
        try:
            conn, _ = server.accept()
            while True:  # Keep connection open for multiple commands
                raw_data = conn.recv(4096).decode()
                if not raw_data:
                    break  # Change from 'continue' to 'break' to handle client disconnections

                args = json.loads(raw_data)
                sys.argv = ["huge_cli.py"] + args

                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = sys.stderr = SocketWriter(conn)

                try:
                    huge_cli.app(
                        standalone_mode=False
                    )  # Change from 'huge_cli.main()' to prevent typer from exiting
                except Exception as e:
                    print(f"Command Error: {e}\n")
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    conn.close()
        except Exception as e:
            print(f"Daemon Error: {e}\n")
        finally:
            conn.close()


if __name__ == "__main__":
    start_daemon()
