import getopt
import sys
import os

MAX_PLAYERS = 4
MIN_PLAYERS, MIN_STAGES = 1, 1
MAX_STAGES = 10
IP = "127.0.0.1"
PORT_CLIENT = 8080
PORT_SERVER = 8080
MIN_PORT = 1024
MAX_PORT = 65535


class ArgumentError(Exception):
    pass


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def parse_args_server():
    port = PORT_SERVER
    opts, args = getopt.getopt(sys.argv[1:], "p:", ["port="])
    for o, a in opts:
        if o in ("-o", "--port"):
            port = a
    return port


def parse_args_client():
    number_players = MIN_PLAYERS
    number_stages = MIN_STAGES
    ip = IP
    port = PORT_CLIENT
    name = None
    opts, args = getopt.getopt(sys.argv[1:], "p:s:i:o:n:", ["players=", "stages=", "ip=", "port=", "name="])
    for o, a in opts:
        if o in ("-p", "--players"):
            number_players = a
        elif o in ("-s", "--stages"):
            number_stages = a
        elif o in ("-i", "--ip"):
            ip = a
        elif o in ("-o", "--port"):
            port = a
        elif o in ("-n", "--name"):
            name = a
    return number_players, number_stages, ip, port, name


def check_port(port):
    correct_port = False
    try:
        if MIN_PORT <= int(port) <= MAX_PORT:
            correct_port = True
            return int(port)
    except ValueError:
        print("The port has to be an integer")

    if not correct_port:
        raise ArgumentError
    else:
        pass


def check_args(players, stages, name):
    correct_players = False
    correct_stages = False
    try:
        players = int(players)
        if MIN_PLAYERS <= players <= MAX_PLAYERS:
            correct_players = True
        else:
            print("The number of players must be between 1 and 4.")
    except ValueError:
        print("The value given for -p or --players must be an integer number.")

    try:
        stages = int(stages)
        if MIN_STAGES <= stages <= MAX_STAGES:
            correct_stages = True
        else:
            print("The number of stages must be between 1 and 10.")
    except ValueError:
        print("The value given for -s or --stages must be an integer number.")

    if name is None:
        print("There isn´t name")
        raise ArgumentError

    if not correct_players or not correct_stages:
        raise ArgumentError
    else:
        print("A game with " + str(stages) + " stage(s) will be set up for " + str(players) + " player(s).")



