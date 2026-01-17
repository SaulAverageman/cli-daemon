#!/usr/bin/env python3
import socket, sys, json

SOCKET_PATH = "/tmp/authentik_fast.sock"


def main():
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(SOCKET_PATH)
            s.sendall(json.dumps(sys.argv[1:]).encode())

            # Keep reading until the daemon closes the connection
            while True:
                data = s.recv(4096)
                if not data:
                    break
                print(data.decode(), end="", flush=True)
    except ConnectionRefusedError:
        print("Daemon not running. Start it with 'python3 auth_daemon.py'")


if __name__ == "__main__":
    main()
