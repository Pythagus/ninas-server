# NINAS server code
__NINAS Is Not Another SMTP__ is a [TLS-SEC](https://tls-sec.github.io/) research project working on a SMTP upgrade including security features against email spoofing, spam, etc. For now, this project is only educational and should not be used for real implementation.

## Dependencies
You can install the dependencies using:
```bash
sudo apt install python3-dnspython
sudo apt install python3-simple-term-menu
```

## Testing
Keys were generated to be able to simulate two hosts `server.host` and `client.host`. Password decrypting keys is `tata`.

To use the testing scripts, you need to add the following virtual hosts in the `/etc/hosts` file (for Linux users):
```bash
127.0.0.2	server.host
127.0.0.3	client.host
```

## Authors
Maud Pennetier, Elies Tali, Damien Molina
