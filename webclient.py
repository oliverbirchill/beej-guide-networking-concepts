import argparse
import socket

def encode(string):
    return string.encode("ISO-8859-1")

def decode(received_bytes):
    return received_bytes.decode("ISO-8859-1")

def build_request(host, port, payload, content_type, method):
    return f"{method} / HTTP/1.1\r\nHost: {host}:{port}\r\nContent-Type: {content_type}\r\nContent-Length: {len(encode(payload))}\r\nConnection: close\r\n\r\n{payload}"

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("host")
    parser.add_argument("port", type=int, nargs="?", default=80)
    parser.add_argument("--payload", default="")
    parser.add_argument("--content_type", default="text/plain")
    parser.add_argument("--method", default="GET")

    args = parser.parse_args()
    return args


args = parse_args()
client_socket = socket.socket()
client_socket.connect((args.host, args.port))

request = build_request(args.host, args.port, args.payload, args.content_type, args.method)
client_socket.sendall(encode(request))

response = client_socket.recv(4096)
while response:
    print(decode(response))
    response = client_socket.recv(4096)

client_socket.close()
