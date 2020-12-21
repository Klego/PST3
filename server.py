# -- Autores --
# Paula Gallego Vieira
# Sonia Liceth Quevedo Becerra
# Justo Martín Collado
# ---------------------


#from game import *
import socket
import threading
from protocols_messages import *
import inputcontrol

games = {}
clients_games = {}
awaiting_players = {}
dic_sockets = {}
players_names = {}
dic_threads = {}

# BORRAR PLAYERS DESCONECTADOS DEL JUEGO siempre que se salga del juego (mirar otras funciones)
# Y COMPROBAR FUNCION
# me da error cuando ingreso un mensaje para enviar pero despues quiero que siga haciendo cosas
# Recorrer los nombres de los jugadores para ponerlo linea 244


def list_players_in_games():
    global games
    global clients_games
    players_in_game = 0
    available_games = ""
    i = 0
    players = 0
    if games:
        for i in games.keys():
            players = games[i].get_players()
            for j in clients_games.values():
                if i == j:
                    players_in_game += 1
        available_games = available_games + str(i) + ".- Players: " + str(players_in_game) + "/" + str(players) + "\t"
    else:
        available_games = "NO_GAMES"

    return available_games


def broadcast_clients(id_game, server_reply, c_address):
    global clients_games
    global games
    global dic_sockets
    for i in clients_games.keys():
        if clients_games[i] == id_game:
            for j in dic_sockets.keys():
                if j == i and j != c_address:
                    #dic_sockets[j].sendall(server_reply)
                    send_one_message(dic_sockets[j], server_reply)

def creator_name(id_game):
    list_names = []
    for i in clients_games.keys():
        if clients_games[i] == id_game:
            for j in players_names.keys():
                if j == i:
                    list_names.append(players_names[j])
    creators_name = list_names[0]
    return creators_name


def list_players_names(id_game):
        list_names = []
        for i in clients_games.keys():
            if clients_games[i] == id_game:
                for j in players_names.keys():
                    if j == i:
                        list_names.append(players_names[j])
        return list_names


def send_to_all_players(id_game, server_reply):
    global clients_games
    global games
    global dic_sockets
    for i in clients_games.keys():
        if clients_games[i] == id_game:
            for j in dic_sockets.keys():
                if j == i:
                    #dic_sockets[j].sendall(server_reply)
                    send_one_message(dic_sockets[j], server_reply)


def manage_join(name, c_socket):
    print("(WELCOME) " + name + " joined the server")
    server_reply = craft_welcome()
    #c_socket.sendall(server_reply)
    send_one_message(c_socket, server_reply)


def manage_disconnection(reason, c_socket, client_thread):
    server_reply = craft_send_dc_server(reason)
    #c_socket.sendall(server_reply)
    send_one_message(c_socket, server_reply)
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
            #c_socket.sendall(server_reply)
            send_one_message(c_socket, server_reply)
        else:
            print("(EXIT) " + name + " disconnected by SERVER (No new game slots)")
            reason = "SERVER: There are no empty slots for a new game"
            manage_disconnection(reason, c_socket, client_thread)
    elif option == "2":
        available_games = list_players_in_games()
        server_reply = craft_send_games(available_games)
        #c_socket.sendall(server_reply)
        send_one_message(c_socket, server_reply)
    elif option == "3":
        print("(EXIT) " + name + " disconnected")
        reason = "SERVER: Client disconnected by himself"
        manage_disconnection(reason, c_socket, client_thread)


def enter_game(c_address, id_game, c_socket, name, game, option, client_thread):
    global clients_games
    global games
    global awaiting_players
    global players_names
    clients_games[c_address] = id_game
    dic_sockets[c_address] = c_socket
    players_names[c_address] = name
    del awaiting_players[c_address]
    dic_threads[c_address] = client_thread
    character = game.choose_character(option)
    game.set_player(character, name)


def send_message(msg, c_socket):
    message = craft_server_msg(msg)
    #c_socket.sendall(message)
    send_one_message(c_socket, message)


def send_turn(id_game, c_address):
    global games
    global players_names
    global clients_games
    global dic_sockets
    game = games[id_game]
    for i in clients_games.keys():
        if clients_games[i] == id_game:
            for j in dic_sockets.keys():
                if j == i:
                    # dic_sockets[j].sendall(server_reply)
                    name = players_names[j]
                    ask_turn = craft_your_turn(game.get_dic_player(name), name)
                    send_one_message(dic_sockets[j], ask_turn)


def init_game(id, c_address):
    global games
    game = games[id]
    message = game.show_chars_attributes()
    message += game.show_stage()
    message += game.show_round()
    new_msg = message.format("PLAYERS")
    server_reply = craft_server_msg(new_msg)
    send_to_all_players(id, server_reply)
    send_turn(id, c_address)


