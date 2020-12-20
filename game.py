from characters import Bookworm, Worker, Procrastinator, Whatsapper
from enemies import Enemy
import random

NUMBER_ENEMIES = 4


class Game:

    def __init__(self, players, stages):
        self.players = players
        self.stages = stages
        self.enemies = []
        self.dicPlayer = {}
        self.current_stage = 0
        self.current_round = 0
        self.message = ""
        self.check_turn = []

    def get_players(self):
        return self.players

    def set_player(self, character, nick):
        self.dicPlayer[nick] = character

    def get_dic_player(self, name):
        return self.dicPlayer[name]

    def set_turn(self, name):
        self.check_turn.append(name)

    def get_check_turn(self):
        return self.check_turn

    def clean_check_turn(self):
        self.check_turn.clear()

    @staticmethod
    def display_chars_menu():
        chars_list = [Bookworm, Worker, Whatsapper, Procrastinator]
        num = 1
        msg = "\n*********** AVAILABLE CHARACTERS ***********"
        for i in chars_list:
            msg += "\n{} - {}".format(num, i())
            num += 1
        return msg

    @staticmethod
    def choose_character(option):
        character = None
        if option == "1":
            character = Bookworm()
        elif option == "2":
            character = Worker()
        elif option == "3":
            character = Whatsapper()
        elif option == "4":
            character = Procrastinator()
        return character

    def show_chars_attributes(self):
        msg = ""
        if len(self.dicPlayer) > 0:
            for key in self.dicPlayer:
                msg += " (" + key + ") - %s" % self.dicPlayer[key]
        return msg

    @staticmethod
    def __random_damage(dmg):
        return random.randint(1, dmg)

    def __create_monster(self):
        msg = "\n\t\t---- CURRENT MONSTERS ----"
        msg += "\n\t++++++++++++++++++++++++++++++++++++++"
        for i in range(NUMBER_ENEMIES):
            n = random.randint(1, NUMBER_ENEMIES)
            self.enemies.append(Enemy(n, self.current_stage))

        if len(self.enemies) > 0:
            for enemy in self.enemies:
                msg += "\n\t" + enemy.__str__()
        msg += "\n\t++++++++++++++++++++++++++++++++++++++"
        return msg

    # checks whether there is at least one dead character or not
    def __check_chars_dead(self):
        dead = False
        for char in self.dicPlayer:
            if not self.dicPlayer[char].get_alive():
                dead = True
        return dead

    # checks whether there is at least one character alive or not
    def __check_chars_alive(self):
        alive = False
        for char in self.dicPlayer:
            if self.dicPlayer[char].get_alive():
                alive = True
        return alive

    # checks whether there is at least one monster alive or not
    def __check_monsters_alive(self):
        alive = False
        for enemy in self.enemies:
            if enemy.get_alive():
                alive = True
        return alive

    def prepare_char_attack(self, character, dmg, name):
        n = random.randint(0, NUMBER_ENEMIES - 1)
        while not self.enemies[n].get_alive():
            n = random.randint(0, NUMBER_ENEMIES - 1)
        if self.enemies[n].get_alive():
            enemy = self.enemies[n]
            msg = character.attack(enemy, dmg, self.current_round, name)
            return msg

    # comprobar ataque de los enemigos
    def turn_enemy_attack(self):
        jug = ""
        x = ""
        msg = ""
        for enemy in self.enemies:
            if enemy.get_alive():
                if self.__check_chars_alive():
                    cont = 0
                    n = random.randint(0, len(self.dicPlayer) - 1)
                    for x in self.dicPlayer.keys():
                        cont += 0
                        if n == cont:
                            jug = self.dicPlayer[x]
                    while not jug.get_alive():
                        n = random.randint(0, len(self.dicPlayer) - 1)
                        for x in self.dicPlayer.keys():
                            cont += 0
                            if n == cont:
                                jug = self.dicPlayer[x]
                    if jug.get_alive():
                        dmg = self.__random_damage(enemy.get_dmg())
                        msg += "\n" + enemy.attack(x, jug, dmg, self.current_stage)
        msg += "\n+++++++++++++++++++++++++++++ End Round %s +++++++++++++++++++++++++++++" % self.current_round
        return msg

    # comprobar bookworm
    def heal(self, character, name):
        jug = name
        cont = 0
        n = random.randint(0, len(self.dicPlayer) - 1)
        for x in self.dicPlayer.keys():
            cont += 0
            if n == cont:
                jug = self.dicPlayer[x]
        while (not jug.get_alive()) or (jug.get_hp() == jug.get_hp_max()):
            n = random.randint(0, len(self.dicPlayer) - 1)
            for x in self.dicPlayer.keys():
                cont += 1
                if n == cont:
                    jug = self.dicPlayer[x]
        cure = character.get_dmg() * 2
        hp = jug.get_hp()
        hp += cure
        if hp > jug.get_hp_max():
            hp = jug.get_hp_max()
        else:
            hp = hp
        jug.set_hp(hp)
        msg = "\nThe {} has been healed with the following cure: {}. Current HP: {}.".format(name, cure, hp)
        return msg

    def char_resurrect(self, list_to_revive, option, name):
        msg = ""
        in_revive = option
        if len(list_to_revive) > 0:
            for i in range(0, len(list_to_revive)):
                if (int(in_revive) - 1) == i:
                    revive_player = list_to_revive[int(in_revive) - 1]
                    self.dicPlayer[revive_player].set_hp_max()
                    self.dicPlayer[revive_player].set_alive(True)
                    character = self.dicPlayer[name]
                    character.set_timeskill(0)
                    msg = "OMG!!!!! This player is alive again!!!!! \n{}".format(self.dicPlayer[revive_player])
        else:
            pass
        return msg

    def app_bookworm_skill(self, character):
        list_to_revive = []
        players_name = ""
        msg = "\n********************************************************"
        aux_count = 1
        for p in self.dicPlayer:
            if self.dicPlayer[p] != character and not self.dicPlayer[p].get_alive():
                list_to_revive.append(p)
                players_name += p + ", "
                msg += "\n{}. - {}".format(aux_count, self.dicPlayer[p])
                aux_count += 1
        msg += "\n********************************************************"
        if len(list_to_revive) > 0:
            msg += "\nWho do you want to revive? "
        else:
            msg = "\nThere isn't anyone dead to revive"
        return msg, list_to_revive

    def app_worker_skill(self, character, message, name):
        if character.get_timeskill() >= 3:
            msg = message.format(character.__class__.__name__, name)
            dmg = (character.get_dmg() + self.__random_damage(character.get_dmg())) * 1.5
            msg += self.prepare_char_attack(character, dmg, name)
            character.set_timeskill(0)
        else:
            msg = "\nThe skill is currently in cooldown for {} more rounds.".format(
                3 - character.get_timeskill())
        #     Pedir otra vez comando si no se puede enviar
        return msg

    def app_whatsapper_skill(self, character, message, name):
        not_hp_max = False
        for i in self.dicPlayer:
            if self.dicPlayer[i].get_hp_max() > self.dicPlayer[i].get_hp() \
                    and self.dicPlayer[i].get_alive():
                not_hp_max = True
        if not_hp_max:
            if character.get_timeskill() >= 3:
                new_msg = message.format(character.__class__.__name__, name)
                new_msg += "\n" + self.heal(character, name)
                character.set_timeskill(0)
            else:
                new_msg = "\nThe skill is currently in cooldown for {} more rounds.".format(3 - character.get_timeskill())
        else:
            # pedir otra vez el comando
            new_msg = "\nAll players have their maximum HP, so the skill will not be used."
        return new_msg

    def app_procrastinator_skill(self, character, message, name):
        if self.current_round >= 3 and not character.get_used_skill():
            new_msg = message.format(character.__class__.__name__, name)
            dmg = self.__random_damage(character.get_dmg()) + character.get_dmg() + self.current_stage
            for enemy in self.enemies:
                if enemy.get_alive():
                    new_msg += character.attack(enemy, dmg, self.current_round, name)
            character.set_used_skill(True)
        else:
            new_msg = "\nThis skill can only be used after the third round of each stage " \
                      "and once per stage, so it will not be used."
        return new_msg

    def choose_character_option(self, option, name):
        list_to_revive = []
        new_msg = ""
        character = self.dicPlayer[name]
        character.update_timeskill()
        if option.lower() == "a":
            dmg = self.__random_damage(character.get_dmg())
            msg = self.prepare_char_attack(character, dmg, name)
            return msg
        elif option.lower() == "s":
            message = "The {} ({}) used his/her skill."
            if character.__class__.__name__ == Bookworm.__name__:
                if self.__check_chars_dead():
                    if character.get_timeskill() >= 4:
                        new_msg = message.format(character.__class__.__name__, name)
                        msg_book, list_to_revive = self.app_bookworm_skill(character)
                        new_msg += msg_book
                        return new_msg, list_to_revive
                    else:
                        new_msg = "The skill is currently in cooldown for {} more rounds.".format(
                            4 - character.get_timeskill())
                else:
                    new_msg = "All players are alive, so the skill will not be used."
            elif character.__class__.__name__ == Worker.__name__:
                new_msg = self.app_worker_skill(character, message, name)
            elif character.__class__.__name__ == Whatsapper.__name__:
                new_msg = self.app_whatsapper_skill(character, message, name)
            elif character.__class__.__name__ == Procrastinator.__name__:
                new_msg = self.app_procrastinator_skill(character, message, name)
        return new_msg

    def check_game(self):
        check_option = 0
        if self.__check_monsters_alive() and self.__check_chars_alive():
            check_option = 1
        if self.__check_chars_alive() and not self.__check_monsters_alive():
            check_option = 2
        if not self.__check_chars_alive() and self.__check_monsters_alive():
            check_option = 3
        if not self.__check_monsters_alive() and self.current_stage == int(self.stages):
            check_option = 4
        return check_option

    def __play_round(self):
        while self.__check_monsters_alive() and self.__check_chars_alive():

            if self.__check_chars_alive():
                for player in self.dicPlayer:
                    if self.dicPlayer[player].get_alive():
                        if self.__check_monsters_alive():
                            self.__turn(player, None)
                    else:
                        print("The {} ({}) has been defeated. It can not make "
                              "any move until revived.".format(self.dicPlayer[player].__class__.__name__, player))

            # enemies turn
            if self.__check_monsters_alive():
                for enemy in self.enemies:
                    if enemy.stats["alive"]:
                        if self.__check_chars_alive():
                            self.__turn(None, enemy)
            print("+++++++++++++++++++++++++++++ End Round %s +++++++++++++++++++++++++++++" % self.current_round)

    def prepare_new_stage(self):
        self.enemies.clear()
        Enemy.numerated_monster = 1
        self.current_round = 0
        for player in self.dicPlayer:
            self.dicPlayer[player].add_hp()
            if self.dicPlayer[player].__class__.__name__ == Procrastinator.__name__:
                self.dicPlayer[player].set_used_skill(False)
                self.dicPlayer[player].set_timeskill(0)
        if self.current_stage < int(self.stages):
            msg = "Players won this level. Continue next stage."
            msg += "Every character will be added +1/4 HP. These are the updated attributes of each player: "
            msg += self.show_chars_attributes()
        else:
            msg = "STAGES_CLEARED"
        return msg

    def show_turn(self):
        message = "\n\t\t\t\t---------------------------"
        message += "\n\t\t\t\t     - {} TURN -"
        message += "\n\t\t\t\t---------------------------"
        return message

    def show_round(self):
        self.current_round += 1
        message = "\n+++++++++++++++++++++++++++++++ Round %s +++++++++++++++++++++++++++++++" % self.current_round
        message += self.show_turn()
        return message

    def show_stage(self):
        self.current_stage = self.current_stage + 1
        if len(self.enemies) == 0:
            message = "\n\t\t************************" \
                      "\n\t\t       * STAGE %s *" \
                      "\n\t\t************************" % self.current_stage
            message += self.__create_monster()
            return message
