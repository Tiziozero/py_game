import struct, threading, socket, time


# ---------- u8 (unsigned 8-bit) ----------
def pack_u8(value: int) -> bytes:
    """Pack an unsigned 8-bit integer into bytes."""
    return struct.pack("B", value)

def unpack_u8(data: bytes) -> int:
    """Unpack an unsigned 8-bit integer from bytes."""
    return struct.unpack("B", data)[0]


# ---------- i32 (signed 32-bit) ----------
def pack_i32(value: int, endian: str = "<") -> bytes:
    """
    Pack a signed 32-bit integer into bytes.
    endian = "<" little-endian, ">" big-endian
    """
    return struct.pack(endian + "i", value)

def unpack_i32(data: bytes, endian: str = "<") -> int:
    """
    Unpack a signed 32-bit integer from bytes.
    endian = "<" little-endian, ">" big-endian
    """
    return struct.unpack(endian + "i", data)[0]


HOST = "127.0.0.1"  # localhost
PORT_TCP = 5000         # arbitrary non-privileged port
PORT_UDP = 5000         # arbitrary non-privileged port

def tcp():
# Create TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT_TCP))
        server.listen()

        print(f"Server listening on {HOST}:{PORT_TCP}")
        conn, addr = server.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)   # receive up to 1024 bytes
                if not data:
                    break
                print("Received:", data.decode())
                conn.sendall(data)       # echo back



X_ON = 0b00000001
Y_ON = 0b00000010
# Z_ON = 0b00000100

def parse_data_many(data):
    if len(data) < 4:
        raise Exception("not enough data to parse length")
    all_length = unpack_i32(data[:4])
    data = data[4:]
    if all_length != len(data):
        raise Exception("length of data is not expected length")

    unpacked_data = []
    while len(data) > 0:
        id, x, y, data = parse_data(data,None);
        unpacked_data.append((id,x,y))
    return unpacked_data



def parse_data(data, clients):
    if len(data) < 4:
        raise Exception("not enough data to parse length")

    length = unpack_i32(data[:4])
    data = data[4:]
    if length > len(data):
        print("actual data is less than expected data")
        raise Exception("actual data is less than expected data")

    id,x,y = None,None,None
    actives = unpack_u8(data[:1])
    data = data[1:]
    if actives == 0:
        print("there must be data to parse")
        raise Exception("there must be data to parse")

    id = unpack_i32(data[:4])
    data = data[4:]

    if actives & X_ON:
        x = unpack_i32(data[:4])
        data = data[4:]
    if actives & Y_ON:
        y = unpack_i32(data[:4])
        data = data[4:]

    return id,x,y, data

def pack_data(id, x,y):
    msg = pack_u8(X_ON | Y_ON) + pack_i32(id) +  pack_i32(x) + pack_i32(y)
    return pack_i32(len(msg)) + msg

class ClientData:
    def __init__(self, id, x,y,addr) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.addr = addr
    def comp_addr(self, addr):
        return self.addr[0] == addr[0] and self.addr[1] == addr[1]

class Server:
    def __init__(self) -> None:
        self.clients = {}
        self.client_lock = threading.Lock()
        self.on = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((HOST, PORT_UDP))
        self.socket.settimeout(2.0)

    def getter(self):
        print("Starting initialisation")
        while self.on:
            try:
                data, addr = self.socket.recvfrom(1024)
                try:
                    id, x, y, _ = parse_data(data, self.clients)
                    print(id, x, y)
                except Exception as e:
                    print("Parse error:", e)
                    continue  # skip this iteration if parse fails

                # validate
                client = self.clients.get(id,None)
                if client is None:
                    with self.client_lock:
                        self.clients[id] = ClientData(id,x,y,addr)
                        continue
                elif not client.comp_addr(addr):
                    raise Exception("Addresses don't match")

                # Thread-safe update
                with self.client_lock:
                    self.clients[id].x = x
                    self.clients[id].y = y

            except KeyboardInterrupt:
                self.on=False
                return
            except Exception as e:
                print("Socket error or unexpected:", e)
    def pack_cliets(self):
        data = b''
        for k,v in self.clients.items():
            with self.client_lock:
                data += pack_data(k,v.x,v.y)
        data = pack_i32(len(data)) + data
        return data

    def sender(self):
        last = time.time()
        while self.on:
            now = time.time()
            if now - last >= 0.002:
                last = now
                data = self.pack_cliets()
                for _,v in self.clients.items():
                    self.socket.sendto(data,v.addr)
            else:
                time.sleep(0.0005)  # 0.5 ms


if __name__ == "__main__":
    msg = pack_data(6969, 32,99)
    print(parse_data(msg, None))
    server = Server()

    server.clients[1] = ClientData(1,22,33, ())
    server.clients[2] = ClientData(2,-4,9003, ())
    server.clients[3] = ClientData(3,23234,777, ())
    server.clients[4] = ClientData(4,22,33, ())
    data = server.pack_cliets()
    print(parse_data_many(data))
    server.clients = {}

    getter_thread = threading.Thread(target=Server.getter, args=[server,])
    sender_thread = threading.Thread(target=Server.sender, args=[server,])
    getter_thread.start()
    sender_thread.start()
    getter_thread.join()
    sender_thread.join()
