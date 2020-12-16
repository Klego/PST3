# -- Autores --
# Paula Gallego Vieira
# Sonia Liceth Quevedo Becerra
# Justo Martín Collado
# ---------------------

from game import *
import socket
import threading
import os
from protocols_messages import *
import utils

games = {}
clients_games = {}
awaiting_players = {}
dic_sockets = {}
players_names = {}


def list_players_in_games():
    global games
    global clients_games
    players_in_game = 0
    available_games = ""
    if games:
        for i in games.keys():
            players = games[i].get_players()
            for j in clients_games.values():
                if i == j:
                    players_in_game += 1
        available_games = available_games + str(i) + ".- Players: " + str(players_in_game) + "/" + str(players) + "\t"
    else:
        available_games = "There are no games available. Please, create a new game."

    return available_games


def broadcast_clients(id_game, server_reply, c_address):
    global clients_games
    global games
    global dic_sockets
    for i in clients_games.keys():
        if clients_games[i] == id_game:
            for j in dic_sockets.keys():
                if j == i and j != c_address:
                    dic_sockets[j].sendall(server_reply)


def creator_name(id_game):
    list_names = []
    for i in clients_games.keys():
        if clients_games[i] == id_game:
            for j in players_names.keys():
                if j == i:
                    list_names.append(players_names[j])
    creators_name = list_names[0]
    return creators_name


def manage_join(name, c_socket):
    print("(WELCOME) " + name + " joined the server")
    server_reply = craft_welcome()
    c_socket.sendall(server_reply)


def manage_disconnection(reason, c_socket, client_thread):
    server_reply = craft_send_dc_server(reason)
    c_socket.sendall(server_reply)
    client_thread.set_disconnected()


def manage_server_option(client_thread, msg, c_address, name, c_socket):
    global games
    global awaiting_players
    option = msg["Option"]
    players = int(msg["Players"])
    stages = int(msg["Stages"])
    id_game = 1
    if option == "1":
        if len(games) <= 3:
            for index_key in games.keys():
                id_game += 1
            game = Game(players, stages)
            games[id_game] = game
            awaiting_players[c_address] = id_game
            print("(CREATE) " + name + " created a game")
            server_reply = craft_choose_character()
            c_socket.sendall(server_reply)
        else:
            # Falta. solucion = el error de client
            print("(EXIT) " + name + " disconnected by SERVER (No new game slots)")
            reason = "SERVER: There are no empty slots for a new game"
            manage_disconnection(reason, c_socket, client_thread)
    elif option == "2":
        available_games = list_players_in_games()
        server_reply = craft_send_games(available_games)
        c_socket.sendall(server_reply)
    elif option == "3":
        print("(EXIT) " + name + " disconnected")
        reason = "SERVER: Client disconnected by himself"
        manage_disconnection(reason, c_socket, client_thread)


def enter_game(c_address, id_game, c_socket, name, game, option, players_count):
    # Preguntar si hay que poner aqui las globales
    global clients_games
    global games
    global awaiting_players
    global players_names
    clients_games[c_address] = id_game
    dic_sockets[c_address] = c_socket
    players_names[c_address] = name
    del awaiting_players[c_address]
    character = game.choose_character(option)
    game.set_player(character, players_count)


def send_message(msg, c_socket):
    message = craft_server_msg(msg)
    c_socket.sendall(message)


def send_turn(c_socket, game, name, players_count):
    ask_turn = craft_your_turn(game.get_dic_player(players_count), name)
    c_socket.sendall(ask_turn)


def manage_send_character(client_thread, msg, c_address, c_socket, name):
    global clients_games
    global games
    global awaiting_players
    global players_names
    option = msg["Option"]
    id_game = awaiting_players[c_address]
    game = games[id_game]
    players = int(game.get_players())
    players_count = 0
    # check how many players in game
    for i in clients_games.values():
        if i == id_game:
            players_count += 1
    if players_count < players:
        if players == 1:
            print("(START) {} started a game".format(name))
            enter_game(c_address, id_game, c_socket, name, game, option, players_count)
            message = game.show_chars_attributes(name)
            message += game.show_stage()
            send_message(message, c_socket)
            send_turn(c_socket, game, name, players_count)
        else:
            enter_game(c_address, id_game, c_socket, name, game, option, players_count)
            players_count = 0
            for i in clients_games.values():
                if i == id_game:
                    players_count += 1
            if players_count < players:
                server_reply = craft_wait()
                c_socket.sendall(server_reply)
            else:
                # BROADCAST SENDALL TO THE CLIENTS CONNECTED TO THE GAME
                server_reply = craft_continue()
                broadcast_clients(id_game, server_reply, c_address)
    else:
        del awaiting_players[c_address]
        print("(EXIT) " + name + " disconnected by SERVER (No new slots in selected game)")
        reason = "SERVER: There are no empty slots for the game"
        manage_disconnection(reason, c_socket, client_thread)


def manage_char_command(msg, c_address, c_socket, name):
    global games
    global clients_games
    command = msg["Command"]
    id_game = clients_games[c_address]
    msg = games[id_game].choose_character_option(command, name)
    send_message(msg, c_socket)
#     si han atacado todos los jugadores que ataquen los enemigos


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
            manage_char_command(decoded_msg, self.client_address, self.client_socket, self.name)
        # if decoded_msg["Protocol"] == PROTOCOL_SEND_GAME_CHOICE:
        #     option = decoded_msg["Option"]
        #     num_players = 0
        #     game = games[option]
        #     players = game.players
        #     for i in clients_games.values():
        #         if i == option:
        #             num_players += 1
        #     if num_players < players:
        #         joined = True
        #         server_reply = craft_send_valid_game(joined)
        #         self.client_socket.sendall(server_reply)
        #         awaiting_players[self.client_address] = option
        #         print("(JOIN) " + self.name + " joined " + creator_name(option) + "'s game")
        #         server_reply = craft_choose_character()
        #         self.client_socket.sendall(server_reply)
        #     else:
        #         joined = False
        #         server_reply = craft_send_valid_game(joined)
        #         self.client_socket.sendall(server_reply)

        # if decoded_msg["Protocol"] == PROTOCOL_SEND_DC_ME:
        #     print("(DC) " + players_names[self.client_address] + " was disconnected")
        #     reason = "A player disconnected from the game."
        #     id_game = clients_games[self.client_address]
        #     server_reply = craft_send_dc_server(reason)
        #     broadcast_clients(id_game, server_reply, self.client_address)
        #     ClientThread.set_disconnected()

    def run(self):

        while not self.end:
            message = self.client_socket.recv(1024)
            msg_client = decoded_msgs(message)
            self.manage_msg(msg_client)


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


def main():
    port = utils.arguments_parser_server()
    server_socket_thread = ServerSocketThread(port)
    server_socket_thread.daemon = True
    server_socket_thread.start()
    input("Server started at {}:{} \n".format("127.0.0.1", port))


if __name__ == "__main__":
    main()
