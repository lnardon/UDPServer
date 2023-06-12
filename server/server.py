import socket
import pickle
import time
import zlib
import hashlib

# Ip do servidor
IP = "127.0.0.1"
PORT = 3072


def checksumCalculator(data):
 checksum = zlib.crc32(data)
 return checksum

def verifyChecksum(originalChecksum, packet):
    return originalChecksum == checksumCalculator(packet)

def calculate_md5(file_path):
    md5_hash = hashlib.md5()

    with open(file_path, 'rb') as file:
        chunk = file.read(4096)
        while chunk:
            md5_hash.update(chunk)
            chunk = file.read(4096)

    return md5_hash.hexdigest()

class Packet:
    def __init__(self, seq, payload):
        self.seq = seq
        self.payload = payload
        self.checksum = ""
        self.md5 = ""
    def __str__(self):
            return f"Packet(seq={self.seq}, payload={self.payload})"


writer = open("test_received.txt", "wb")

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
sock.bind((IP,PORT))


current_data: bytes = b''
while True:
    data, addr = sock.recvfrom(4096)
    current_data += data
    parsedPacket = pickle.loads(data)
    if(parsedPacket.payload == b"DONE"):
        print("END OF EXEC! No more data to receive")
        data = pickle.loads(current_data)
        writer.write(current_data)
        writer.close()
        print(parsedPacket.md5, calculate_md5("test_received.txt"))
        if (parsedPacket.md5 == calculate_md5("test_received.txt")):
            print("MD5 CHECKSUM = File is NOT CORRUPTED!")
        sock.close()
        break
    else:
        isPacketValid = verifyChecksum(parsedPacket.checksum, parsedPacket.payload)
        if isPacketValid:
            print("*** CHECKSUM PACKET = Packet is NOT CORRUPTED! ***\n")
            print(f"Received packet {parsedPacket.seq}:\n%s"%str(parsedPacket) + "\n\n")
            sock.sendto(f"ACK-{parsedPacket.seq + 1}".encode(), addr)
        else:
            print("!!!!! CHECKSUM PACKET = Packet IS CORRUPTED !!!!!\n\n")
        # sleep
        time.sleep(0.1)
