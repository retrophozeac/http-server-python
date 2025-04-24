import socket
import threading
import sys
import os
from pathlib import Path


class HttpRequest:
    def __init__(self, request):
        self.request = request
        self.method = None
        self.path = None
        self.headers = {}
        self.body = None
        self._parse_request()

    def _parse_request(self):
        if not self.request:
            return
        lines = self.request.split("\r\n")
        request_line = lines[0].split()
        if len(request_line) > 2:
            self.method = request_line[0]
            self.path = request_line[1]
        for line in lines[1:]:
            if not line:
                break
            elif ":" in line:
                header, value = line.split(": ", 1)
                self.headers[header] = value.strip()
        body_start_index = self.request.find("\r\n\r\n")
        if body_start_index != -1:
            self.body = self.request[body_start_index + 4:]

    def get_header(self, name):
        return self.headers.get(name)


class HttpResponse:
    def __init__(self, status_code: int = 200, content: str = "", content_type: str = "text/plain"):
        self.status_code = status_code
        self.content = content
        self.content_type = content_type
        self.headers = {}

    def add_header(self, name, value):
        self.headers[name] = value

    def _get_status_text(self):
        status_text = {
            200: "OK",
            201: "Created",
            404: "Not Found",
            500: "Internal Server Error"
        }
        return status_text.get(self.status_code)

    def create_response(self):
        response_line = f"HTTP/1.1 {self.status_code} {self._get_status_text()}\r\n"
        headers = (
            f"Content-Type: {self.content_type}\r\n"
            f"Content-Length: {len(self.content)}\r\n"
        )
        for name, value in self.headers.items():
            headers += f"{name}: {value}\r\n"
        return f"{response_line}{headers}\r\n{self.content}".encode("utf-8")


class FileHandler:

    def __init__(self, base_directory: str = None):
        self.base_directory = base_directory

    def set_base_directory(self, directory):
        self.base_directory = directory

    def get_file_path(self, url_path):

        if not url_path.startswith("/files/") or not self.base_directory:
            return None
        filename = os.path.basename(url_path.split("/files/")[1])
        return os.path.join(self.base_directory, filename)

    def read_file(self, path):

        if not os.path.isfile(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    def write_file(self, path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


class HttpServer:

    def __init__(self, host: str = "localhost", port: int = 4221):
        self.host = host
        self.port = port
        self.file_handler = FileHandler()
        self.server_socket = socket.create_server((self.host, self.port))
        self.running = False

    def set_directory(self, directory):
        self.file_handler.set_base_directory(directory)

    def start(self):

        self.running = True
        print(f"Server running on {self.host}:{self.port}")

        while self.running:
            try:
                connection, address = self.server_socket.accept()
                thread = threading.Thread(
                    target=self._handle_connection, args=(connection,)
                )
                thread.start()
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        self.running = False
        self.server_socket.close()
        print("server stopped")

    def _handle_connection(self, connection):
        try:
            while True:
                data = connection.recv(1024).decode("utf-8")
                if not data:
                    return
                request = HttpRequest(data)
                connection_header = request.get_header("Connection")
                encoding_header = request.get_header("Accept-Encoding")
                response = self._route_request(request)
                if encoding_header and "gzip" in encoding_header:
                    response.add_header("Content-Encoding", "gzip")
                if connection_header and connection_header.lower() == "close":
                    response.add_header("Connection","close")
                    connection.sendall(response.create_response())
                    break
                connection.sendall(response.create_response())
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            connection.close()

    def _route_request(self, request):

        if not request.method or not request.path:
            return HttpResponse(400, "Bad Request")
        if request.path == "/":
            return HttpResponse(200)
        elif request.path.startswith("/echo/"):
            content = request.path.split("/echo/")[1]
            return HttpResponse(200, content)
        elif request.path.startswith("/user-agent"):
            user_agent = request.get_header("User-Agent") or ""
            return HttpResponse(200, user_agent)
        elif request.path.startswith("/files/"):
            return self._handle_file_request(request)
        else:
            return HttpResponse(404)

    def _handle_file_request(self, request):
        file_path = self.file_handler.get_file_path(request.path)
        if not file_path:
            return HttpResponse(404)
        if request.method == "GET":
            file_content = self.file_handler.read_file(file_path)
            if file_content:
                return HttpResponse(200, file_content.decode(), "application/octet-stream")
            return HttpResponse(404)
        elif request.method == "POST":
            if not request.body:
                return HttpResponse(400, "Bad Request")
            self.file_handler.write_file(file_path, request.body)
            return HttpResponse(201)
        return HttpResponse(404)


if __name__ == "__main__":
    server = HttpServer()

    if len(sys.argv) > 2 and sys.argv[1] == "--directory":
        server.set_directory(sys.argv[2])

    server.start()
