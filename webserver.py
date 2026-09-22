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
        
    except:
        new_socket.sendall(
            encode("HTTP/1.1 404 Not Found\r\n"
                "Content-Length: 13\r\n"
                "Connection: close\r\n"
                "\r\n"
                "404 not found")
            )

    return None


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
}

while True:
    new_socket, address = server_socket.accept()
    content = decode(new_socket.recv(4096))
    header_data = content.split("\r\n")
    method, full_path, protocol = header_data[0].split(" ")
    filename = os.path.split(full_path)[-1]
    content_type = mime_dict.get(os.path.splitext(full_path)[1])
    payload = read(filename)

    print(f"New connection from IP Address {address[0]}:{address[1]}")
    print(f"HTTP Method : {method}")
    print(f"File : {filename}")
    print(f"Protocol : {protocol}")
    print(f"Content type: {content_type}")

    if payload is None:
        new_socket.close()
        continue

    new_socket.sendall(encode(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(payload)}\r\nConnection: close\r\n\r\n") + payload)
    new_socket.close()
    