def clear_dicts(id_game):
    global games
    global clients_games
    global players_names
    global dic_sockets
    global dic_threads

    for player in clients_games.keys():
        if clients_games[player] == id_game:
            del dic_sockets[player]
            del players_names[player]
            del dic_sockets[player]
            del dic_threads[player]
            del clients_games[player]
    del games[id_game]

def check_player_attack(game):
    print("entra?")
    all_players_attacked = False
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
            enter_game(c_address, id_game, c_socket, name, game, option, client_thread)
            init_game(id_game, c_address)
        else:
            enter_game(c_address, id_game, c_socket, name, game, option, client_thread)
            players_count = 0
            for i in clients_games.values():
                if i == id_game:
                    players_count += 1
            if players_count < players:
                server_reply = craft_wait()
                #c_socket.sendall(server_reply)
                send_one_message(c_socket, server_reply)
            else:
                # BROADCAST SENDALL TO THE CLIENTS CONNECTED TO THE GAME
                server_reply = craft_continue()
                broadcast_clients(id_game, server_reply, c_address)
                init_game(id_game, c_address)
    else:
        del awaiting_players[c_address]
        print("(EXIT) " + name + " disconnected by SERVER (No new slots in selected game)")
        reason = "SERVER: There are no empty slots for the game"
        manage_disconnection(reason, c_socket, client_thread)


def manage_bookworm(msg, name, c_address, c_socket):
    global games
    global clients_games
    option = msg["Option"]
    resurrection_list = msg["List"]
    id_game = clients_games[c_address]
    server_reply = games[id_game].char_resurrect(resurrection_list, option, name)
    games[id_game].set_turn(name)
    send_message(server_reply, c_socket)
    if not check_player_attack(games[id_game]):
        server_reply = craft_wait()
        #c_socket.sendall(server_reply)
        send_one_message(c_socket, server_reply)
    else:
        server_reply = craft_continue()
        broadcast_clients(id_game, server_reply, c_address)


def enemies_turn(id_game):
    global games
    msg = games[id_game].show_turn()
    msg = msg.format('MONSTERS')
    msg += "\n" + games[id_game].turn_enemy_attack()
    server_reply = craft_server_msg(msg)
    send_to_all_players(id_game, server_reply)


def game_check(id_game, c_address):
    global games
    game = games[id_game]
    check = game.check_game()
    if check == 1:
        message = game.show_round()
        msg = message.format("PLAYERS")
        server_reply = craft_server_msg(msg)
        send_to_all_players(id_game, server_reply)
        send_turn(id_game, c_address)
    elif check == 2:
        msg = game.prepare_new_stage()
        server_reply = craft_server_msg(msg)
        send_to_all_players(id_game, server_reply)
        message = game.show_stage()
        message += game.show_round()
        new_msg = message.format("PLAYERS")
        server_reply = craft_server_msg(new_msg)
        send_to_all_players(id_game, server_reply)
        send_turn(id_game, c_address)
    elif check == 3:
        players_in_game = list_players_names(id_game)
        names = ""
        for name in players_in_game:
            names += name + ", "
        names = names[:len(names) - 2]
        print("(GAMEEND) {} game ended. They lost.".format(names))
        win = False
        server_reply = craft_send_end_game(win)
        send_to_all_players(id_game, server_reply)
        for players in clients_games.keys():
            if clients_games[players] == id_game:
                dic_threads[players].set_disconnected()
    elif check == 4:
        players_in_game = list_players_names(id_game)
        names = ""
        for name in players_in_game:
            names += name + ", "
        names = names[:len(names) - 2]
        print("(GAMEEND) {} game ended. They won.".format(names))
        win = True
        server_reply = craft_send_end_game(win)
        send_to_all_players(id_game, server_reply)
        for players in clients_games.keys():
            if clients_games[players] == id_game:
                dic_threads[players].set_disconnected()
        clear_dicts(id_game)



