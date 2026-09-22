import argparse
import socket
import os

def encode(string):
    return string.encode("ISO-8859-1")

def decode(received_bytes):
    return received_bytes.decode("ISO-8859-1")

def read(filename):
    try:
        with open(filename, "rb") as fp:
            data = fp.read()
            return data
        
    except OSError:
        new_socket.sendall(
            encode("HTTP/1.1 404 Not Found\r\n"
                "Content-Length: 13\r\n"
                "Connection: close\r\n"
                "\r\n"
                "404 not found")
            )

    return None

def make_index():
    paths = list(os.listdir())
    payload = ""

    for path in paths:
        payload += f"<a href='{path}'>{path}</a><br>"

    return payload

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=28333)

args = parser.parse_args()

server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", args.port))
server_socket.listen()

mime_dict = {
    ".txt": "text/plain",
    ".html": "text/html",
    ".ico": "image/x-icon",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeeg",
    ".pdf": "application/pdf"
}

while True:
    new_socket, address = server_socket.accept()
    content = decode(new_socket.recv(4096))
    header_data = content.split("\r\n")
    method, full_path, protocol = header_data[0].split(" ")
    filename = os.path.split(full_path)[-1]

    if full_path == "/":
        payload = make_index()
        filename = "index.txt"
        content_type = "text/html"
    else:
        content_type = mime_dict.get(os.path.splitext(full_path)[1])
        payload = decode(read(filename))

    if payload is None:
        new_socket.close()
        continue

    print(
        f"New connection from IP Address {address[0]}:{address[1]}\r\n"
        f"HTTP Method : {method}\r\n"
        f"File : {filename}\r\n"
        f"Protocol : {protocol}\r\n"
        f"Content type: {content_type}\r\n"
        )

    new_socket.sendall(encode(f"HTTP/1.1 200 OK\r\n"
                              f"Content-Type: {content_type}\r\n"
                              f"Content-Length: {len(payload)}\r\n"
                              f"Connection: close\r\n\r\n{payload}") 
                              )

    new_socket.close()
    