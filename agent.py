from python.proto_pb2 import *
from python.proto_pb2_grpc import *

from os import environ
from json import loads, dumps
from python.client import ActorClient
from time import sleep
import random
import string

agent_name = ""

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

    agent_name = environ["GIMULATOR_NAME"]

    agent = Agent()

    client.ImReady()

    while True:
        sleep(2)

        try:
            response = client.Get(Key(type="world", name="referee", namespace="xo-namespace"))
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print("world not found")
                continue
            raise e

        world = loads(response.content)
        reaction = agent.react(world)
        print("Reaction is ", reaction)
        if len(reaction) != 0:
            client.Put(Message(key=Key(type="action", name=agent_name, namespace="xo-namespace"), content=dumps(reaction)))
