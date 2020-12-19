import json
from game import *


PROTOCOL_JOIN = "Join"
PROTOCOL_WELCOME = "Welcome"
PROTOCOL_SEND_SERVER_OPTION = "Send_Server_Option"
PROTOCOL_CHOOSE_CHARACTER = "Choose_Character"
PROTOCOL_SEND_CHARACTER = "Send_Character"
PROTOCOL_SERVER_MSG = "Server_Msg"
PROTOCOL_YOUR_TURN = "Your_Turn"
PROTOCOL_SEND_CHARACTER_COMMAND = "Send_Character_Command"
PROTOCOL_SEND_GAMES = "Send_Games"
PROTOCOL_SEND_GAME_CHOICE = "Send_Game_Choice"
PROTOCOL_SEND_VALID_GAME = "Send_Valid_Game"
PROTOCOL_SEND_END_GAME = "Send_End_Game"
PROTOCOL_SEND_DC_ME = "Send_DC_Me"
PROTOCOL_SEND_DC_SERVER = "Send_DC_SERVER"
PROTOCOL_WAIT = "Wait"
PROTOCOL_CONTINUE = "Continue"
PROTOCOL_BOOKWORM_SEND = "Bookworm_Send"
PROTOCOL_BOOKWORM_CHOOSE = "Bookworm_Choose"


def craft_join(nick):
    message = {"Protocol": PROTOCOL_JOIN, "Name": nick}
    return json.dumps(message).encode()


def craft_welcome():
    # options = [1, 2, 3]
    options = ["1", "2", "3"]
    init_menu = "Welcome to the server. Choose one of this options:\n" + "\t 1.- Create game\n" + "\t 2.- Join game\n" \
                + "\t 3.- Exit\n "
    message = {"Protocol": PROTOCOL_WELCOME, "Message": init_menu, "Option_Range": options}
    return json.dumps(message).encode()


def craft_send_server_option(option, players, stages):
    message = {"Protocol": PROTOCOL_SEND_SERVER_OPTION, "Option": option, "Players": players, "Stages": stages}
    return json.dumps(message).encode()


def craft_choose_character():
    index = 1
    # options = [1, 2, 3, 4]
    options = ["1", "2", "3", "4"]
    menu = Game.display_chars_menu()
    message = {"Protocol": PROTOCOL_CHOOSE_CHARACTER, "Message": menu, "Options_Range": options}
    return json.dumps(message).encode()


def craft_send_character(option):
    message = {"Protocol": PROTOCOL_SEND_CHARACTER, "Option": option}
    return json.dumps(message).encode()


def craft_server_msg(server_message):
    message = {"Protocol": PROTOCOL_SERVER_MSG, "Message": server_message}
    return json.dumps(message).encode()


def craft_your_turn(character, nickname):
    msg = "The " + character.__class__.__name__ + " (" + nickname + "). What do you want to do? [a, s]: "
    options = ["a", "s"]
    message = {"Protocol": PROTOCOL_YOUR_TURN, "Message": msg, "Range_Options": options}
    return json.dumps(message).encode()


def craft_send_character_command(command):
    message = {"Protocol": PROTOCOL_SEND_CHARACTER_COMMAND, "Command": command}
    return json.dumps(message).encode()


def craft_send_games(game_list):
    options = [1, 2, 3, 4]
    msg = "-----------------------------------------------\n" + "Available games\n" \
          + "-----------------------------------------------\n" + game_list + "\n" \
          + "-----------------------------------------------\n"

    message = {"Protocol": PROTOCOL_SEND_GAMES, "Message": msg, "Options_Range": options}
    return json.dumps(message).encode()


def craft_send_game_choice(option):
    message = {"Protocol": PROTOCOL_SEND_GAME_CHOICE, "Option": option}
    return json.dumps(message).encode()


def craft_send_valid_game(joined):
    message = {"Protocol": PROTOCOL_SEND_VALID_GAME, "Joined": joined}
    return json.dumps(message).encode()


def craft_send_end_game(win):
    message = {"Protocol": PROTOCOL_SEND_END_GAME, "Win": win}
    return json.dumps(message).encode()


def craft_send_dc_me():
    message = {"Protocol": PROTOCOL_SEND_DC_ME}
    return json.dumps(message).encode()


def craft_send_dc_server(reason):
    message = {"Protocol": PROTOCOL_SEND_DC_SERVER, "Reason": reason}
    return json.dumps(message).encode()


def craft_wait():
    message = {"Protocol": PROTOCOL_WAIT}
    return json.dumps(message).encode()


def craft_continue():
    message = {"Protocol": PROTOCOL_CONTINUE}
    return json.dumps(message).encode()


def craft_bookworm_send(msg, resurrection_list):
    options = []
    option = 1
    if len(resurrection_list) > 0:
        while option <= len(resurrection_list):
            options.append(option)
            option += 1

    message = {"Protocol": PROTOCOL_BOOKWORM_SEND, "Message": msg, "Options": options, "List": resurrection_list}
    return json.dumps(message).encode()


def craft_bookworm_choose(option, resurrection_list):
    message = {"Protocol": PROTOCOL_BOOKWORM_CHOOSE, "Option": option, "List": resurrection_list}
    return json.dumps(message).encode()


def decoded_msgs(message):
    return json.loads(message.decode())
