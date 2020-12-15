import os
import sys
import argparse
NUM_MAX_STAGES = 10
NUM_MAX_PLAYERS = 4
NUM_MAX_PORT = 65535
NUM_MIN_PORT = 1024


class InvalidInputError(Exception):
    pass


class RetryCountExceededError(Exception):
    pass


def sanitize_inputs(message="", valid_input=[], valid_cast=str, num_retries=-1):
    cont_retries = 0
    while cont_retries < num_retries or num_retries < 0:
        try:
            raw = valid_cast(input(message))
            if raw in valid_input:
                return raw
            else:
                raise InvalidInputError("You have inputted a wrong option.\n")
        except ValueError:
            print("ValueError Exception. Quitting program...\n")
            sys.exit(0)
        except InvalidInputError:
            cont_retries += 1
            continue
        except KeyboardInterrupt:
            print("The user terminated the program. Quitting...\n")
            sys.exit(0)
    raise RetryCountExceededError("RetryCountExceededError: count exceeded in function 'sanitize_inputs")


def clear_screen():
    os.system('clear')


def arguments_parser_client():
    num_players = 1
    num_stages = 1
    nick = ""
    port = 8080
    try:
        error = False
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--players', type=int, default=1)
        parser.add_argument('-s', '--stages', type=int, default=1)
        parser.add_argument('-n', '--name', type=str)
        parser.add_argument('-i', '--ip', type=str, default="127.0.0.1")
        parser.add_argument('-o', '--port', type=int, default=8080)
        args = parser.parse_args()
        if not int(args.players) <= NUM_MAX_PLAYERS:
            print("The number of players must be between 1 and 4. Finishing program")
            error = True
        else:
            num_players = args.players
        if not int(args.stages) <= NUM_MAX_STAGES:
            print("The number of stages must be between 1 and 10. Finishing program")
            error = True
        else:
            num_stages = args.stages
        if not args.name:
            print("A name for the nickname must be given. Finishing program.")
            error = True
        else:
            nick = args.name
        if not NUM_MIN_PORT <= int(args.port) <= NUM_MAX_PORT:
            print("The port can't be used. Use a port between 1024 and 65535. Finishing program.")
            error = True
        else:
            port = args.port
        ip = args.ip
        if error:
            sys.exit(0)
        else:
            return num_players, num_stages, nick, ip, port
    except ValueError:
        print("You inputted strings where you should write integers. Finishing program\n")
        sys.exit(0)


def arguments_parser_server():
    port = 8080
    try:
        error = False
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--port', type=int, default=8080)
        args = parser.parse_args()
        if not NUM_MIN_PORT <= int(args.port) <= NUM_MAX_PORT:
            print("The port can't be used. Use a port between 1024 and 65535. Finishing program.")
            error = True
        else:
            port = args.port
        if error:
            sys.exit(0)
        else:
            return port
    except ValueError:
        print("You inputted strings where you should write integers. Finishing program\n")
        sys.exit(0)


def list_games(client_game):
    for games in client_game.values():
        pass
