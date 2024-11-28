import networkx as nx

class Civic:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.owned = False

sedentarism = Civic('Sedentarism', 40)
drama_and_poetry = Civic('Drama and Poetry', 80)
urbanization = Civic('Urbanization', 120)
guilds = Civic('Guilds', 160)
humanism = Civic('Humanism', 160)
square_rigging = Civic('Square Rigging', 200)
feudalism = Civic('Feudalism', 200)
colonization = Civic('Colonization', 200)

class CivicTree:
    def __init__(self):
        self.G = nx.DiGraph()
        self.civics = []
        self.init_civic_list()
        self.add_civics()

    def init_civic_list(self):
        self.civics.append(sedentarism)
        self.civics.append(drama_and_poetry)
        self.civics.append(urbanization)
        self.civics.append(guilds)
        self.civics.append(humanism)
        self.civics.append(square_rigging)
        self.civics.append(feudalism)
        self.civics.append(colonization)
        self.G.add_nodes_from(self.civics)

    def add_civics(self):
        self.G.add_edge(sedentarism, drama_and_poetry)
        self.G.add_edge(drama_and_poetry, urbanization)
        self.G.add_edge(drama_and_poetry, humanism)
        self.G.add_edge(urbanization, guilds)
        self.G.add_edge(guilds, square_rigging)
        self.G.add_edge(humanism, feudalism)
        self.G.add_edge(humanism, colonization)
