import socket
import threading
import sys

def handle_client(connection):
    try:
        data = connection.recv(1024)
        request_data = data.decode().split("\r\n")
        request_line = request_data[0]
        print(request_line)
        method, target, http_version = request_line.split()
        if method == "GET":
            if target == "/":
                response = b"HTTP/1.1 200 OK\r\n\r\n"
            elif target.startswith("/echo/"):
                value = target.split("/echo/")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}".encode()
            elif target == "/user-agent":
                request_line2 = request_data[2]
                print(request_line2)
                header, value1 = request_line2.split(":", 1)
                header = header.strip()
                value1 = value1.strip()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value1)}\r\n\r\n{value1}".encode()
            elif target.startswith("/files/"):
                filename = target.split("/files/")[1]
                directory = sys.argv[2]
                print(filename)
                try:
                    with open(f"/{directory}/{filename}", "r") as file:
                        content = file.read()
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n{content}".encode()
                except FileNotFoundError:
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        elif method == "POST":
            if target.startswith("/files/"):
                filename = target.split("/files/")[1]
                directory = sys.argv[2]
                body = request_data[-1]
                with open(f"/{directory}/{filename}", "w") as file:
                    file.write(body)
                response = b"HTTP/1.1 201 Created\r\n\r\n"
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"    

        connection.sendall(response)
    finally:
        connection.close()


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server is running on port 4221...")

    while True:
        connection, address = server_socket.accept()  # Wait for a client
        print(f"Connection established with {address}")
        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(connection,))
        client_thread.start()


if __name__ == "__main__":
    main()