def manage_char_command(msg, c_address, c_socket):
    global games
    global clients_games
    global players_names
    name = players_names[c_address]
    command = msg["Command"]
    id_game = clients_games[c_address]
    check = games[id_game].check_game()
    if check == 1:
        if games[id_game].dicPlayer[name].get_alive():
            if games[id_game].dicPlayer[name].__class__.__name__ == "Bookworm" and command == "s":
                msg, list_to_resurrect = games[id_game].choose_character_option(command, name)
                if len(list_to_resurrect) > 0:
                    # BOOKWORM'S SKILL SPECIAL MESSAGE PROTOCOL
                    server_reply = craft_bookworm_send(msg, list_to_resurrect)
                    #c_socket.sendall(server_reply)
                    send_one_message(c_socket, server_reply)
                else:
                    server_reply = craft_server_msg(msg)
                    #c_socket.sendall(server_reply)
                    send_one_message(c_socket, server_reply)
                    games[id_game].set_turn(name)
                    if not check_player_attack(games[id_game]):
                        server_reply = craft_wait()
                        #c_socket.sendall(server_reply)
                        send_one_message(c_socket, server_reply)
                    else:
                        server_reply = craft_continue()
                        broadcast_clients(id_game, server_reply, c_address)
            else:
                msg = games[id_game].choose_character_option(command, name)
                send_message(msg, c_socket)
                games[id_game].set_turn(name)
                if not check_player_attack(games[id_game]):
                    server_reply = craft_wait()
                    #c_socket.sendall(server_reply)
                    send_one_message(c_socket, server_reply)
                else:
                    server_reply = craft_continue()
                    broadcast_clients(id_game, server_reply, c_address)
                    enemies_turn(id_game)
                    game_check(id_game, c_address)
        else:
            #AQUÍ ESTÁ PUESTO LO DE ABAJO
            msg = "The {} ({}) has been defeated. It can not make any move until revived.\n Your turn is passed."
            new_msg = msg.format(games[id_game].get_dic_player(name).__class__.__name__, name)
            send_message(new_msg, c_socket)
            games[id_game].set_turn(name)
            if not check_player_attack(games[id_game]):
                server_reply = craft_wait()
                #c_socket.sendall(server_reply)
                send_one_message(c_socket, server_reply)
            else:
                server_reply = craft_continue()
                broadcast_clients(id_game, server_reply, c_address)
    else:
        game_check(id_game, c_address)
                # ESTO ESTÁ PUESTO ARRIBA
                # if games[id_game].get_dic_player(name).get_alive():
                #
                # else:
                #     msg = "The {} ({}) has been defeated. It can not make any move until revived."
                #     new_msg = msg.format(games[id_game].get_dic_player(name).__class__.__name__, name)
                #     send_message(new_msg, c_socket)


# cOMPROBAR FUNCION
def manage_game_choice(msg, c_socket, c_address, name):
    global games
    global clients_games
    global awaiting_players
    option = int(msg["Option"])
    num_players = 0
    game = games[option]
    players = game.players
    for i in clients_games.values():
        if i == option:
            num_players += 1
    if num_players < players:
        joined = True
        server_reply = craft_send_valid_game(joined)
        #c_socket.sendall(server_reply)
        send_one_message(c_socket, server_reply)
        awaiting_players[c_address] = option
        print("(JOIN) " + name + " joined " + creator_name(option) + "'s game")
        server_reply = craft_choose_character()
        #c_socket.sendall(server_reply)
        send_one_message(c_socket, server_reply)
    else:
        joined = False
        server_reply = craft_send_valid_game(joined)
        #c_socket.sendall(server_reply)
        send_one_message(c_socket, server_reply)


# BORRAR PLAYERS DESCONECTADOS DEL JUEGO siempre que se salga del juego (mirar otras funciones)
# Y COMPROBAR FUNCION
def manage_disconnected_player(client_thread):
    global clients_games
    global players_names
    print("(DC) " + players_names[client_thread.client_address] + " was disconnected")
    reason = "A player disconnected from the game."
    id_game = clients_games[client_thread.client_address]
    server_reply = craft_send_dc_server(reason)
    broadcast_clients(id_game, server_reply, client_thread.client_address)
    for clients in clients_games.keys():
        if clients_games[clients] == id_game:
            print("(DC) " + players_names[clients] + "has been disconnected")
    print("SERVER: Game " + str(id_game) + " was finished because a player was disconnected.")
    for players in clients_games.keys():
        if clients_games[players] == id_game:
            dic_threads[players].set_disconnected()
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
            message = recv_one_message(self.client_socket)
            msg_client = json.loads(message.decode())
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
    try:
        inputcontrol.clear_screen()
        port = inputcontrol.parse_args_server()
        port = inputcontrol.check_port(port)
        server_socket_thread = ServerSocketThread(port)
        server_socket_thread.daemon = True
        server_socket_thread.start()
        input("Server started at {}:{} \n".format("127.0.0.1", port))
    except inputcontrol.ArgumentError:
        print("\nProgram finished due to bad arguments.")
    except ConnectionResetError:
        print("\nThe connection to the client has been interrupted")
    except ConnectionRefusedError:
        print("\nCould not connect to the client")
    except KeyboardInterrupt:
        print("\nProgram finished due to CTRL+C command.")


if __name__ == "__main__":
    main()
