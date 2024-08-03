import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for port in range(1, 8081):
    print(f"testing {port}")
    res = client_socket.connect_ex(('10.41.60.157',port))
    if res == 0:
        print(port)
