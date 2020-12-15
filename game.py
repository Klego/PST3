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

    def get_players(self):
        return self.players

    def set_player(self, character, i):
        self.dicPlayer["Player " + str(i + 1)] = character

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
        else:
            print("Option not recognized.")
        return character

    def show_chars_attributes(self):
        if len(self.dicPlayer) > 0:
            for key in self.dicPlayer:
                return "{} - {}".format(key, self.dicPlayer[key])

    @staticmethod
    def __random_damage(dmg):
        return random.randint(1, dmg)

    def __create_monster(self):
        print("\n\t\t---- CURRENT MONSTERS ----")
        print("\n\t++++++++++++++++++++++++++++++++++++++")
        for i in range(NUMBER_ENEMIES):
            n = random.randint(1, NUMBER_ENEMIES)
            self.enemies.append(Enemy(n, self.current_stage))

        if len(self.enemies) > 0:
            for enemy in self.enemies:
                print("\t" + enemy.__str__())
        print("\t++++++++++++++++++++++++++++++++++++++")

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

    def prepare_char_attack(self, character, player, dmg):
        n = random.randint(0, NUMBER_ENEMIES - 1)
        while not self.enemies[n].get_alive():
            n = random.randint(0, NUMBER_ENEMIES - 1)
        if self.enemies[n].get_alive():
            enemy = self.enemies[n]
            character.attack(player, enemy, dmg, self.current_round)

    def prepare_enemy_attack(self, enemy):
        n = random.randint(1, len(self.dicPlayer))
        while not self.dicPlayer["Player " + str(n)].get_alive():
            n = random.randint(1, len(self.dicPlayer))
        if self.dicPlayer["Player " + str(n)].get_alive():
            dmg = self.__random_damage(enemy.get_dmg())
            player = "Player " + str(n)
            enemy.attack(player, self.dicPlayer[player], dmg, self.current_stage)

    def heal(self, character):
        n = random.randint(1, len(self.dicPlayer))
        while not self.dicPlayer["Player " + str(n)].get_alive() \
                or self.dicPlayer["Player " + str(n)].get_hp() == self.dicPlayer["Player " + str(n)].get_hp_max():
            n = random.randint(1, len(self.dicPlayer))
        cure = character.get_dmg() * 2
        player = "Player " + str(n)
        hp = self.dicPlayer[player].get_hp()
        hp += cure
        if hp > self.dicPlayer["Player " + str(n)].get_hp_max():
            hp = self.dicPlayer["Player " + str(n)].get_hp_max()
        else:
            hp = hp
        self.dicPlayer[player].set_hp(hp)
        print("The {} has been healed with the following cure: {}. Current HP: {}.".format(player, cure, hp))

    def app_bookworm_skill(self, character):
        list_to_revive = []
        players_name = ""
        print("********************************************************")
        aux_count = 1
        for p in self.dicPlayer:
            if self.dicPlayer[p] != character and not self.dicPlayer[p].get_alive():
                list_to_revive.append(p)
                players_name += p + ", "
                print("{}. - {}".format(aux_count, self.dicPlayer[p]))
                aux_count += 1
        aux = False
        print("********************************************************")
        in_message = "Who do you want to revive? "
        while not aux:
            try:
                in_revive = input(in_message.format(len(list_to_revive),
                                                    players_name[:len(players_name) - 2]))
                for i in range(0, len(list_to_revive)):
                    if (int(in_revive) - 1) == i:
                        aux = True
                        revive_player = list_to_revive[int(in_revive) - 1]
                        self.dicPlayer[revive_player].set_hp_max()
                        self.dicPlayer[revive_player].set_alive(True)
                        character.set_timeskill(0)
                        print("OMG!!!!! This player is alive again!!!!! \n{}".format(
                            self.dicPlayer[revive_player]))
                    else:
                        in_message = "Incorrect choice. Choice must be between 1 and {} ({}). " \
                                     "\nWho do you want to revive?:"
            except ValueError:
                print("You must choose a player using an integer number.")

    def app_worker_skill(self, character, message, player):
        if character.get_timeskill() >= 3:
            print(message.format(character.__class__.__name__, player))
            dmg = (character.get_dmg() + self.__random_damage(character.get_damage())) * 1.5
            self.prepare_char_attack(character, player, dmg)
            character.set_timeskill(0)
            return True
        else:
            print("The skill is currently in cooldown for {} more rounds.".format(
                3 - character.get_timeskill()))
            return False

    def app_whatsapper_skill(self, character, message, player):
        not_hp_max = False
        for i in self.dicPlayer:
            if self.dicPlayer[i].get_hp_max() > self.dicPlayer[i].get_hp() \
                    and self.dicPlayer[i].get_alive():
                not_hp_max = True
        if not_hp_max:
            if character.get_timeskill() >= 3:
                print(message.format(character.__class__.__name__, player))
                self.heal(character)
                character.set_timeskill(0)
                return True
            else:
                print("The skill is currently in cooldown for {} more rounds.".format(
                    3 - character.get_timeskill()))
                return False
        else:
            print("All players have their maximum HP, so the skill will not be used.")
            return False

    def app_procrastinator_skill(self, character, message, player):
        if self.current_round >= 3 and not character.get_used_skill():
            print(message.format(character.__class__.__name__, player))
            dmg = self.__random_damage(character.get_dmg()) + character.get_dmg() + self.current_stage
            for enemy in self.enemies:
                if enemy.get_alive():
                    character.attack(player, enemy, dmg, self.current_round)
            character.set_used_skill(True)
            return True
        else:
            print("This skill can only be used after the third round of each stage "
                  "and once per stage, so it will not be used.")
            return False

    def __turn(self, player, enemy):
        if player is not None:
            correct_option = False
            character = self.dicPlayer[player]
            character.update_time_skill()
            while not correct_option:
                option = input("{} ({}). What are you going to do "
                               "a (attack) or s (skill)?: ".format(character.__class__.__name__, player))

                if option.lower() == "a":
                    correct_option = True
                    dmg = self.__random_damage(character.get_dmg())
                    self.prepare_char_attack(character, player, dmg)

                elif option.lower() == "s":
                    correct_option = True
                    message = "The {} ({}) used his/her skill."
                    if character.__class__.__name__ == Bookworm.__name__:
                        if self.__check_chars_dead():
                            if character.get_timeskill() >= 4:
                                print(message.format(character.__class__.__name__, player))
                                self.app_bookworm_skill(character)
                            else:
                                print("The skill is currently in cooldown for {} more rounds.".format(
                                    4 - character.get_timeskill()))
                                correct_option = False
                        else:
                            print("All players are alive, so the skill will not be used.")
                            correct_option = False
                    elif character.__class__.__name__ == Worker.__name__:
                        correct_option = self.app_worker_skill(character, message, player)
                    elif character.__class__.__name__ == Whatsapper.__name__:
                        correct_option = self.app_whatsapper_skill(character, message, player)
                    elif character.__class__.__name__ == Procrastinator.__name__:
                        correct_option = self.app_procrastinator_skill(character, message, player)
                else:
                    print("Option not recognized.")
                    correct_option = False

        elif enemy is not None:
            self.prepare_enemy_attack(enemy)

    def __play_round(self):
        while self.__check_monsters_alive() and self.__check_chars_alive():
            self.current_round += 1
            print("\n+++++++++++++++++++++++++++++++ Round %s +++++++++++++++++++++++++++++++" % self.current_round)
            message = "\n\t\t\t\t---------------------------"
            message += "\n\t\t\t\t     - {} TURN -"
            message += "\n\t\t\t\t---------------------------"
            if self.__check_chars_alive():
                print(message.format('PLAYERS'))
                for player in self.dicPlayer:
                    if self.dicPlayer[player].get_alive():
                        if self.__check_monsters_alive():
                            self.__turn(player, None)
                    else:
                        print("The {} ({}) has been defeated. It can not make "
                              "any move until revived.".format(self.dicPlayer[player].__class__.__name__, player))
            # enemies turn
            if self.__check_monsters_alive():
                print(message.format('MONSTERS'))
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
            print("Players won this level. Continue next stage.")
            print("Every character will be added +1/4 HP. These are the updated attributes of each player: ")
            self.show_chars_attributes()

    def check_end_game(self):
        if not self.__check_chars_alive() and self.__check_monsters_alive():
            print("All characters have been defeated. Try again. GAME OVER")
        if not self.__check_monsters_alive() and self.current_stage == int(self.stages):
            print("All the stages have been cleared. CONGRATS! YOU WON THE GAME!")
        else:
            pass

    def play(self):
        for s in range(int(self.stages)):
            self.current_stage = stage + 1
            if len(self.enemies) == 0:
                message = "\n\t\t************************" \
                          "\n\t\t       * STAGE %s *" \
                          "\n\t\t************************" % self.current_stage
                self.__create_monster()

            self.__play_round()

        if self.__check_chars_alive() and not self.__check_monsters_alive():
            self.prepare_new_stage()
