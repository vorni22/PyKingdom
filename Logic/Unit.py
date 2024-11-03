unit_classes = ['Melee', 'Ranged', 'Cavalry', 'Siege', 'Naval Melee', 'Naval Ranged', 'Civilian']

melee_units = ['Warrior', 'Swordsman', 'Man at Arms']
ranged_units = ['Slinger', 'Archer', 'Crossbowman']
cavalry_units = ['Horseman', 'Heavy Chariot', 'Knight']
siege_units = ['Catapult', 'Trebuchet', 'Bombard']
naval_melee_units = ['Galley', 'Caravel']
naval_ranged_units = ['Quadrireme', 'Frigate']
civilian_units = ['Settler']

class Unit:
    def __init__(self, type_id, name_id):
        self.type = unit_classes[type_id]
        self.name = None
        self.init_name(type_id, name_id)
        self.movement = 0
        self.init_movement(type_id, name_id)
        self.ranged_strength = 0
        self.init_ranged_strength(type_id, name_id)
        self.melee_strength = 0
        self.init_melee_strength(type_id, name_id)
        self.health_percentage = 100

    def rest(self):
        self.health_percentage = min(100, self.health_percentage + 20)

    def init_name(self, type_id, name_id):
        if type_id == 0:
            self.name = melee_units[name_id]
        elif type_id == 1:
            self.name = ranged_units[name_id]
        elif type_id == 2:
            self.name = cavalry_units[name_id]
        elif type_id == 3:
            self.name = siege_units[name_id]
        elif type_id == 4:
            self.name = naval_melee_units[name_id]
        elif type_id == 5:
            self.name = naval_ranged_units[name_id]
        elif type_id == 6:
            self.name = civilian_units[name_id]

    def init_movement(self, type_id, name_id):
        if type_id == 0:
            if name_id == 0 or name_id == 1:
                self.movement = 2
            elif name_id == 2:
                self.movement = 3
        elif type_id == 1:
            if name_id == 0 or name_id == 1:
                self.movement = 2
            elif name_id == 2:
                self.movement = 3
        elif type_id == 2:
            if name_id == 0 or name_id == 1:
                self.movement = 4
            elif name_id == 3:
                self.movement = 6
        elif type_id == 3:
            self.movement = 2
        elif type_id == 4:
            if name_id == 0:
                self.movement = 3
            elif name_id == 1:
                self.movement = 5
        elif type_id == 5:
            if name_id == 0:
                self.movement = 2
            elif name_id == 1:
                self.movement = 4
        elif type_id == 6:
            self.movement = 2
        else:
            raise TypeError("No such unit type")

    def init_ranged_strength(self, type_id, name_id):
        if type_id == 1:
            if name_id == 0:
                self.ranged_strength = 10
            elif name_id == 1:
                self.ranged_strength = 20
            elif name_id == 2:
                self.ranged_strength = 35
        elif type_id == 3:
            if name_id == 0:
                self.ranged_strength = 10
            elif name_id == 1:
                self.ranged_strength = 20
            elif name_id == 2:
                self.ranged_strength = 35
        elif type_id == 5:
            if name_id == 0:
                self.ranged_strength = 15
            elif name_id == 1:
                self.ranged_strength = 25

    def init_melee_strength(self, type_id, name_id):
        if type_id == 0:
            if name_id == 0:
                self.melee_strength = 10
            elif name_id == 1:
                self.melee_strength = 20
            elif name_id == 2:
                self.melee_strength = 35
        elif type_id == 1:
            if name_id == 0:
                self.melee_strength = 5
            elif name_id == 1:
                self.melee_strength = 10
            elif name_id == 2:
                self.melee_strength = 20
        elif type_id == 2:
            if name_id == 0:
                self.melee_strength = 10
            elif name_id == 1:
                self.melee_strength = 17
            elif name_id == 2:
                self.melee_strength = 30
        elif type_id == 3:
            if name_id == 0:
                self.melee_strength = 5
            elif name_id == 1:
                self.melee_strength = 10
            elif name_id == 2:
                self.melee_strength = 20
        elif type_id == 4:
            if name_id == 0:
                self.melee_strength = 15
            elif name_id == 1:
                self.melee_strength = 35
        elif type_id == 5:
            if name_id == 0:
                self.melee_strength = 10
            elif name_id == 1:
                self.melee_strength = 20

    def health_strength_loss(self):
        return (100 - self.health_percentage) * 0.1

    def calculate_melee_combat_with_unit(self, enemy_unit):
        diff = (self.melee_strength - self.health_strength_loss() -
                enemy_unit.melee_strength + enemy_unit.health_strength_loss())
        if diff > 0:
            self.health_percentage -= 0.4 * diff - 3
        else:
            self.health_percentage -= 2.5 * (-diff) - 5

    def calculate_ranged_combat_with_unit(self, enemy_unit):
        diff = (enemy_unit.ranged_strength - enemy_unit.health_strength_loss() -
                self.ranged_strength + self.health_strength_loss())
        if enemy_unit.type == unit_classes[1] and (self.type == unit_classes[4] or self.type == unit_classes[5]):
            diff = max(0, diff - 10)
        if enemy_unit.type == unit_classes[3]:
            diff = max(0, diff - 10)
        if diff > 0:
            self.health_percentage -= 2.5 * diff - 5
        else:
            self.health_percentage -= 0.4 * (-diff) - 3

    def calculate_melee_combat_with_city(self, city):
        diff = city.melee_strength - self.melee_strength + city.health_strength_loss() - self.health_strength_loss()
        if diff > 0:
            self.health_percentage -= 2.5 * diff - 5
        else:
            self.health_percentage -= 0.4 * (-diff) - 5
