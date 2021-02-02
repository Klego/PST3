# -- Autores --
# Paula Gallego Vieira
# Sonia Liceth Quevedo Becerra
# Justo Martín Collado
# ---------------------

# This gives a warning. We think it's because global dictionaries
from game import *
import socket
import threading
from protocols_messages import *
import inputcontrol
from doubly_map import *

games = DoublyLinkedList()
clients_games = DoublyLinkedList()
awaiting_players = DoublyLinkedList()
ll_sockets = DoublyLinkedList()
players_names = DoublyLinkedList()
ll_threads = DoublyLinkedList()
finished_games = DoublyLinkedList()


def list_players_in_games():
    global games
    global clients_games
    players_in_game = 0
    available_games = ""
    i = 0
    players = 0
    if games.get_length() > 0:
        for i in games:
            players = games.find_node(i).get_players()
            for j in clients_games:
                if i == clients_games.find_node(j):
                    players_in_game += 1
        available_games = available_games + str(i) + ".- Players: " + str(players_in_game) + "/" + str(players) + "\t"
    else:
        available_games = "NO_GAMES"

    return available_games


def broadcast_clients(id_game, server_reply, c_address):
    global clients_games
    global ll_sockets
    for key_client in clients_games:
        if clients_games.find_node(key_client) == id_game:
            for key_sockets in ll_sockets:
                if key_sockets == key_client and key_sockets != c_address:
                    send_one_message(ll_sockets.find_node(key_sockets), server_reply)


def creator_name(id_game):
    global clients_games
    global players_names
    list_names = []
    for i in clients_games:
        if clients_games.find_node(i) == id_game:
            for j in players_names:
                if j == i:
                    list_names.append(players_names.find_node(j))
    if len(list_names) > 0:
        creators_name = list_names[0]
    else:
        creators_name = "None"
    return creators_name


def list_players_names(id_game):
    global clients_games
    global players_names
    list_names = []
    for i in clients_games:
        if clients_games.find_node(i) == id_game:
            for j in players_names:
                if j == i:
                    list_names.append(players_names.find_node(j))
    return list_names


def send_to_all_players(id_game, server_reply):
    global clients_games
    global ll_sockets
    for key_client in clients_games:
        if clients_games.find_node(key_client) == id_game:
            for key_socket in ll_sockets:
                if key_socket == key_client:
                    send_one_message(ll_sockets.find_node(key_socket), server_reply)


def manage_join(name, c_socket):
    print("\n(WELCOME) " + name + " joined the server")
    server_reply = craft_welcome()
    send_one_message(c_socket, server_reply)


def manage_disconnection(reason, c_socket, client_thread):
    server_reply = craft_send_dc_server(reason)
    send_one_message(c_socket, server_reply)
    client_thread.set_disconnected()


def manage_server_option(client_thread, msg, c_address, name, c_socket):
    global games
    global awaiting_players
    option = int(msg["Option"])
    players = int(msg["Players"])
    stages = int(msg["Stages"])
    if option == 1:
        if games.length <= 3:
            id_game = games.length + 1
            game = Game(players, stages)
            games.append(id_game, game)
            awaiting_players.append(c_address, id_game)
            print("\n(CREATE) " + name + " created a game")
            server_reply = craft_choose_character()
            send_one_message(c_socket, server_reply)
        else:
            print("\n(EXIT) " + name + " disconnected by SERVER (No new game slots)")
            reason = "SERVER: There are no empty slots for a new game"
            manage_disconnection(reason, c_socket, client_thread)
    elif option == 2:
        available_games = list_players_in_games()
        server_reply = craft_send_games(available_games)
        send_one_message(c_socket, server_reply)
    elif option == 3:
        print("\n(EXIT) " + name + " disconnected")
        reason = "SERVER: Client disconnected by himself"
        manage_disconnection(reason, c_socket, client_thread)


def save_character(c_address, id_game, c_socket, name, game, option, client_thread):
    global clients_games
    global awaiting_players
    global players_names
    global ll_sockets
    global ll_threads
    clients_games.append(c_address, id_game)
    ll_sockets.append(c_address, c_socket)
    players_names.append(c_address, name)
    del awaiting_players[c_address]
    ll_threads.append(c_address, client_thread)
    character = game.choose_character(option)
    game.set_player(character, name)


