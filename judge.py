from os import environ
import logging
from time import sleep
from json import loads, dumps

from python.proto_pb2 import *

from client import GimulatorClient

LOGLEVEL = environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger('XO Judge')

players = []  # First element will be player X and second will be player of O


def evolve(world: dict, player: str, action: list) -> dict:
    # Discard action if it wasn't its turn
    if world['turn'] != player:
        logger.debug("Action was invalid! It wasn't its turn...")
        raise ValueError()

    if not (0 <= action[0] < 3 and 0 <= action[1] < 3):
        logger.debug("Action was invalid! Position was out of border...")
        raise ValueError()

    # Discard action if the position is already full
    if world['world'][action[0]][action[1]] is not None:
        logger.debug("Action was invalid! Position was full...")
        raise ValueError()

    logger.debug("Action was okay!")

    if player == players[0]:
        world['world'][action[0]][action[1]] = 'X'
        world['turn'] = players[1]
    else:
        world['world'][action[0]][action[1]] = 'O'
        world['turn'] = players[0]

    return world


def check_game_status(world: dict):
    board = world['world']
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    elif board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    else:
        for row in board:
            for cell in row:
                if cell is None:
                    return None
    return 'draw'


if __name__ == '__main__':
    client = GimulatorClient()

    logger.debug("Waiting for players to join...")
    while True:
        registers = list(client.get_all(Key(Type='register', Namespace='XO-namespace')))
        if len(registers) == 2:
            for player in registers:
                players.append(player.Content)
            break
        sleep(3)

    logger.debug("Creating initial world...")
    client.put(Message(Content=dumps({
        'world': [[None] * 3] * 3,
        'turn': players[0]
    }), Key=Key(Type='world', Name='judge', Namespace='XO-namespace')))

    for action in client.watch(Key(Type='action')):
        logger.debug("Action received: " + action.Content)

        world = loads(client.get(Key(Type='world', Name='judge', Namespace='XO-namespace')).Content)

        try:
            world = evolve(world, action.Key.Name, loads(action.Content))
        except ValueError:
            continue

        logger.debug("World changed: " + str(world))

        winner = check_game_status(world)
        if winner is None:
            client.put(Message(Content=dumps(world), Key=Key(Type='world', Name='judge', Namespace='XO-namespace')))
        else:
            client.put(Message(Content=winner, Key=Key(Type='result', Name='judge', Namespace='XO-namespace')))
