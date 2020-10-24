from os import environ
import logging
from concurrent import futures
from json import dumps

from python.proto_pb2 import *
from python.proto_pb2_grpc import *
from google.protobuf.empty_pb2 import Empty

LOGLEVEL = environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger('Gimulator Mock gRPC Server')


class Servicer(APIServicer):
    def Get(self, request, context):
        logger.debug('Get request received!')
        return Message(Content=dumps([[None] * 3] * 3), Key=None, Meta=None)

    def Put(self, request, context):
        logger.debug('Put request received!')
        return Empty()


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = Servicer()
    add_APIServicer_to_server(servicer, server)

    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('Server is started...')

    server.wait_for_termination()
