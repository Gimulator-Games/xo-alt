from python.client import DirectorClient
from python.proto_pb2 import *
from time import sleep
from json import loads, dumps

agents = []


def evolve(world: dict, agentName: str, action: list) -> dict:
    print("starting to evolve world", world)

    if world['turn'] != agentName:
        print("action is invalid! It isn't its turn...")
        raise ValueError()

    if not (0 <= action[0] < 3 and 0 <= action[1] < 3):
        print("invalid action, range error")
        raise ValueError()

    if world['world'][action[0]][action[1]] is not None:
        print("cell was full")
        raise ValueError()

    if agentName == agents[0]:
        world['world'][action[0]][action[1]] = 'X'
        world['turn'] = agents[1]
    else:
        world['world'][action[0]][action[1]] = 'O'
        world['turn'] = agents[0]

    return world


def check_game_status(world: dict):
    board = world['world']

    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]

    if board[0][0] == board[1][1] == board[2][2]:
        return board[1][1]
    elif board[0][2] == board[1][1] == board[2][0]:
        return board[1][1]
    else:
        for row in board:
            for cell in row:
                if cell is None:
                    return None
    return 'draw'


if __name__ == "__main__":
    client = DirectorClient()

    while True:
        users = list(client.GetActors())
        if len(users) == 2:
            for agent in users:
                agents.append(agent.Name)
            break
        sleep(2)

    world = {
        'world': [[None] * 3] * 3,
        'turn': agents[0],
    }
    client.Put(Message(
        Key=Key(Type="world", Name="referee", Namespace="xo-namespace"),
        Content=dumps(world),
    ))

    for action in client.Watch(Key(Type="action", Namespace="xo-namespace")):
        world = loads(client.Get(Key(Type="world", Name="referee", Namespace="xo-namespace")).Content)

        try:
            newWorld = evolve(world, action.Key.Name, loads(action.Content))
        except ValueError:
            continue

        winner = check_game_status(newWorld)
        if winner is None:
            client.Put(Message(Key=Key(Type="world", Name="referee", Namespace="xo-namespace"), Content=dumps(newWorld)))
        else:
            client.PutResult(Result(Status=Status, Score=Score()))
            print("result: ", winner)
            exit(0)
