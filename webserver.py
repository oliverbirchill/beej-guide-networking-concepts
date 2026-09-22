import argparse
import socket

def encode(string):
    return string.encode("ISO-8859-1")

def decode(received_bytes):
    return received_bytes.decode("ISO-8859-1")


parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=28333)

args = parser.parse_args()

server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", args.port))
server_socket.listen()

while True:
    new_socket, address = server_socket.accept()
    content = decode(new_socket.recv(4096))
    method = content.split(" ")[0]
    payload = content.split("\r\n\r\n", 1)[1]

    print(f"New connection from IP Address {address[0]}:{address[1]}")
    print(f"HTTP Method : {method}")
    if payload:
        print(f"Payload : {payload}")

    new_socket.sendall(encode("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 6\r\nConnection: close\r\n\r\nHello!"))
    new_socket.close()
    