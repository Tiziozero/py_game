import socket
from server import *


SERVER_ADDRESS = (HOST, PORT_UDP)
class DataSender:
    def __init__(self, id) -> None:
        self.id = id
        self.socket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(2.0)
        self.open = True
        self.clients = {}
        self.client_lock = threading.Lock()
    def send_data(self, x, y):
        try:
            data = pack_data(self.id,int(x),int(y));
            self.socket.sendto(data, SERVER_ADDRESS)
        except Exception as e:
            print(e)
            self.open = False
    def data_getter(self):
        try:
            data, addr = self.socket.recvfrom(1024)
            if addr[0] != SERVER_ADDRESS[0] and addr[1] != SERVER_ADDRESS[1]:
                raise Exception("Recevied data from unknown sourse")
            unpacked_data = parse_data_many(data)
            print(unpacked_data)
            for id,x,y in unpacked_data:
                with self.client_lock:
                    if self.clients.get(id, None) is None:
                        self.clients[id] = ClientData(id,0,0,None)
                    if x is not None:
                        self.clients[id].x = x
                    if y is not None:
                        self.clients[id].y = y
            return unpacked_data
        except socket.timeout:
            print("No data received within timeout")
            return None
        except Exception as e:
            print(e)
            self.open = False

