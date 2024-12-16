import pygame as pg

class PermanentPanel:
    def __init__(self):
        self.surf = pg.image.load("Assets/MainMenu/permanent_layout.png")
        self.fnt = pg.font.Font("Assets/MainMenu/DejaVuSans.ttf", 30)

        self.science_rect = pg.rect.Rect(51, 0, 143, 50)
        self.culture_rect = pg.rect.Rect(241, 0, 143, 50)
        self.gold_rect = pg.rect.Rect(433, 0, 143, 50)

        self.text_science = self.fnt.render("123" + self.__to_superscript("+69"), True, "Black")
        self.text_culture = self.fnt.render("123" + self.__to_superscript("+69"), True, "Black")
        self.text_gold = self.fnt.render("123" + self.__to_superscript("+69"), True, "Black")

        self.text_science_rect = self.text_science.get_rect()
        self.text_culture_rect = self.text_culture.get_rect()
        self.text_gold_rect = self.text_gold.get_rect()

        self.text_science_rect.x, self.text_science_rect.centery = self.science_rect.x + 10, self.science_rect.centery
        self.text_culture_rect.x, self.text_culture_rect.centery = self.culture_rect.x + 10, self.culture_rect.centery
        self.text_gold_rect.x, self.text_gold_rect.centery = self.gold_rect.x + 10, self.gold_rect.centery

    def draw(self, screen):
        screen.blit(self.surf, (0,0))
        screen.blit(self.text_science, self.text_science_rect)
        screen.blit(self.text_culture, self.text_culture_rect)
        screen.blit(self.text_gold, self.text_gold_rect)

    def __to_superscript(self, text):
        superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            '+': '⁺'
        }
        return ''.join(superscript_map.get(char, char) for char in text)
