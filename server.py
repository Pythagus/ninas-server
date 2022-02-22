from ninas.network import createNetworkInstance, NetworkPacket, receiveBytes
import socketserver
import threading
import json
import sys


# Main class used to handle
# every incoming payload like
# requests and responses. This
# is thread-programming.
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("CONNECTION FROM : " + str(self.client_address))
        sock = self.request

        while True:
            buf  = receiveBytes(sock, NetworkPacket.SIZE_LENGTH, b"")
            size = int(buf)
            buf  = receiveBytes(sock, size, buf)

            packet = NetworkPacket.unserialize(buf)
            request = createNetworkInstance(sock, json.loads(packet.payload))
            print(request)
            request.handle()


# Current server data.
HOST, PORT = "server.host", int(sys.argv[1])

# Base threaded server class.
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

# Create the server
with ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler) as server:
    ip, port = server.server_address

    # Start a thread with the server
    # That thread will then start one more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    
    print("Server loop running in thread:", server_thread.name)
    while True: pass
