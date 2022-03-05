NINAS_PORT=8000
IMAP_PORT=8001

# The NINAS receiving server.
ninas_server:
	@python3 server.py server.host ${NINAS_PORT} ${IMAP_PORT} || true

# The NINAS sending server.
ninas_client:
	@python3 server.py client.host ${NINAS_PORT} ${IMAP_PORT} || true

# The client interface for sending emails.
client:
	@python3 client_wrapper.py ${NINAS_PORT} ${IMAP_PORT} || true

# Clean the repository.
clean:
	@find samples -name "*.mail" -exec rm {} \;
