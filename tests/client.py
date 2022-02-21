import socket
import ssl

ROOT_PATH='/home/dmolina/tls_sec/ninas-server/tests/keys'
hostname = 'server.host'


context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, capath=ROOT_PATH)
context.load_cert_chain(ROOT_PATH + '/client/cert.pem', ROOT_PATH + '/client/key.pem')


# TODO : try/catch ssl.SSLCertVerificationError 
with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    with context.wrap_socket(
        sock,
        server_side=False,
        server_hostname=hostname
    ) as ssock:
        try:
            ssock.connect(('server.host', 8443))
        except ssl.SSLCertVerificationError as e:
            print("Tu es méchant, mais c'est pas grave : " + str(e))

        ssock.send(b"COUCOU TOUA")
        print(ssock.version())