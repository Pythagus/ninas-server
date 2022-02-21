import socket
import ssl

ROOT_PATH='/home/dmolina/tls_sec/ninas-server/tests/keys'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, capath=ROOT_PATH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(ROOT_PATH + '/server/cert.pem', ROOT_PATH + '/server/key.pem')
#context.load_verify_locations(capath=ROOT_PATH)

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