from os import environ
import logging

from python.proto_pb2_grpc import *

logger = logging.getLogger('Gimulator Client')


class GimulatorClient(APIStub):
    def __init__(self):
        self.client_token = client_token = environ['TOKEN']
        logger.debug("Client token is " + client_token)
        self.metadata = (('token', client_token),)

        channel = grpc.insecure_channel(environ['GIMULATOR_HOST'])
        super().__init__(channel)
        logger.info("Client connected!")

    def Get(self, key):
        return super().Get(key, metadata=self.metadata)

    def Put(self, message):
        return super().Put(message, metadata=self.metadata)

    def Watch(self, key):
        return super().Watch(key, metadata=self.metadata)
