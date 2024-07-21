#!/usr/bin/env python3

"""
A Python/Pygame exercise to build a tiled memory game. The game is
to match 12 different tiles. The game is played on a 5 x 5 matrix
25 squares. We need only 24. So the middle square is taken out of
play in the the self.tile_list leaving only 24 entries. However an
extra number has to be added to the self.card_list after it is
duplicated and shuffled so there are 25 numbers, same as the number
of squares. This is number 12 and is never used. This middle square
has no cover and is used to signal if the guessed tiles are a good
match or not.
"""

import os
from os import path
import random
import time
import pygame as pg

# These are the initial constants.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
H_TILESIZE = 100
V_TILESIZE = 100
FONT_NAME = 'arial'
TIME_FILE = "time.txt"

COVER_LAYER = 1
CARD_LAYER = 2


class Card(pg.sprite.Sprite):
    """Establish Card class.
       Card images are a sub-set of majong tile
       fronts cut square to 100 x 100 pixels.
       These images are stored in the img sub-directory.
       Three sets are images are available if you want to
       change the card images."
    """

    def __init__(self, game, tile, tile_pos):  # Set up card face up display
        super(Card, self).__init__()
        self.groups = game.all_sprites, game.cards
        self._layer = CARD_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = tile
        self.rect = self.image.get_rect()
        self.pos = (tile_pos)
        self.rect = self.pos


class Cover(pg.sprite.Sprite):
    """Establish Cover class.
       Images are a sub-set of back images
       cut square to 100 x 100 pixels. These
       are stored in the img sub-directory.
       Special back images for the middle square
       are also here.
    """

    def __init__(self, game, tile, tile_pos):
        """Set up back covers."""
        super(Cover, self).__init__()
        self.groups = game.all_sprites, game.covers
        self._layer = COVER_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = tile
        self.rect = self.image.get_rect()
        self.pos = (tile_pos)
        self.rect = self.pos


