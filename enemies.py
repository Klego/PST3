class Enemy:

    def __init__(self, option, stage):
        self.__create_enemy(option, stage)

    def __str__(self):
        return "{} -> Stats: {}HP and {}DMG.".format(self.name, self.stats["HP"], str(self.stats["DMG"]))

    def __create_enemy(self, option, stage):
        option = option - 1 if option == 2 and stage < 4 else option
        if option == 1:
            # 20
            self.name = "Partial Exam"
            self.stats = {"HP": 2, "DMG": 6, "alive": True}
        elif option == 2:
            # 40
            self.name = "Final Exam"
            self.stats = {"HP": 4, "DMG": 12, "alive": True}
        elif option == 3:
            # 8
            self.name = "Theoretical class"
            self.stats = {"HP": 8, "DMG": 4, "alive": True}
        elif option == 4:
            # 15
            self.name = "Teacher"
            self.stats = {"HP": 1, "DMG": 7, "alive": True}

    def attack(self, name, character, dmg, stage):
        msg = ""
        hp = character.stats["HP"]
        if self.name == "Theoretical class":
            dmg += stage
        elif self.name == "Teacher" and dmg == 7:
            dmg *= 2

        if character.stats["alive"]:
            hp -= dmg
            if hp <= 0:
                character.stats["HP"], hp = 0, 0
                character.stats["alive"] = False
            else:
                character.stats["HP"] = hp

            msg = "The {} did {} damage to {} ({}). {} has {}hp left.".format(self.name,
                                                                              dmg, character.__class__.__name__, name,
                                                                              character.__class__.__name__, hp)
        return msg

    def get_hp(self):
        return self.stats["HP"]

    def get_dmg(self):
        return self.stats["DMG"]

    def get_alive(self):
        return self.stats["alive"]

    def set_hp(self, hp):
        self.stats["HP"] = hp

    def set_dmg(self, dmg):
        self.stats["DMG"] = dmg

    def set_die(self):
        self.stats["alive"] = False
