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


def list_players_in_games():
    global games
    global clients_games
    players_in_game = 0
    available_games = ""
    if games:
        for i in games.keys():
            players = i.get_players()
            for j in games.values():
                if i == j:
                    players_in_game += 1
        available_games = available_games + str(i) + ".- Players: " + str(players_in_game) + "/" + str(players) + "\t"
    else:
        available_games = "There are no games available. Please, create a new game."

    return available_games


def manage_msg(decoded_msg, c_socket, c_address):
    global clients_games
    global games
    global awaiting_players
    if decoded_msg["Protocol"] == PROTOCOL_JOIN:
        name = decoded_msg["Name"]
        #TENEIS QUE ASIGNAR EL ATRIBUTO NAME AL NOMBRE
        print("(WELCOME) " + name + " joined the server")
        server_reply = craft_welcome()
        c_socket.sendall(server_reply)
    if decoded_msg["Protocol"] == PROTOCOL_SEND_SERVER_OPTION:
        option = decoded_msg["Option"]
        players = decoded_msg["Players"]
        stages = decoded_msg["Stages"]
        id_game = 1
        if option == 1:
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
                print("(EXIT) " + name + " disconnected by SERVER (No new game slots)")
                reason = "SERVER: There are no empty slots for a new game"
                server_reply = craft_send_dc_server(reason)
                c_socket.sendall(server_reply)
                ClientThread.set_disconnected()
        if option == 2:
            available_games = list_players_in_games()
            server_reply = craft_send_games(available_games)
            c_socket.sendall(server_reply)
        if option == 3:
            print("(EXIT) " + name + " disconnected")
            reason = "SERVER: Client disconnected by himself"
            server_reply = craft_send_dc_server(reason)
            c_socket.sendall(server_reply)
            ClientThread.set_disconnected()

    if decoded_msg["Protocol"] == PROTOCOL_SEND_CHARACTER:
        option = decoded_msg["Option"]
        id_game = awaiting_players[c_address]
        game = games[id_game]
        players = game.get_players()
        players_count = 0
        # check how many players in game
        for i in clients_games.values():
            if i == id_game:
                players_count += 1
        if players_count < players:
            if players == 1:
                clients_games[c_address] = id_game
                del awaiting_players[c_address]
                character = game.choose_character(option)
                game.set_player(character, players_count)
                game.play()
            else:
                clients_games[c_address] = id_game
                del awaiting_players[c_address]
                character = game.choose_character(option)
                game.set_player(character, players_count)
                server_reply = craft_wait()
                c_socket.sendall(server_reply)
        else:
            del awaiting_players[c_address]
            reason = "SERVER: There are no empty slots for the game"
            server_reply = craft_send_dc_server(reason)
            c_socket.sendall(server_reply)
            print("(EXIT) " + name + " disconnected by SERVER (No new slots in selected game)")
            ClientThread.set_disconnected()
    if decoded_msg["Protocol"] == PROTOCOL_SEND_GAME_CHOICE:
        option = decoded_msg["Option"]
        #COMPROBAR SI EL JUEGO SELECCIONADO ESTA O NO LLENO Y ENVIAR SEND_VALID_GAME
        #SEGUIDAMENTE METER EN LA LISTA DE AWAITING PLAYERS AL JUGADOR Y ENVIARLE EL MENU DE PERSONAJES



class ClientThread(threading.Thread) :
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.name = ""
        self.end = False

    def set_disconnected(self):
        self.end = True


    def run(self):

        while not self.end:
            message = self.client_socket.recv(1024)
            msg_client = decoded_msgs(message)
            manage_msg(msg_client, self.client_socket, self.client_address, self.name)


class ServerSocketThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.stop = False
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((socket.gethostname(), self.port))
        self.server_socket.listen(20)

    def run(self):
        while True:
            close_connection = False
            print("Server started at " + str(socket.gethostname()) + ":" + str(self.port))
            client_socket, client_address = self.server_socket.accept()
            client_thread = ClientThread(client_socket, client_address)
            client_thread.start()


def main():
    port = utils.arguments_parser_server()
    server_socket_thread = ServerSocketThread(port)
    server_socket_thread.daemon = True
    server_socket_thread.start()

if __name__ == "__main__":
    main()
