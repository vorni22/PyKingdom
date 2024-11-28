import networkx as nx

class Tech:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.owned = False

animal_husbandry = Tech('Animal Husbandry', 20)
mining = Tech('Mining', 20)
pottery = Tech('Pottery', 20)
sailing = Tech('Sailing', 40)
iron_workings = Tech('Iron Workings', 50)
writing = Tech('Writing', 40)
wheel = Tech('Wheel', 60)
archery = Tech('Archery', 50)
shipbuilding = Tech('Shipbuilding', 80)
military_tactics = Tech('Military Tactics', 100)
currency = Tech('Currency', 80)
engineering = Tech('Engineering', 100)
celestial_navigation = Tech('Celestial Navigation', 120)
apprenticeship = Tech('Apprenticeship', 160)
gunpowder = Tech('Gunpowder', 160)
education = Tech('Education', 160)
machinery = Tech('Machinery', 200)
mass_production = Tech('Mass Production', 200)
siege_tactics = Tech('Siege Tactics', 200)
sanitation = Tech('Sanitation', 240)
industrialization = Tech('Industrialization', 240)

class TechTree:
    def __init__(self):
        self.G = nx.DiGraph()
        self.techs = []
        self.init_tech_list()
        self.add_techs()

    def init_tech_list(self):
        self.techs.append(animal_husbandry)
        self.techs.append(mining)
        self.techs.append(pottery)
        self.techs.append(sailing)
        self.techs.append(iron_workings)
        self.techs.append(writing)
        self.techs.append(wheel)
        self.techs.append(archery)
        self.techs.append(shipbuilding)
        self.techs.append(military_tactics)
        self.techs.append(currency)
        self.techs.append(engineering)
        self.techs.append(celestial_navigation)
        self.techs.append(apprenticeship)
        self.techs.append(gunpowder)
        self.techs.append(education)
        self.techs.append(machinery)
        self.techs.append(mass_production)
        self.techs.append(siege_tactics)
        self.techs.append(sanitation)
        self.techs.append(industrialization)
        self.G.add_nodes_from(self.techs)

    def add_techs(self):
        self.G.add_edge(animal_husbandry, archery)
        self.G.add_edge(animal_husbandry, sailing)
        self.G.add_edge(mining, iron_workings)
        self.G.add_edge(pottery, writing)
        self.G.add_edge(pottery, wheel)
        self.G.add_edge(archery, machinery)
        self.G.add_edge(sailing, shipbuilding)
        self.G.add_edge(iron_workings, military_tactics)
        self.G.add_edge(writing, currency)
        self.G.add_edge(wheel, engineering)
        self.G.add_edge(shipbuilding, celestial_navigation)
        self.G.add_edge(military_tactics, industrialization)
        self.G.add_edge(currency, education)
        self.G.add_edge(currency, apprenticeship)
        self.G.add_edge(engineering, apprenticeship)
        self.G.add_edge(engineering, gunpowder)
        self.G.add_edge(celestial_navigation, mass_production)
        self.G.add_edge(education, sanitation)
        self.G.add_edge(apprenticeship, industrialization)