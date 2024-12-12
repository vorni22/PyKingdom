import Map_Generation.Map as Map
unit_classes = ['Melee', 'Ranged', 'Cavalry', 'Siege', 'Naval Melee', 'Naval Ranged', 'Civilian']

melee_units = ['Warrior', 'Swordsman', 'Man at Arms']
ranged_units = ['Slinger', 'Archer', 'Crossbowman']
cavalry_units = ['Horseman', 'Heavy Chariot', 'Knight']
siege_units = ['Catapult', 'Trebuchet', 'Bombard']
naval_melee_units = ['Galley', 'Caravel']
naval_ranged_units = ['Quadrireme', 'Frigate']
civilian_units = ['Settler']

melee_units_costs = [50, 70, 90]
ranged_units_costs = [50, 70, 90]
cavalry_units_costs = [50, 70, 90]
siege_units_costs = [50, 70, 90]
naval_melee_units_costs = [60, 80]
naval_ranged_units_costs = [60, 80]
civilian_units_costs = 120

# Holds information about a unit
# @param position_line: the line on which the unit is currently situated
# @param position_column: the column on which the unit is currently situated
# @param type: what type of unit this unit could be
# @param display_name: what name the unit displays. By default, the same as the internal name, but can be changed
# @param name: the name of the unit type
# @param movement: how much movement the unit has
# @param ranged_strength: how much ranged strength the unit has. Only applicable to ranged, siege and naval ranged units
# @param melee_strength: how much melee strength the unit has
# @param health percentage: how much health the unit has left. If the unit reaches 0, it dies

class Unit:
    def __init__(self, type_id, name_id, position_line, position_column):
        self.position_line = position_line
        self.position_column = position_column
        self.type_id = type_id
        self.type = unit_classes[type_id]
        self.name = None
        self.name_id = name_id
        self.init_name(type_id, name_id)
        self.movement = 0
        self.init_movement(type_id, name_id)
        self.remaining_movement = self.movement
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

    def move(self, new_line, new_column):
        distance = Map.Map.get_unit_shortest_distance(self.position_line, self.position_column, new_line, new_column)
        if distance < self.remaining_movement:
            if distance % self.remaining_movement == 0:
                return distance // self.remaining_movement
            else:
                return distance // self.remaining_movement + 1
        self.remaining_movement -= distance
        self.position_line = new_line
        self.position_column = new_column
        return 0

    def reset_movement(self):
        self.remaining_movement = self.movement
