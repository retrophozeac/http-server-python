import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    connection, address = server_socket.accept() # wait for client
    data = connection.recv(1024)
    request_line = data.decode().splitlines()[0]
    method, path, _ = request_line.split()
    if path == "/":
        connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        connection.close()
    else:
        connection.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
        connection.close()
        
if __name__ == "__main__":
    main()
