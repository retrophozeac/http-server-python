import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    connection, address = server_socket.accept() # wait for client
    data = connection.recv(1024)
    request_data = data.decode().split("\r\n")
    request_line = request_data[0]
    method, target, http_version = request_line.split()

    if target == "/":
        response = b"HTTP/1.1 200 OK\r\n\r\n"
    elif target.startswith("/echo/"):
        value = target.split("/echo/")[1]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}".encode()
    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"

    connection.sendall(response)

if __name__ == "__main__":
    main()
