import socket
import sys

if len(sys.argv) == 3:
    ip = sys.argv[1]
    port = int(sys.argv[2])
else:
    exit(1)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (ip, port)
s.bind(server_address)

while True:
    print("####### Server is listening on PORT", port, "#######")
    data, address = s.recvfrom(4096)
    
    # Envia ACK para o cliente
    ack_message = 'ACK'
    s.sendto(ack_message.encode(), address)
    print('ACK enviado para o cliente. Conexão estabelecida.', server_address, ack_message, port)


    # close the socket
    s.close()

