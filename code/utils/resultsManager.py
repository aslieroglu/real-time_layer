"""
Author: Saurabh
Date:02.02.24
"""
import socket
import json
import yaml
from psychopy import logging
class resultsServerHandler(object):
    def __init__(self,host="127.0.0.1",port=5558):
        self.host = host
        self.port = port
        logging.debug(f"Created the {self.__class__.__name__} object")

    def get_result(self,vol_id):
        """
        returns:
        None if something fails
        Dictionary of response of pyneal if socket connects
        """
        resp = None
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
            #request the result server for the volume in format dddd
            request = f"{vol_id:0>4}"
            logging.debug(f"Requesting volume {request}")
            client_socket.sendall(request.encode())
            resp = b''
            while True:
                server_response = client_socket.recv(4096)
                if server_response:
                    resp += server_response
                else: 
                    break
            resp = json.loads(resp.decode())
        except socket.error as e:
            logging.error(f"Problem at socket with results server-> {e}")
        finally:
            client_socket.close()

        return resp


    def test_results_server(self):
        """
        Retuns:
         None if socket doesnt connect
         Dict of response for volume id 9999 if socket connects
        """
        logging.info("Testing connection to the results server")
        test_resp = self.get_result(9999)
        if test_resp:
            logging.info("Result server found and connected OK")
            return True
        else:
            logging.warning("No results server found. What's the point in carrying on")
            return False
        



