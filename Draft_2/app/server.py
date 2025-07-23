# server.py
import paramiko
import socket

def start_ssh_server():
    # Placeholder: Load SSH keys and config
    # Load host key from config
    try:
        with open(os.path.join(os.path.dirname(__file__), "../config/host_key.txt"), "r") as f:
            host_key_data = f.read()
        host_key = paramiko.RSAKey(file_obj=open(os.path.join(os.path.dirname(__file__), "../config/host_key.txt")))
    except Exception as e:
        print(f"Failed to load host key: {e}")
        return

    # Placeholder: Set up server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 2200))
    server_socket.listen(100)
    print("SSH server listening on port 2200...")

    while True:
        try:
            client, addr = server_socket.accept()
        except Exception as e:
            print(f"Socket accept error: {e}")
            continue
        print(f"Connection from {addr}")
        try:
            transport = paramiko.Transport(client)
            transport.add_server_key(host_key)
            # TODO: Implement secure SSH authentication, session timeout, and logging
            # Placeholder: Accept session, handle errors
            try:
                transport.start_server()
            except Exception as e:
                print(f"SSH transport error: {e}")
            finally:
                transport.close()
        except Exception as e:
            print(f"Transport setup error: {e}")
            client.close()

if __name__ == "__main__":
    start_ssh_server()