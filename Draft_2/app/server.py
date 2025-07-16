# server.py
import paramiko
import socket

def start_ssh_server():
    # Placeholder: Load SSH keys and config
    host_key = None  # TODO: Load host key from config

    # Placeholder: Set up server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 2200))
    server_socket.listen(100)
    print("SSH server listening on port 2200...")

    while True:
        client, addr = server_socket.accept()
        print(f"Connection from {addr}")
        # Placeholder: Initialize SSH transport
        transport = paramiko.Transport(client)
        # TODO: Add authentication and session handling
        transport.close()

if __name__ == "__main__":
    start_ssh_server()