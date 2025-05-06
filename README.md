# HTTP Server in Python

A simple HTTP server implementation in Python, created as part of the [Codecrafters](https://codecrafters.io/) challenge.

## Overview

This project implements a basic HTTP/1.1 server from scratch in Python, supporting various HTTP features including request parsing, response generation, file operations, and more.

## Features

- **Basic HTTP Routing**:
  - `/` - Returns a 200 OK response
  - `/echo/<message>` - Echoes back the message in the response body
  - `/user-agent` - Returns the User-Agent header from the request
  - `/files/<filename>` - Handles file operations

- **HTTP Features**:
  - Multithreaded request handling
  - Gzip compression support
  - Connection management (keep-alive/close)
  - File operations (GET to retrieve, POST to create)
  - HTTP headers parsing and generation

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pipenv install
   ```

## Running the Server

Use the provided script to run the server:

```bash
./your_program.sh
```

To specify a directory for file operations:

```bash
./your_program.sh --directory /path/to/directory
```

## Project Structure

- `app/main.py` - Main server implementation
- `your_program.sh` - Script to run the server locally
- `Pipfile` & `Pipfile.lock` - Dependency management
- `codecrafters.yml` - Configuration for the Codecrafters platform

## Implementation Details

The server is implemented with the following components:

- `HttpRequest` - Parses incoming HTTP requests
- `HttpResponse` - Generates HTTP responses
- `FileHandler` - Manages file operations
- `HttpServer` - Core server implementation that handles connections and routes requests
