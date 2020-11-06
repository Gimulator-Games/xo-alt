from os import environ
import logging

from python.proto_pb2_grpc import *
from python.proto_pb2 import *
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

logger = logging.getLogger('Gimulator Client')


class GimulatorClient:
    client_token = None
    channel = None
    api = None
    metadata = None

    def __init__(self):
        self.client_token = client_token = environ['GIMULATOR_TOKEN']
        logger.debug("Client token is " + client_token)
        self.metadata = (('token', client_token),)

        self.channel = grpc.insecure_channel(environ['GIMULATOR_HOST'])
        self.api = MessageAPIStub(self.channel)
        logger.info("Client connected!")

    def Get(self, key: Key):
        return self.api.Get(key, metadata=self.metadata)

    def GetAll(self, key: Key):
        return self.api.GetAll(key, metadata=self.metadata)

    def Put(self, message: Message):
        return self.api.Put(message, metadata=self.metadata)

    def Delete(self, message: Message):
        return self.api.Delete(message, metadata=self.metadata)

    def DeleteAll(self, message: Message):
        return self.api.DeleteAll(message, metadata=self.metadata)

    def Watch(self, key: Key):
        return self.api.Watch(key, metadata=self.metadata)


class DirectorClient(GimulatorClient):
    director_api = None

    def __init__(self):
        super().__init__()
        self.director_api = DirectorAPIStub(self.channel)

    def GetActors(self):
        empty = google_dot_protobuf_dot_empty__pb2.Empty()
        return self.director_api.GetActors(empty, metadata=self.metadata)

    def PutResult(self, result: Result):
        return self.director_api.PutResult(result, metadata=self.metadata)


class OperatorClient(GimulatorClient):
    operator_api = None

    def __init__(self):
        super().__init__()
        self.operator_api = OperatorAPIStub(self.channel)

    def SetUserStatus(self, report: Report):
        return self.operator_api.SetUserStatus(report, metadata=self.metadata)


class ActorClient(GimulatorClient):
    actor_api = None

    def __init__(self):
        super().__init__()
        self.actor_api = UserAPIStub(self.channel)

    def ImReady(self):
        empty = google_dot_protobuf_dot_empty__pb2.Empty()
        return self.actor_api.ImReady(empty, metadata=self.metadata)
