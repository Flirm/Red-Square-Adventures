from pplay.sprite import *
from pplay.window import *
import pygame
import globalSettings
from gameClasses.player import Player


class Sword(Sprite):

    def __init__(self, image_file, frames=1):

        # Parent's constructor must be first-called
        super(Sword, self).__init__(image_file, frames)

        #initializes images of the player facing left and right
        baseImage = pygame.image.load(image_file)
        self.image = pygame.transform.rotate(baseImage, 90)
        self.rotatedImage = pygame.transform.flip(self.image, True, False)
        

    def attack(self):
        if Window.get_keyboard().key_pressed("c"):
            globalSettings.attacking = True
        else:
            globalSettings.attacking = False


    def draw(self):

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not globalSettings.attacking:
            if globalSettings.direction == 0:
                Window.get_screen().blit(self.image, self.rect)
            else:
                Window.get_screen().blit(self.rotatedImage, self.rect)
        else:
            if globalSettings.direction == 0:
                Window.get_screen().blit(self.rotatedImage, self.rect)
            else:
                Window.get_screen().blit(self.image, self.rect)