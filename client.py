import socket
import sys
import time


if len(sys.argv) == 4:
    ip = sys.argv[1]
    port = int(sys.argv[2])
    file = sys.argv[3]
else:
    print("Erro ao iniciar o cliente, execute como: python3 client.py <arg1 server ip> <arg2 port> <arg3 file>")
    exit(1)

#Controle de erro das mensagens
#algoritmo de cálculo de CRC
def calculaCRC(data: bytes):
    poly = 0x8408
    crc = 0xFFFF
    for b in data:
        cur_byte = 0xFF & b
        for _ in range(0, 8):
            if (crc & 0x0001) ^ (cur_byte & 0x0001):
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            cur_byte >>= 1
    crc = (~crc & 0xFFFF)
    crc = (crc << 8) | ((crc >> 8) & 0xFF)
    return crc & 0xFFFF

#teste de CRC
data= 'teste'
crc = calculaCRC(data.encode())
print('CRC: ', crc)

#Pega dados do arquivo para enviar
file = open(file, 'rb')
fileData = file.read()
fileSize = len(fileData)
fileBytes = bytes(fileData) #limite de 300 bytes por pacote
print('Tamanho em bytes: ', len(fileBytes), ' bytes')


#função para quebrar o arquivo em pacotes e guardar em uma lista com hash para identificação do pacote
def chunckFile(file,packetSize):
    chunckedFile = []
    packetIndex = 1
    while True:
        if len(file) > packetSize:
            chunckedFile.append((packetIndex, file[0:packetSize])) #guarda o pacote com o hash
            file = file[packetSize:] #remove os bytes já enviados
            packetIndex += 1 #incrementa o index do pacote
        else:
            chunckedFile.append((packetIndex, file)) #guarda o último pacote com o hash            
            break
    return chunckedFile

#imprime o arquivo quebrado em pacotes
chunckedFile = chunckFile(fileBytes, 300)
#print('Arquivo quebrado em pacotes: ', chunckedFile)

#Função de controle de congestionamento
#Técnicas do TCP: Slow Start, Congestion Avoidance, Fast Retransmit

"""
Slow Start: A técnica Slow Start tem um crescimento exponencial. 
A ideia é que a aplicação comece com a transmissão de um pacote e vá aumentando a taxa de envio (2, 4, 8, 16...) à medida que as confirmações cheguem do destino.
Congestion Avoidance: Esta técnica faz um crescimento linear e é utilizada após o Slow Start.
Fast Retransmit: É uma técnica que faz a retransmissão imediata de um pacote ao receber 3 ACKs duplicados.
"""

def defineControleDeCongestionamento(windowSize):
    if tecnicaAtual == 'Slow Start' and windowSize == 8:
        windowSize = windowSize * 2
        tecnicaAtual = 'Slow Start'
        print(tecnicaAtual)
        print('windowSize: ', windowSize)
    if tecnicaAtual == 'Slow Start':        
        tecnicaAtual = 'Congestion Avoidance'
        print(tecnicaAtual)
        print('windowSize: ', windowSize)
    if tecnicaAtual == 'Congestion Avoidance':
        tecnicaAtual = 'Congestion Avoidance'
        print(tecnicaAtual)
        windowSize = windowSize + 1
        print('windowSize: ', windowSize)
    return windowSize



#define tamanho de janela de congestionamento
windowSize = 1
tecnicaAtual = 'Slow Start'
#Os números de sequência devem começar em zero e ir incrementando de acordo com a quantidade de pacotes que está sendo transmitida
sequencia = 0
#O número do ACK representa o número de sequência mais 1, ou seja, indica o número do pacote que o destino deseja receber.
ack = 0

#função para formatar a mensagem
def formataMesagem(sequencia):
    #seleciona sequencia de acordo com posição no chunckedFile
    pacote = chunckedFile[sequencia]
    print('Pacote: ', pacote)
    tamanhoDoPacote = pacote[0]
    dadosDoPacote = pacote[1]
    #comcatena pacote e dados para checksum
    dadosCheck = str(pacote) + str(dadosDoPacote)
    #print('Dados do pacote: ', dadosDoPacote)
    #Checksum
    checksum = calculaCRC(dadosCheck.encode())
    #formata mensagem
    mensagem = str(tamanhoDoPacote) + '|' + str(checksum) + '|' + str(dadosDoPacote)
    #verifica se pacote é menor que 300 bytes se for adiciona . até completar 300 bytes
    if len(mensagem) < 300:
        mensagem = mensagem + '.' * (300 - len(mensagem))
    return mensagem



#cria o socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while True:
    #implementa sleep para observar comunicação
    #time.sleep(5)

    #Estabelecimento de conexão:
    mensagem = formataMesagem(sequencia)  #mensagem de SYN para estabelecer conexão com o servidor 
    print('Mensagem: ', mensagem)
    print('ip', ip, 'port', port)
    s.sendto(mensagem.encode(), (ip, port)) #envia mensagem de SYN para o servidor
    print('Enviado para o servidor. Sequencia: ' + str(sequencia) + ' ACK: ' + str(ack) + ' Tamanho: ' + str(len(mensagem)) + ' bytes' )


    # Aguarda a resposta ACK do servidor
    ack_data, server_address = s.recvfrom(4096) #recebe mensagem de ACK do servidor
    ack_message = ack_data.decode() #decodifica a mensagem de ACK

    if ack_message == 'ACK': 
        print('ACK recebido do servidor. Conexão estabelecida.', server_address, ' porta: ', port)
        sequencia += 1
        ack = sequencia + 1

    #fecha o socket
    s.close()
