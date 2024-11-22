import socket
import json

#for port in range(1, 8081):
#    print(f"testing {port}")
#    res = client_socket.connect_ex(('10.41.60.157',port))
#    if res == 0:
#        print(port)
for port in [5555,5556,5557,5558]:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"trying port {port}")
    try:
        client_socket.connect(('10.41.60.157', port))
        #request the result server for the volume in format dddd
        request = "9999"
        print(f"Requesting volume {request}")
        client_socket.sendall(request.encode())
        resp = b''
        while True:
            server_response = client_socket.recv(2048)
            if server_response:
                resp += server_response
            else: 
                break
            resp = json.loads(resp.decode())
            print(resp)
    except socket.error as e:
        print(f"Problem at socket with results server-> {e}")
    finally:
        client_socket.close()

print("Done")


