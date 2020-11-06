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
        sleep(2)

        print("starting to get users")

        users = list(client.GetActors())
        if len(users) != 2:
            continue

        flag = False
        for agent in users:
            if not agent.readiness:
                flag = True
        if flag:
            continue

        for agent in users:
            agents.append(agent.name)
        break

    print("starting to initiate world")
    world = {
        'world': [[None] * 3] * 3,
        'turn': agents[0],
    }
    print("world =", world)
    client.Put(Message(
        key=Key(type="world", name="referee", namespace="xo-namespace"),
        content=dumps(world),
    ))

    for action in client.Watch(Key(type="action", namespace="xo-namespace")):
        world = loads(client.Get(Key(type="world", name="referee", namespace="xo-namespace")).content)

        print("starting to generate new world")
        try:
            newWorld = evolve(world, action.key.name, loads(action.content))
        except ValueError:
            continue

        print("new world =", newWorld)
        winner = check_game_status(newWorld)
        result = Result()
        result.status = Result.success
        if winner is None:
            client.Put(Message(key=Key(type="world", name="referee", namespace="xo-namespace"), content=dumps(newWorld)))
            continue
        elif winner == 'draw':
            result.scores = [Result.Score(name=agent[0],score=1),Result.Score(name=agent[1],score=1)]
        elif winner == agents[0]:
            result.scores = [Result.Score(name=agent[0],score=3),Result.Score(name=agent[1],score=0)]
        elif winner == agents[1]:
            result.scores = [Result.Score(name=agent[0],score=0),Result.Score(name=agent[1],score=3)]

        client.PutResult(result)
        exit(0)
