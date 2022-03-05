PORT=8000

# The NINAS receiving server.
ninas_server:
	@python3 server.py server.host ${PORT} || true

# The NINAS sending server.
ninas_client:
	@python3 server.py client.host ${PORT} || true

# The client interface for sending emails.
client:
	@python3 client_wrapper.py ${PORT} || true

# Clean the repository.
clean:
	@find samples -name "*.mail" -exec rm {} \;
