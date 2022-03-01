import socket
import ssl

ROOT_PATH='/home/elies/5A/ninas-server/keys/'
hostname = 'server.host'


context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_cert_chain(ROOT_PATH + 'client.host/cert.pem', ROOT_PATH + '/client.host/key.pem')
context.load_verify_locations(cafile=ROOT_PATH + "demoCA/cacert.pem") 


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
