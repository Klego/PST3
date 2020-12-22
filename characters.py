class Characters:
    def __init__(self, skill, hp_max, dmg):
        self.skill = skill
        self.hp_max = hp_max
        self.stats = {"HP": hp_max, "DMG": dmg, "timeSkill": 0, "alive": True}

    def __str__(self):
        return "The {} -> Stats: {}HP and {}DMG. \n\t\tSkill: {}".format(self.__class__.__name__,
                                                                         self.stats["HP"], self.stats["DMG"],
                                                                         self.skill)

    def get_skill(self):
        return self.skill

    def get_hp_max(self):
        return self.hp_max

    def get_hp(self):
        return self.stats["HP"]

    def get_dmg(self):
        return self.stats["DMG"]

    def get_timeskill(self):
        return self.stats["timeSkill"]

    def get_alive(self):
        return self.stats["alive"]

    def set_hp(self, hp):
        self.stats["HP"] = hp

    def set_hp_max(self):
        self.stats["HP"] = self.hp_max

    def set_dmg(self, dmg):
        self.stats["DMG"] = dmg

    def set_timeskill(self, timeskill):
        self.stats["timeSkill"] = timeskill

    def update_timeskill(self):
        self.stats["timeSkill"] += 1

    def set_alive(self, alive):
        self.stats["alive"] = alive

    def attack(self, enemy, dmg, current_round, name):
        hp = enemy.stats["HP"]
        if enemy.stats["alive"]:
            if self.__class__.__name__ == "Procrastinator":
                dmg += (current_round - 1)
            hp -= dmg
            if hp <= 0:
                enemy.stats["HP"], hp = 0, 0
                enemy.stats["alive"] = False
            else:
                enemy.stats["HP"] = hp
            msg = "\nThe {} ({}) did {} damage to {}. " \
                  "{} has {}hp left.".format(self.__class__.__name__, name, dmg,
                                             enemy.name, enemy.name, hp)
            return msg

    # hp can't be higher than hp_max
    def add_hp(self):
        hp = None
        if self.__class__.__name__ == Bookworm.__name__:
            hp = self.stats["HP"] + (Bookworm().hp_max * 0.25)
            hp = Bookworm().hp_max if hp > Bookworm().hp_max else hp
        elif self.__class__.__name__ == Worker.__name__:
            hp = self.stats["HP"] + (Worker().hp_max * 0.25)
            hp = Worker().hp_max if hp > Worker().hp_max else hp
        elif self.__class__.__name__ == Whatsapper.__name__:
            hp = self.stats["HP"] + (Whatsapper().hp_max * 0.25)
            hp = Whatsapper().hp_max if hp > Whatsapper().hp_max else hp
        elif self.__class__.__name__ == Procrastinator.__name__:
            hp = self.stats["HP"] + (Procrastinator().hp_max * 0.25)
            hp = Procrastinator().hp_max if hp > Procrastinator().hp_max else hp
        self.stats["HP"] = hp


class Bookworm(Characters):
    def __init__(self, skill="Revives one player (4 rounds)", hp_max=25, dmg=9):
        super().__init__(skill, hp_max, dmg)
        self.stats["timeSkill"] = 4


class Worker(Characters):
    def __init__(self, skill="1.5 * (DMG + DMG roll) damage to one enemy (3 rounds)", hp_max=4, dmg=10):
        super().__init__(skill, hp_max, dmg)
        self.stats["timeSkill"] = 3


class Procrastinator(Characters):
    def __init__(self,
                 skill="DMG + DMG roll + stage level to all the enemies after the third round of each stage and once "
                       "per stage.",
                 hp_max=30, dmg=6):
        super().__init__(skill, hp_max, dmg)
        self.stats["usedSkill"] = False

    def get_used_skill(self):
        return self.stats["usedSkill"]

    def set_used_skill(self, used_skill):
        self.stats["usedSkill"] = used_skill


class Whatsapper(Characters):
    def __init__(self, skill="Heals 2*DMG to one player (3 rounds)", hp_max=20, dmg=6):
        super().__init__(skill, hp_max, dmg)
        self.stats["timeSkill"] = 3
