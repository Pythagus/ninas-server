import socket
import ssl

ROOT_PATH='/home/elies/5A/ninas-server/keys/'


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(ROOT_PATH + 'server.host/cert.pem', ROOT_PATH + 'server.host/key.pem')
context.load_verify_locations(cafile=ROOT_PATH + "demoCA/cacert.pem") 

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(('server.host', 8443))
    sock.listen(5)
    with context.wrap_socket(sock, server_side=True) as ssock:
        try:
            conn, addr = ssock.accept()
            buf = ""
            while len(buf) <= 0:
                buf = conn.recv(64)
                print("Received from " + str(addr) + " : " + str(buf))
        except ssl.SSLError as e:
            print("C'est pêté : " + str(e))

print("Server terminated.")
