from ninas.network import NetworkBasePayload, PAYLOAD_RESPONSE_MASK, payloadMustContain, dictToBytes


# Responses identifiers.
RES_HELLO_SERVER = PAYLOAD_RESPONSE_MASK + 10


class Response(NetworkBasePayload):

     # Get a correspondence dictionnary
     # between network payload type and
     # a class name.
    @staticmethod
    def classIdentifierCorrespondence(): 
        return {
            20010: None
        }
        