# -- Autores --
# Paula Gallego Vieira
# Sonia Liceth Quevedo Becerra
# Justo Martín Collado
# ---------------------

from protocols_messages import *
import socket
from inputcontrol import *
# import os


def msg_join(c_socket, nick):
    send_name = craft_join(nick)
    send_one_message(c_socket, send_name)


def manage_welcome(c_socket, players, stages):
    print(msg_client["Message"])
    send_option = ""
    while send_option not in msg_client["Option_Range"]:
        send_option = input("\nYour option: ")
        if send_option not in msg_client["Option_Range"]:
            print("Option must be between 1 and 3. Try again")
    reply_welcome = craft_send_server_option(send_option, players, stages)
    send_one_message(c_socket, reply_welcome)


def manage_choose_character(c_socket):
    print(msg_client["Message"])
    choose_character = ""
    while choose_character not in msg_client["Options_Range"]:
        choose_character = input("Choose one option: ")
        if choose_character not in msg_client["Options_Range"]:
            print("The characters options are between 1 and 4. Try again")
    send_character = craft_send_character(choose_character)
    send_one_message(c_socket, send_character)


def manage_msg_server():
    print(msg_client["Message"])


def manage_turn(c_socket):
    print(msg_client["Message"])
    command = ""
    while command not in msg_client["Range_Options"]:
        command = input("Choose one option: ")
        if command not in msg_client["Range_Options"]:
            print("Option not valid. Try again")
    send_command = craft_send_character_command(command)
    send_one_message(c_socket, send_command)


def manage_send_games(c_socket, nick):
    msg = msg_client["Message"]
    options = msg_client["Options_Range"]
    if options == "0":
        print(msg)
        msg_join(c_socket, nick)
    else:
        print(msg)
        choice = ""
        while choice not in msg_client["Options_Range"]:
            choice = input("Choose one option: ")
            if choice not in msg_client["Options_Range"]:
                print("Option not valid. Try again")
        reply = craft_send_game_choice(choice)
        send_one_message(c_socket, reply)


def manage_valid_game(c_socket, nick):
    joined = msg_client["Joined"]
    if not joined:
        print("You won't be able to join the game, select a new game or create any other game if possible")
        msg_join(c_socket, nick)


def manage_endgame():
    if msg_client["Win"]:
        print("All the stages have been cleared. CONGRATS! YOU WON THE GAME!")
    else:
        print("All characters have been defeated. Try again. GAME OVER")


def manage_dcserver():
    print(msg_client["Reason"])



def manage_bookworm_send(msgc, c_socket):
    msg = msgc["Message"]
    options = msgc["Options"]
    list_resurrect = msgc["List"]
    choose = ""
    if len(list_resurrect) > 0:
        while choose not in options:
            choose = input(msg)
            if choose not in str(options):
                print("Option not valid. Try again")
            else:
                reply = craft_bookworm_choose(choose, list_resurrect)
                send_one_message(c_socket, reply)
    else:
        print(msg)


def manage_msgs(msg_client, client_socket, n_players, n_stages, finalize):
    if msg_client["Protocol"] == PROTOCOL_WELCOME:
        manage_welcome(client_socket, n_players, n_stages)
    elif msg_client["Protocol"] == PROTOCOL_CHOOSE_CHARACTER:
        manage_choose_character(client_socket)
    elif msg_client["Protocol"] == PROTOCOL_SERVER_MSG:
        manage_msg_server()
    elif msg_client["Protocol"] == PROTOCOL_YOUR_TURN:
        manage_turn(client_socket)
    elif msg_client["Protocol"] == PROTOCOL_SEND_GAMES:
        manage_send_games(client_socket, name)
    elif msg_client["Protocol"] == PROTOCOL_SEND_VALID_GAME:
        manage_valid_game(client_socket, name)
    elif msg_client["Protocol"] == PROTOCOL_SEND_END_GAME:
        manage_endgame()
        finalize = True
    elif msg_client["Protocol"] == PROTOCOL_SEND_DC_SERVER:
        manage_dcserver()
        finalize = True
        client_socket.close()
    elif msg_client["Protocol"] == PROTOCOL_WAIT:
        print("Waiting for other players")
    elif msg_client["Protocol"] == PROTOCOL_CONTINUE:
        print("The game can continue")
    elif msg_client["Protocol"] == PROTOCOL_BOOKWORM_SEND:
        manage_bookworm_send(msg_client, client_socket)
    return finalize


try:
    n_players, n_stages, ip, port, name = parse_args_client()
    check_args(n_players, n_stages, name)
    port = check_port(port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    msg_join(client_socket, name)
    finalize = False
    while not finalize:
        try:
            msg_type = recv_one_message(client_socket)
            if msg_type is not None or msg_type != '':
                msg_client = decoded_msgs(msg_type)
                finalize = manage_msgs(msg_client, client_socket, n_players, n_stages, finalize)
        except KeyboardInterrupt:
            client_reply = craft_send_dc_me()
            send_one_message(client_socket, client_reply)
            client_socket.close()
            print("Program finished due to CTRL+C command.")
    client_socket.close()
except OSError:
    print("Client disconnected due to OSERROR")
except ConnectionResetError:
    print("The connection to the server has been interrupted")
except ConnectionRefusedError:
    print("Could not connect to the server. Are you sure you have provided the correct ip and port?")
except ArgumentError:
    print("Program finished due to bad arguments.")
except BrokenPipeError:
    pass