def send_message(msg, id_game):
    message = craft_server_msg(msg)
    send_to_all_players(id_game, message)


def send_turn(id_game):
    global games
    global players_names
    global clients_games
    global ll_sockets
    game = games.find_node(id_game)
    for i in clients_games:
        if clients_games.find_node(i) == id_game:
            for j in ll_sockets:
                if j == i:
                    name = players_names.find_node(j)
                    ask_turn = craft_your_turn(game.get_dic_player(name), name)
                    send_one_message(ll_sockets.find_node(j), ask_turn)


def init_game(id_game):
    global games
    game = games.find_node(id_game)
    message = game.show_chars_attributes()
    message += game.show_stage()
    message += game.show_round()
    new_msg = message.format("PLAYERS")
    server_reply = craft_server_msg(new_msg)
    send_to_all_players(id_game, server_reply)
    send_turn(id_game)


def clear_dicts(id_game):
    global games
    global clients_games
    global players_names
    global ll_sockets
    global ll_threads

    for player in clients_games:
        if clients_games.find_node(player) == id_game:
            ll_sockets.delete_node_by_key(player)
            players_names.delete_node_by_key(player)
            ll_threads.delete_node_by_key(player)
            clients_games.delete_node_by_key(player)
    games.delete_node_by_key(id_game)


def check_player_attack(game):
    if len(game.get_check_turn()) < game.get_players():
        all_players_attacked = False
    else:
        all_players_attacked = True
        game.clean_check_turn()

    return all_players_attacked


def manage_send_character(client_thread, msg, c_address, c_socket, name):
    global clients_games
    global games
    global awaiting_players
    option = msg["Option"]
    id_game = awaiting_players.find_node(c_address)
    game = games.find_node(id_game)
    players = int(game.get_players())
    players_count = 0
    # check how many players in game
    for i in clients_games:
        if clients_games.find_node(i) == id_game:
            players_count += 1
    if players_count < players:
        if players == 1:
            print("\n(START) {} started a game".format(name))
            save_character(c_address, id_game, c_socket, name, game, option, client_thread)
            init_game(id_game)
        else:
            save_character(c_address, id_game, c_socket, name, game, option, client_thread)
            players_count = 0
            for i in clients_games:
                if clients_games.find_node(i) == id_game:
                    players_count += 1
            if players_count < players:
                server_reply = craft_wait()
                send_one_message(c_socket, server_reply)
            else:
                # BROADCAST SENDALL TO THE CLIENTS CONNECTED TO THE GAME
                server_reply = craft_continue()
                broadcast_clients(id_game, server_reply, c_address)
                init_game(id_game)
    else:
        del awaiting_players[c_address]
        print("\n(EXIT) " + name + " disconnected by SERVER (No new slots in selected game)")
        reason = "SERVER: There are no empty slots for the game"
        manage_disconnection(reason, c_socket, client_thread)


def manage_bookworm(msg, name, c_address, c_socket):
    global games
    global clients_games
    option = msg["Option"]
    resurrection_list = msg["List"]
    id_game = clients_games.find_node(c_address)
    new_msg = games.find_node(id_game).char_resurrect(resurrection_list, option, name)
    send_message(new_msg, id_game)
    send_wait_or_continue(name, id_game, c_socket, c_address)


def enemies_turn(id_game):
    global games
    msg = games.find_node(id_game).show_turn()
    msg = msg.format('MONSTERS')
    msg += "\n" + games.find_node(id_game).turn_enemy_attack()
    server_reply = craft_server_msg(msg)
    send_to_all_players(id_game, server_reply)


def send_end_game(win, id_game):
    server_reply = craft_send_end_game(win)
    send_to_all_players(id_game, server_reply)
    for players in clients_games:
        if clients_games.find_node(players) == id_game:
            ll_threads.find_node(players).set_disconnected()


