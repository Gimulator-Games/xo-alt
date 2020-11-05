from python.proto_pb2 import *
from python.proto_pb2_grpc import *

from json import loads, dumps
from python.client import ActorClient
from time import sleep
import random
import string

agent_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5))


class Agent:
    def react(self, world: dict) -> list:
        print("starting to react")
        if world['turn'] != agent_name:
            print("it's not my turn")
            return []
        
        for i, row in enumerate(world['world']):
            for j, cell in enumerate(row):
                if cell is None:
                    return [i, j]


if __name__ == '__main__':
    client = ActorClient()

    agent = Agent()

    client.ImReady()

    while True:
        sleep(1)

        try:
            response = client.Get(Key(Type="world", Name="referee", Namespace="xo-namespace"))
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                continue
            raise e

        reaction = agent.react(loads(response.Content))
        print("Reaction is ", reaction)
        if len(reaction) != 0:
            client.Put(Message(Key=Key(Type="action", Name=agent_name, Namespace="xo-namespace"), Content=dumps(reaction)))
