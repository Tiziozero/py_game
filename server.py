import socket

HOST = "127.0.0.1"  # localhost
PORT = 5000         # arbitrary non-privileged port

# Create TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server listening on {HOST}:{PORT}")
    conn, addr = server.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)   # receive up to 1024 bytes
            if not data:
                break
            print("Received:", data.decode())
            conn.sendall(data)       # echo back
