import socket
import sys

# 1 - Server IP
# 2 - Server PORT
if len(sys.argv) == 3:
    ip = sys.argv[1]
    port = int(sys.argv[2])
else:
    exit(1)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (ip, port)
s.bind(server_address)

while True:
    print("####### Server is listening on PORT ${port} #######")
    data, address = s.recvfrom(4096)
    print("\n\n 2. Server received: ", data.decode('utf-8'), "\n\n")
    send_data = input("Type some text to send => ")
    s.sendto(send_data.encode('utf-8'), address)
    print("\n\n 1. Server sent : ", send_data,"\n\n")
