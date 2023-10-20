from pplay.sprite import Sprite
from pplay.window import Window
import pygame
import globalSettings

class Player(Sprite):

    def __init__(self, image_file, frames=1):

        # Parent's constructor must be first-called
        super(Player, self).__init__(image_file, frames)

        #initializes images of the player facing left and right
        self.image = pygame.image.load(image_file)
        self.flipedImage = pygame.transform.flip(self.image, True, False)

    def movement(self, speed):


        #flips the player image depending on direction and update movement
        if Window.get_keyboard().key_pressed("left"):
            self.move_x(-speed)
            globalSettings.direction = 1
        elif Window.get_keyboard().key_pressed("right"):
            self.move_x(speed)
            globalSettings.direction = 0

    def jump(self, force):

        #check if space is pressed and not already jumping
        if Window.get_keyboard().key_pressed("space") and not globalSettings.jumpDelay:
            #update global var to set player to jumping state
            globalSettings.jumpDelay = True
            globalSettings.grounded = False

        #if is jumping update y value, jumping loses force with time in air
        if globalSettings.jumpDelay == True:
            self.y -= force*5
            if globalSettings.jumpForce > 0:
                globalSettings.jumpForce -= 0.1
            else:
                globalSettings.jumpForce = 0
        

    def gravity(self, gForce):
        #if jump ended and not on ground, start falling
        if globalSettings.jumpForce == 0 and not globalSettings.grounded:
            self.y += gForce*5
            if globalSettings.gravForce < 500:
                globalSettings.gravForce += 0.1
        #if on gorund resets jumping state
        elif globalSettings.grounded:
            globalSettings.jumpDelay = False
            globalSettings.jumpForce = 100
        
    

    def draw(self):

        #defines player rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        #renders player in the correct direction
        if globalSettings.direction == 0:
            Window.get_screen().blit(self.image, self.rect)
        elif globalSettings.direction == 1:
            Window.get_screen().blit(self.flipedImage, self.rect)
