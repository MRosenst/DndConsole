# TODO implement this properly
class Spell:
    def __init__(self, name, description, lvl, school, casting_time, spell_range, components,
                 duration, is_prepared=False, attack=None):
        self.name = name
        self.description = description
        self.lvl = lvl
        self.is_prepared = is_prepared
        self.attack = attack
        self.school = school
        self.casting_time = casting_time
        self.spell_range = spell_range
        self.components = components
        self.duration = duration
