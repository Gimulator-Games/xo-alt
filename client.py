from os import environ
import logging

from python.proto_pb2_grpc import *

logger = logging.getLogger('Gimulator Client')


class GimulatorClient:
    def __init__(self):
        self.client_token = client_token = environ['GIMULATOR_TOKEN']
        logger.debug("Client token is " + client_token)
        self.metadata = (('token', client_token),)

        channel = grpc.insecure_channel(environ['GIMULATOR_HOST'])
        self.api = APIStub(channel)
        logger.info("Client connected!")

    def get(self, key):
        return self.api.Get(key, metadata=self.metadata)

    def get_all(self, key):
        return self.api.GetAll(key, metadata=self.metadata)

    def put(self, message):
        return self.api.Put(message, metadata=self.metadata)

    def watch(self, key):
        return self.api.Watch(key, metadata=self.metadata)
