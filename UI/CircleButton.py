import pygame as pg
from math import sqrt

class CircleButton:
    def __init__(self, surface, radius, center):
        self.surf = surface
        self.radius = radius
        self.center = center
        self.rendered = False

    def circle_collidepoint(self, position):
        return ((position[0] - (self.center[0] + self.radius // 2)) ** 2 + (position[1] - (self.center[1] + self.radius // 2)) ** 2) <= self.radius ** 2

    def draw(self, screen):
        screen.blit(self.surf, self.center)
        self.rendered = True