import pygame as pg

# @author Alexandru Condorache
# This class is responsible for rendering a permanent UI panel that displays
# resource information such as science, culture, and gold. The panel's layout
# is defined by a background image, and text overlays show dynamic values
# for each resource.
# @param surf (pg.Surface): The surface representing the background image of the panel.
# @param fnt (pg.Font): The font object used to render text on the panel.
# @param science_rect (pg.Rect): The rectangle area for the science resource display.
# @param culture_rect (pg.Rect): The rectangle area for the culture resource display.
# @param gold_rect (pg.Rect): The rectangle area for the gold resource display.
# @param text_science (pg.Surface): The rendered text showing the science value and modifier.
# @param text_culture (pg.Surface): The rendered text showing the culture value and modifier.
# @param text_gold (pg.Surface): The rendered text showing the gold value and modifier.
# @param text_science_rect (pg.Rect): The rectangle defining the position of the science text.
# @param text_culture_rect (pg.Rect): The rectangle defining the position of the culture text.
# @param text_gold_rect (pg.Rect): The rectangle defining the position of the gold text.


class PermanentPanel:
    def __init__(self):
        self.surf = pg.image.load("Assets/UIAssets/permanent_layout.png")
        self.fnt = pg.font.Font("Assets/UIAssets/DejaVuSans.ttf", 30)

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

# Draws the player information
    def draw(self, screen, get_player_information):
        screen.blit(self.surf, (0,0))

        (num, total_science, total_culture, total_gold, science_per_turn, culture_per_turn, gold_per_turn) = get_player_information()

        self.text_science = self.fnt.render(str(total_science) + self.__to_superscript("+" + str(round(science_per_turn))), True, "Black")
        self.text_culture = self.fnt.render(str(total_culture) + self.__to_superscript("+" + str(round(culture_per_turn))), True, "Black")
        self.text_gold = self.fnt.render(str(total_gold) + self.__to_superscript("+" + str(round(gold_per_turn))), True, "Black")

        self.text_science_rect = self.text_science.get_rect()
        self.text_culture_rect = self.text_culture.get_rect()
        self.text_gold_rect = self.text_gold.get_rect()

        self.text_science_rect.x, self.text_science_rect.centery = self.science_rect.x + 5, self.science_rect.centery
        self.text_culture_rect.x, self.text_culture_rect.centery = self.culture_rect.x + 5, self.culture_rect.centery
        self.text_gold_rect.x, self.text_gold_rect.centery = self.gold_rect.x + 5, self.gold_rect.centery

        screen.blit(self.text_science, self.text_science_rect)
        screen.blit(self.text_culture, self.text_culture_rect)
        screen.blit(self.text_gold, self.text_gold_rect)

# Maps digits and . and + chars to superscript versions
    def __to_superscript(self, text):
        superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            '+': '⁺', '.': '˙'
        }
        return ''.join(superscript_map.get(char, char) for char in text)