class Game:
    """Establish Game class."""

    def __init__(self):  # Get play area size and initilise
        pg.init()
        pg.mouse.set_visible(True)
        self.font_name = pg.font.match_font(FONT_NAME)
        self.running = True
        self.screen = pg.display.set_mode(
            (H_TILESIZE * 5, V_TILESIZE * 5))
        pg.display.set_caption('Match the Cards')
        # Some initial settings.
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.cards = pg.sprite.Group()
        self.covers = pg.sprite.Group()
        self.playing = True
        self.st_time = 0
        self.tile_num = ()
        self.tile_list = []
        self.card_list = []
        self.alpha = ()
        self.beta = ()
        self.card_alpha = None
        self.card_beta = None
        self.tile_alpha = None
        self.tile_beta = None
        self.num_alpha = None
        self.num_beta = None
        self.happy = None
        self.sad = None
        self.elapsed_time = 0
        self.mouse_click = 0
        self.show = False
        self.secs = 1.0
        self.best_time = 0
        self.card_list = []
        self.load_images()

    def load_images(self):  # Load all game graphics
        folder = path.join(path.dirname(__file__), 'img')
        try:
            self.dir = path.dirname(__file__)
            try:
                with open(path.join(self.dir, TIME_FILE), 'r') as fff:
                    self.best_time = int(fff.read())
            except IOError:
                print("No file time.txt found")
                self.best_time = 250
            self.card_list = ['majong1.png', 'majong2.png', 'majong3.png',
                              'majong4.png', 'majong5.png', 'majong6.png',
                              'majong7.png', 'majong8.png', 'majong9.png',
                              'majong10.png', 'majong11.png', 'majong12.png']
            self.card_images = []
            for img in self.card_list:
                self.card_images.append(pg.image.load(
                    os.path.join(folder, img)).convert())
            self.back_list = ['back1.png', 'back2.png',
                              'back3.png', 'back4.png']
            self.back_images = []
            for img in self.back_list:
                self.back_images.append(pg.image.load(
                    os.path.join(folder, img)).convert())
            self.em_list = ['em1.png', 'em2.png', 'em3.png', 'em4.png']
            self.em_images = []
            for img in self.em_list:
                self.em_images.append(pg.image.load(
                    os.path.join(folder, img)).convert())
        except OSError as err:
            print("OS error: {0}".format(err))

    @staticmethod
    def get_tile(pos):  # Get tile number from mouse position
        col = 0
        row = 0
        tile_num = 0, 0
        for ppp in range(5):
            if pos[0] // H_TILESIZE == ppp:
                col = ppp
        for qqq in range(5):
            if pos[1] // V_TILESIZE == qqq:
                row = qqq
        tile_num = row, col
        return tile_num

    @staticmethod
    def change_places(alist, tile_one, tile_two):  # Only make change randomly
        if random.randint(1, 101) % 3 == 0:
            alist[tile_one], alist[tile_two] = alist[tile_two], alist[tile_one]
        return alist

    def new(self):
        # Create th card list of 12 numbers, duplicate it and shuffle.
        self.card_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        list2 = self.card_list.copy()
        self.card_list.extend(list2)
        random.shuffle(self.card_list)
        # Add in tthe extra number (12) in the middle of the list.
        self.card_list.insert(12, 12)
        for i in range(5):
            for j in range(5):
                if i == 2 and j == 2:  # Place image on the the middle tile
                    tile_pos = i * 100, j * 100
                    Cover(self, self.em_images[2], tile_pos)
                else:  # Create list of playable tiles
                    self.tile_list.append((i, j))
                    tile_pos = i * 100, j * 100
                    Cover(self, self.back_images[0], tile_pos)
        self.run()

    def run(self):  # Run main game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def events(self):  # First check for end game events
        for event in pg.event.get():
            if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
                    or event.type == pg.QUIT):
                if self.playing:
                    self.playing = False
                self.running = False
            # Still running? Now handle any MOUSEBUTTONDOWN calls.
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                tile_num = self.get_tile(pos)
                card_num = tile_num[0] * 5 + tile_num[1]
                tile_pos = tile_num[1] * 100, tile_num[0] * 100
                if self.mouse_click == 0:
                    self.st_time = pg.time.get_ticks()
                if tile_num in self.tile_list:
                    if self.mouse_click % 2 == 0:
                        self.tile_alpha = tile_num
                        self.num_alpha = card_num
                        self.card_alpha = self.card_list[
                            self.num_alpha]
                        self.alpha = Card(self, self.card_images[
                            self.card_alpha], tile_pos)
                        self.tile_list.remove(self.tile_alpha)
                        self.mouse_click += 1
                    else:
                        self.tile_beta = tile_num
                        self.num_beta = card_num
                        self.card_beta = self.card_list[
                            self.num_beta]
                        self.beta = Card(self, self.card_images[
                            self.card_beta], tile_pos)
                        self.tile_list.append(self.tile_alpha)
                        self.mouse_click += 1

    def update(self):  # Update main game loop
        if self.card_beta is not None and self.show is True:
            if self.card_alpha == self.card_beta:
                # Change middle tile image and draw it before continuing.
                if self.happy is None:
                    self.happy = Card(self, self.em_images[0], (200, 200))
                else:
                    self.tile_list.remove(self.tile_alpha)
                    self.tile_list.remove(self.tile_beta)
                    self.card_alpha = None
                    self.card_beta = None
                    time.sleep(self.secs)
                    self.happy.kill()
                    self.happy = None
                    self.show = False
                    # Have we finished?
                    if len(self.tile_list) <= 0:
                        end_time = pg.time.get_ticks()
                        self.elapsed_time = (
                            end_time - self.st_time) // 1000
                        if self.elapsed_time < self.best_time:
                            self.best_time = self.elapsed_time
                            with open(path.join(
                                    self.dir, TIME_FILE), 'w') as fff:
                                fff.write(str(self.best_time))
                        self.playing = False
            else:
                # Change middle tile image and draw it before continuing.
                if self.sad is None:
                    self.sad = Card(self, self.em_images[1], (200, 200))
                else:
                    time.sleep(self.secs)
                    self.alpha.kill()
                    self.beta.kill()
                    self.sad.kill()
                    self.change_places(
                        self.card_list, self.num_alpha, self.num_beta)
                    self.card_alpha = None
                    self.card_beta = None
                    self.sad = None
                    self.show = False

    def draw(self):  # Draw game screen
        self.screen.fill(BLACK)
        if self.card_beta is not None:
            self.show = True
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def show_start_screen(self):  # Game splash/start screen
        self.screen.fill(BLACK)
        self.screen.blit(
            self.back_images[0], (H_TILESIZE * 5 // 2 - 64, 40))
        self.draw_text(
            "Match the Cards", 48, WHITE, 200)
        self.draw_text(
            "Press any mouse button to start", 24, WHITE, 260)
        self.draw_text(
            "Then click on any Card to see symbol", 18, WHITE, 310)
        self.draw_text(
            "Matched Cards will stay visible", 18, WHITE, 340)
        self.draw_text(
            "Unmatched Cards will disappear", 18, WHITE, 370)
        self.draw_text(
            "and may change position", 18, WHITE, 400)
        self.draw_text(
            "Good Luck", 36, WHITE, 440)
        pg.display.flip()
        self.wait_for_key()

    def show_end_screen(self):
        # Draw game over screen and show for 5 seconds
        if not self.running:
            return
        self.screen.fill(BLACK)
        self.screen.blit(
            self.em_images[3], (H_TILESIZE * 5 // 2 - 64, 40))
        self.draw_text(
            "GAME OVER", 48, WHITE, 200)
        self.draw_text(
            "You have played for " + str(self.elapsed_time) + " seconds",
            18, WHITE, 260)
        self.draw_text(
            "The best time is " + str(self.best_time) + " seconds",
            18, WHITE, 310)
        self.draw_text(
            "Thank you for completing this self-imposed", 18, WHITE, 340)
        self.draw_text(
            "and totally unnecessary task", 18, WHITE, 370)
        self.draw_text(
            "Press any mouse button to play again, ESC to end",
            18, WHITE, 400)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        # Wait for key press to start and end game
        waiting = True
        while waiting:
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
                        or event.type == pg.QUIT):
                    self.running = False
                    waiting = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    waiting = False
                    self.playing = True

    def draw_text(self, text, size, color, posy):
        # Add text to display
        posx = int(H_TILESIZE * 5 // 2)
        posy = int(posy)
        size = int(size)
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (posx, posy)
        self.screen.blit(text_surface, text_rect)


gm = Game()  # Create the game object and start
gm.show_start_screen()
while gm.running:
    gm.new()
    gm.show_end_screen()

pg.quit()  # End game
