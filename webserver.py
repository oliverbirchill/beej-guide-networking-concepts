import argparse
import socket
import os

def encode(string):
    return string.encode("ISO-8859-1")

def decode(received_bytes):
    return received_bytes.decode("ISO-8859-1")

def send_404():
    new_socket.sendall(
    encode("HTTP/1.1 404 Not Found\r\n"
        "Content-Length: 13\r\n"
        "Connection: close\r\n"
        "\r\n"
        "404 not found")
    )

def read(filename):
    try:
        with open(filename, "rb") as fp:
            data = fp.read()
            return data
        
    except OSError:
        send_404()

    return None

def verify_absolute_path(file_path, server_root):
    """
    Checks that the resolved file path is within the server root.
    For example, if a client requests /../../../../etc/passwd,
    abspath() resolves the ".." components, allowing us to detect
    that the resulting path is outside the server root.
    """
    absolute_path = os.path.abspath(file_path)

    return absolute_path.startswith(server_root)

def generate_listing(directory):
    paths = os.listdir(directory)
    payload = ""

    for path in paths:
        if path != "webserver.py" and path != "webclient.py" and path != ".git":
            payload += f"<a href='/{os.path.join(directory, path)}'>{path.split(".")[0]}</a><br>"

    return encode(payload)

def parse_request(content, server_root):
    header_data = content.split("\r\n")
    request_line = header_data[0].split()

    if len(request_line) != 3:
        return None
    
    method, get_path, protocol = request_line

    absolute_path = os.path.join(server_root, get_path[1:]) # Removes preceding "/" from get path
    relative_path = get_path[1:]

    return method, get_path, protocol, relative_path, absolute_path

def make_headers(content_type, payload):
    return encode(
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(payload)}\r\n"
        f"Connection: close\r\n\r\n"
        ) 

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=28333)
args = parser.parse_args()

server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", args.port))
server_socket.listen()
server_root = os.path.abspath(".")

mime_dict = {
    ".txt": "text/plain",
    ".html": "text/html",
    ".ico": "image/x-icon",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".pdf": "application/pdf"
}

while True:
    new_socket, address = server_socket.accept()
    content = decode(new_socket.recv(4096))

    request = parse_request(content, server_root)

    if request is None:
        new_socket.close()
        continue

    method, get_path, protocol, relative_path, absolute_path = request

    if not verify_absolute_path(absolute_path, server_root):
        send_404()
        new_socket.close()
        continue

    if get_path == "/":
        payload = generate_listing(".")
        content_type = "text/html"
    elif os.path.isdir(relative_path):
        payload = generate_listing(relative_path)
        content_type = "text/html"
    else:
        content_type = mime_dict.get(os.path.splitext(get_path)[1])
        payload = read(relative_path)

    if payload is None:
        new_socket.close()
        continue

    print(
        f"New connection from IP Address {address[0]}:{address[1]}\r\n"
        f"HTTP Method : {method}\r\n"
        f"Protocol : {protocol}\r\n"
        f"Content type: {content_type}\r\n"
    )

    headers = make_headers(content_type, payload)
    new_socket.sendall(headers + payload)
    new_socket.close()
    