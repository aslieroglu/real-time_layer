import socket
import json
import time

port = 5555
TR = 2 

for vol_id in range(11):
    time.sleep(TR)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('10.41.60.157', port))
        #request the result server for the volume in format dddd
        request = f"{vol_id:0>4}"
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
