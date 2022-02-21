from ninas.network import createNetworkInstance
import socket
import json

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 8090))
serversocket.listen(5) # become a server socket, maximum 5 connections

while True:
    connection, address = serversocket.accept()
    buf = connection.recv(256)
    if len(buf) > 0:
        request = createNetworkInstance(connection, json.loads(buf))
        print(type(request))
        print(request)
        break