def game_check(id_game):
    global games
    game = games.find_node(id_game)
    check = game.check_game()
    if check == 1:
        message = game.show_round()
        msg = message.format("PLAYERS")
        server_reply = craft_server_msg(msg)
        send_to_all_players(id_game, server_reply)
        send_turn(id_game)
    elif check == 2:
        msg = game.prepare_new_stage()
        server_reply = craft_server_msg(msg)
        send_to_all_players(id_game, server_reply)
        message = game.show_stage()
        message += game.show_round()
        new_msg = message.format("PLAYERS")
        server_reply = craft_server_msg(new_msg)
        send_to_all_players(id_game, server_reply)
        send_turn(id_game)
    elif check == 3:
        players_in_game = list_players_names(id_game)
        names = ""
        for name in players_in_game:
            names += name + ", "
        names = names[:len(names) - 2]
        print("\n(GAMEEND) {} game ended. They lost.".format(names))
        win = False
        send_end_game(win, id_game)
        finished_games.append(id_game, id_game)
        clear_dicts(id_game)
    elif check == 4:
        players_in_game = list_players_names(id_game)
        names = ""
        for name in players_in_game:
            names += name + ", "
        names = names[:len(names) - 2]
        print("\n(GAMEEND) {} game ended. They won.".format(names))
        win = True
        send_end_game(win, id_game)
        finished_games.append(id_game, id_game)
        clear_dicts(id_game)


def send_wait_or_continue(name, id_game, c_socket, c_address):
    global games
    games.find_node(id_game).set_turn(name)
    if not check_player_attack(games.find_node(id_game)):
        server_reply = craft_wait()
        send_one_message(c_socket, server_reply)
    else:
        server_reply = craft_continue()
        broadcast_clients(id_game, server_reply, c_address)
        enemies_turn(id_game)
        game_check(id_game)


def manage_char_command(msg, c_address, c_socket):
    global games
    global clients_games
    global players_names
    if clients_games.get_length() > 0:
        if clients_games.find_node(c_address):
            name = players_names.find_node(c_address)
        else:
            name = "NO_NAME"
    else:
        return
    command = msg["Command"]
    id_game = clients_games.find_node(c_address)
    check = games.find_node(id_game).check_game()
    if check == 1:
        if games.find_node(id_game).dicPlayer[name].get_alive():
            if games.find_node(id_game).dicPlayer[name].__class__.__name__ == "Bookworm" and command == "s":
                msg, list_to_resurrect = games.find_node(id_game).choose_character_option(command, name)
                if len(list_to_resurrect) > 0:
                    # BOOKWORM'S SKILL SPECIAL MESSAGE PROTOCOL
                    server_reply = craft_bookworm_send(msg, list_to_resurrect)
                    send_one_message(c_socket, server_reply)
                else:
                    send_message(msg, id_game)
                    send_wait_or_continue(name, id_game, c_socket, c_address)
            else:
                msg = games.find_node(id_game).choose_character_option(command, name)
                send_message(msg, id_game)
                send_wait_or_continue(name, id_game, c_socket, c_address)
        else:
            msg = "\nThe {} ({}) has been defeated. It can not make any move until revived.\n The turn is passed."
            new_msg = msg.format(games.find_node(id_game).get_dic_player(name).__class__.__name__, name)
            send_message(new_msg, id_game)
            send_wait_or_continue(name, id_game, c_socket, c_address)
    else:
        game_check(id_game)


def manage_game_choice(msg, c_socket, c_address, name):
    global games
    global clients_games
    global awaiting_players
    option = int(msg["Option"])
    num_players = 0
    game = games.find_node(option)
    players = game.players
    for i in clients_games:
        if i == option:
            num_players += 1
    if num_players < players:
        if clients_games.get_length() > 0:
            joined = True
            server_reply = craft_send_valid_game(joined)
            send_one_message(c_socket, server_reply)
            awaiting_players.append(c_address, option)
            print("\n(JOIN) " + name + " joined " + creator_name(option) + "'s game")
            server_reply = craft_choose_character()
            send_one_message(c_socket, server_reply)
        else:
            msg = "\nThere is no game created"
            server_reply = craft_server_msg(msg)
            send_one_message(c_socket, server_reply)
            server_reply = craft_welcome()
            send_one_message(c_socket, server_reply)
    else:
        joined = False
        server_reply = craft_send_valid_game(joined)
        send_one_message(c_socket, server_reply)


