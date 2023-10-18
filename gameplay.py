from pplay.sprite import *
from pplay.window import *
from gameClasses.player import *

def game(window):

    player = Player("sprites/redSquare.png")
    player.set_position(window.width/2, window.height/2)


    while True:

        if window.keyboard.key_pressed("esc"):
            return

        player.movement(400*window.delta_time())

        window.update()
        window.set_background_color([0,0,0])
        player.draw()