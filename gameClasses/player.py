from pplay.sprite import Sprite
from pplay.window import Window
from pplay.gameimage import load_image
import pygame

class Player(Sprite):

    def __init__(self, image_file, frames=1):
        # Parent's constructor must be first-called
        super(Player, self).__init__(image_file, frames)
        self.image_file = image_file

    def movement(self, speed):


        #TODO make this flip the player image depending on direction
        if Window.get_keyboard().key_pressed("left"):
            self.move_x(-speed)
        if Window.get_keyboard().key_pressed("right"):
            self.move_x(speed)