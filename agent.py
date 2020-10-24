from os import environ
import logging
from time import sleep
import random
import string
from json import loads, dumps

from python.proto_pb2 import *
from python.proto_pb2_grpc import *

from client import GimulatorClient

LOGLEVEL = environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger('Gimulator Agent SDK')

agent_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5))


class Agent:
    def react(self, world: dict) -> list:
        action = [None, None]

        # TODO do something with world and populate action
        action[0] = int(input())
        action[1] = int(input())

        return action


if __name__ == '__main__':
    logger.info('Agent name is "%s"' % agent_name)
    agent = Agent()

    client = GimulatorClient()

    logger.debug("Registering agent...")
    client.put(
        Message(Content='agent-' + agent_name, Key=Key(Type='register', Name='agent-' + agent_name, Namespace='XO-namespace')))

    while True:
        sleep(1)
        logger.debug("Requesting world...")
        try:
            response = client.get(Key(Type='world', Name='judge', Namespace='XO-namespace'))
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                continue
            raise e
        logger.debug("World received: " + response.Content)

        logger.debug("Agent is reacting...")
        action = dumps(agent.react(loads(response.Content)))
        logger.debug("Action is ready: " + action)

        client.put(Message(Content=action, Key=Key(Type='action', Name='agent-' + agent_name, Namespace='XO-namespace')))
