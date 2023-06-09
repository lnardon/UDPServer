import socket
import pickle
import zlib
import os
import sys
import gc
import hashlib

# Ip do servidor
UDP_IP = "127.0.0.1"
UDP_PORT_TO_SEND = 3072
file_size = os.path.getsize("test.txt")
chunk_size = 300

# Pacote, contendo o número de sequência e o payload
class Packet:
    def __init__(self, seq, payload, checksum, md5):
        self.seq: int = seq
        self.payload: int = payload
        self.checksum = checksum
        self.md5 = md5
    def __str__(self):
        return f"Packet(seq={self.seq}, payload={self.payload}, checksum={self.checksum}, md5={self.md5})"

def checksumCalculator(data):
    checksum = zlib.crc32(data)
    return checksum

def get_obj_size(obj):
    marked = {id(obj)}
    obj_q = [obj]
    sz = 0
    while obj_q:
        sz += sum(map(sys.getsizeof, obj_q))
        all_refr = ((id(o), o) for o in gc.get_referents(*obj_q))
        new_refr = {o_id: o for o_id, o in all_refr if o_id not in marked and not isinstance(o, type)}
        obj_q = new_refr.values()
        marked.update(new_refr.keys())

    return sz

def calculate_md5(file_path):
    md5_hash = hashlib.md5()

    with open(file_path, 'rb') as file:
        chunk = file.read(4096)
        while chunk:
            md5_hash.update(chunk)
            chunk = file.read(4096)

    return md5_hash.hexdigest()

def __init__():
    packets_to_send = 1
    window_size = 16
    with open("test.txt", 'rb') as file:
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0)
        num_chunks = (file_size // 300) 
        packetID = 0
        while packetID < num_chunks + 1:
            print("******** START OF PACKET BATCH ********\n")
            print("Window Size Limit(Slow Start):", window_size , "packets")
            print("Current Window Size:", packets_to_send , "packets")
            if(packets_to_send ** 2 > window_size):
                print("Current Control State: Congestion Avoidance\n")
            else:
                print("Current Control State: Slow Start\n")
            for index in enumerate(range(1, packets_to_send + 1)):
                data = file.read(chunk_size)
                if not data:
                    print("END! No more data to send")
                    break
                packet_to_send = Packet(packetID, data,checksumCalculator(data),"")
                packetID+=1

                sock.sendto(pickle.dumps(packet_to_send), (UDP_IP, UDP_PORT_TO_SEND))
                data, address = sock.recvfrom(4096)
                print("- Client received : ", data.decode('utf-8'),"\n")
            print("======== END OF PACKET BATCH ========", "\n\n\n\n\n")
            if(packets_to_send ** 2 > window_size):
                packets_to_send +=  1;
            else:
                if(packets_to_send == 1):
                    packets_to_send += 1
                else:
                    packets_to_send = packets_to_send ** 2
        sock.sendto(pickle.dumps(Packet(-1, b"DONE", "",calculate_md5("test.txt"))), (UDP_IP, UDP_PORT_TO_SEND))
        sock.close()

__init__()