
# @author Alexandru Condorache
# Represents a button that has an interactive behaviour
# @param surf (pg.Surface): The surface or image representing the button.
# @param radius (int): The radius of the circular button.
# @param center (tuple): The (x, y) coordinates of the to p -left corner where the button is drawn.
# @param rendered (bool): Indicates whether the button has been rendered on the screen.
class CircleButton:
    def __init__(self, surface, radius, center):
        self.surf = surface
        self.radius = radius
        self.center = center
        self.rendered = False

# Checks if the mouse position is within the circular button's area.
    def circle_collidepoint(self, position):
        return ((position[0] - (self.center[0] + self.radius // 2)) ** 2 + (position[1] - (self.center[1] + self.radius // 2)) ** 2) <= self.radius ** 2

    def draw(self, screen):
        screen.blit(self.surf, self.center)
        self.rendered = True