def manage_disconnected_player(client_thread):
    global clients_games
    global players_names
    print("\n(DC) " + players_names.find_node(client_thread.client_address) + " was disconnected")
    reason = "A player disconnected from the game."
    id_game = clients_games.find_node(client_thread.client_address)
    server_reply = craft_send_dc_server(reason)
    broadcast_clients(id_game, server_reply, client_thread.client_address)
    for clients in clients_games:
        if clients_games.find_node(clients) == id_game:
            print("(DC) " + players_names.find_node(clients) + " has been disconnected")
    print("SERVER: Game " + str(id_game) + " was finished because a player was disconnected.")
    for players in clients_games:
        if clients_games.find_node(players) == id_game:
            ll_threads.find_node(players).set_disconnected()
    clear_dicts(id_game)


class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.name = ""
        self.end = False

    def set_disconnected(self):
        self.end = True

    def manage_msg(self, decoded_msg):
        if decoded_msg["Protocol"] == PROTOCOL_JOIN:
            self.name = decoded_msg["Name"]
            manage_join(self.name, self.client_socket)
        elif decoded_msg["Protocol"] == PROTOCOL_SEND_SERVER_OPTION:
            manage_server_option(self, decoded_msg, self.client_address, self.name, self.client_socket)
        elif decoded_msg["Protocol"] == PROTOCOL_SEND_CHARACTER:
            manage_send_character(self, decoded_msg, self.client_address, self.client_socket, self.name)
        elif decoded_msg["Protocol"] == PROTOCOL_SEND_CHARACTER_COMMAND:
            manage_char_command(decoded_msg, self.client_address, self.client_socket)
        elif decoded_msg["Protocol"] == PROTOCOL_SEND_GAME_CHOICE:
            manage_game_choice(decoded_msg, self.client_socket, self.client_address, self.name)
        elif decoded_msg["Protocol"] == PROTOCOL_SEND_DC_ME:
            manage_disconnected_player(self)
        elif decoded_msg["Protocol"] == PROTOCOL_BOOKWORM_CHOOSE:
            manage_bookworm(decoded_msg, self.name, self.client_address, self.client_socket)

    def run(self):

        while not self.end:
            try:
                message = recv_one_message(self.client_socket)
                msg_client = decoded_msgs(message)
                self.manage_msg(msg_client)
            except TypeError:
                pass


class ServerSocketThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.stop = False
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", self.port))
        self.server_socket.listen(20)

    def run(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = ClientThread(client_socket, client_address)
            client_thread.start()


def shutdown_server():
    global ll_sockets
    print("The server has been closed by the admin.")
    reason = "The server has been shut down by the admin. You have been disconnected."
    server_reply = craft_send_dc_server(reason)
    for client_socket in ll_sockets:
        send_one_message(client_socket, server_reply)


def ngames():
    print("Active games: " + str(games.length) + "\n")
    print("Finished games: " + str(finished_games.length) + "\n")


def games_info():
    global games
    total_players = []
    dead_players = []
    current_stage = []
    total_stages = []
    if len(games) > 0:
        for id_game in games:
            game = games[id_game]
            total_players.insert(1, game.get_players())
            dead_players.insert(1, game.get_dead_players())
            current_stage.insert(1, game.get_current_stage())
            total_stages.insert(1, game.get_stages())
        count = 0
        while count < len(games):
            print("------ GAME -----\n")
            print("Total Players: ", str(total_players[count]) + "\n")
            print("Dead Players: ", str(dead_players[count]) + "\n")
            print("Current Stage: ", str(current_stage[count]) + "\n")
            print("Total Stages: ", str(total_stages[count]) + "\n")
            print("--------------------\n\n")
            count += 1
    else:
        print("There are no available games at the moment\n")


try:
    finish = False
    port = inputcontrol.parse_args_server()
    port = inputcontrol.check_port(port)
    server_socket_thread = ServerSocketThread(port)
    server_socket_thread.daemon = True
    server_socket_thread.start()
    print("Server started at {}:{} \n".format("127.0.0.1", port))
    while not finish:
        command = str(input("Command: "))
        if command == "shutdown" or command == "close":
            shutdown_server()
            finish = True
        elif command == "ngames":
            ngames()
        elif command == "gamesinfo":
            games_info()
        else:
            print("Not a valid command. Available commands are: shutdown/close, ngames or gamesinfo\n")
except inputcontrol.ArgumentError:
    print("\nProgram finished due to bad arguments.")
except ConnectionResetError:
    print("\nThe connection to the client has been interrupted")
except ConnectionRefusedError:
    print("\nCould not connect to the client")
except KeyboardInterrupt:
    print("\nProgram finished due to CTRL+C command.")
