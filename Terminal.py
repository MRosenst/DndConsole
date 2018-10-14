import random
import re
from cmd import Cmd


class Character:
    def __init__(self, name, ability_scheme, max_hp, armor_class, coin):
        self.name = name
        self.ability_scheme = ability_scheme
        self.max_hp = max_hp
        self.hp = max_hp
        self.armor_class = armor_class
        self.coin = coin


class AbilityScheme:
    def __init__(self, base_abilities, specialties, proficiency_bonus):
        self.base_abilities = base_abilities
        self.specialties = specialties
        self.proficiency_bonus = proficiency_bonus

    def modifier(self, name: str) -> int:
        if name in self.base_abilities:
            res = (self.base_abilities[name] - 10) // 2

        elif name in self.specialties:
            ability = self.specialties[name]

            if ability[0] in self.base_abilities:
                res = self.modifier(ability[0])
            else:
                raise ValueError

            if ability[1]:
                res += self.proficiency_bonus
        else:
            raise ValueError

        return res

    def roll(self, name: str) -> int:
        return roll_die(1, 20, self.modifier(name))

    def passive_perception(self) -> int:
        return self.modifier('perception') + 10


class Item:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


class Weapon(Item):
    def __init__(self, name, weight, attack):
        Item.__init__(self, name, weight)
        self.attack = attack


# TODO implement this
class Armor(Item):
    def __init__(self, name, weight, ac, add_dex, limit_dex):
        Item.__init__(name, weight)
        self.ac = ac
        self.add_dex = add_dex
        self.limit_dex = limit_dex


# TODO consult about how to structure an attack
class Attack:
    def __init__(self, dmg_die, dmg_bonus, die_quantity=1, description=''):
        self.die_quantity = die_quantity
        self.dmg_die = dmg_die
        self.dmg_bonus = dmg_bonus
        self.description = description


# TODO implement this
class Class:
    def __init__(self, name, spell_list):
        self.name = name
        self.spell_list = spell_list


def roll_die(quantity, die, modifier):
    res = 0
    for i in range(quantity):
        res += random.randint(1, die)

    res += modifier
    return res


class Shell(Cmd):
    character: Character

    def __init__(self, character):
        Cmd.__init__(self)
        self.character = character

    # Override onecmd in order to split arguments and print returns
    def onecmd(self, line):
        """Mostly ripped from Python's cmd.py"""
        cmd, arg, line = self.parseline(line)
        arg = arg.lower().strip().split()  # <- added line
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            print(func(arg))  # <- also added line
            return  # <- edited this as well

    # Commands
    def do_show(self, args):
        out = ''
        if args[0] == 'stats':
            out += 'Character Stats:\n'
            for stat in self.character.ability_scheme.base_abilities:
                value = self.character.ability_scheme.base_abilities[stat]
                modifier = self.character.ability_scheme.modifier(stat)
                out += stat.title() + ' ' + str(value) + (16 - len(stat) - len(str(value))) * ' '
                out += '(' + ('+' if modifier >= 0 else '') + str(modifier) + ')\n'

            out += '-----\n'

            for stat in self.character.ability_scheme.specialties:
                modifier = self.character.ability_scheme.modifier(stat)
                out += stat.title() + (17 - len(stat)) * ' '
                out += '(' + ('+' if modifier >= 0 else '') + str(modifier) + ')\n'

        elif args[0] == 'hp':
            out += 'Health: ' + str(self.character.hp) + '/' + str(self.character.max_hp) + '\n'
        elif args[0] == 'ac':
            out += 'Armor Class: ' + str(self.character.armor_class) + '\n'
        elif args[0] == 'coin':
            out += 'Coin: ' + str(self.character.coin) + ' GP\n'
        elif args[0] == 'pp':
            out += 'Passive Perception: ' + str(self.character.ability_scheme.passive_perception()) + '\n'
        else:
            out += 'error: invalid arguments.'

        return out

    def do_roll(self, args):
        name = ' '.join(args)

        name = name.strip()
        out = 'error: invalid arguments.'

        try:
            out = self.character.ability_scheme.roll(name)
        except ValueError:
            pass

        if re.match(r'(\d*)d(\d+)(?:\+|-)?(\d*)', args[0]):
            groups = re.findall(r'(\d*)d(\d+)(?:\+|-)?(\d*)', name)[0]

            quantity = '1' if groups[0] == '' else groups[0]
            modifier = '0' if groups[2] == '' else groups[2]

            out = roll_die(int(quantity), int(groups[1]), int(modifier))

        return out

    def do_dmg(self, args):
        try:
            amount = int(args[0])
        except ValueError:
            return 'error: invalid arguments.'

        self.character.hp -= amount

        if -self.character.hp >= self.character.max_hp:
            self.character.hp = 0
            return self.character.name + ' has died.\n'
        elif self.character.hp < 0:
            self.character.hp = 0

        return self.do_show(['hp'])

    def do_heal(self, args):
        try:
            amount = int(args[0])
        except ValueError:
            if args[0] == 'full':
                amount = self.character.max_hp - self.character.hp
            else:
                return 'error: invalid arguments.'
        self.character.hp += amount

        if self.character.hp > self.character.max_hp:
            self.character.hp = self.character.max_hp

        return self.do_show(['hp'])

    def do_add(self, args):
        out = ''
        if args[0] == 'coin':
            try:
                self.character.coin += float(args[1])
                self.character.coin = round(self.character.coin, 2)
                out += self.do_show(['coin'])
            except ValueError:
                out += 'error: invalid coin amount.'

        else:
            out += 'error: invalid arguments.'

        return out


if __name__ == '__main__':
    base = {'strength': 18,
            'dexterity': 14,
            'constitution': 14,
            'intelligence': 12,
            'wisdom': 13,
            'charisma': 16,
            'sanity': 14,
            }

    special = {'acrobatics': ('dexterity', False),
               'animal handling': ('wisdom', True),
               'arcana': ('intelligence', False),
               'athletics': ('strength', True),
               'deception': ('charisma', False),
               'history': ('intelligence', False),
               'insight': ('wisdom', False),
               'intimidation': ('charisma', True),
               'investigation': ('intelligence', False),
               'medicine': ('wisdom', False),
               'nature': ('intelligence', False),
               'perception': ('wisdom', True),
               'performance': ('charisma', False),
               'persuasion': ('charisma', False),
               'religion': ('intelligence', False),
               'sleight of hand': ('dexterity', False),
               'stealth': ('dexterity', False),
               'survival': ('wisdom', True),
               }

    abilities = AbilityScheme(base, special, 3)
    galigus = Character('Galigus', abilities, 28, 21, 56.24)
    shell = Shell(galigus)
    shell.prompt = galigus.name + '> '
    shell.cmdloop()
