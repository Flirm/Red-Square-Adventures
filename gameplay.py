from pplay.sprite import *
from pplay.window import *
from gameClasses.player import *

def game(window):

    #init phase
    player = Player("sprites/redSquare.png")
    player.set_position(window.width/2, window.height/2)

    #main loop
    while True:

        #break condition
        if window.keyboard.key_pressed("esc"):
            return

        #player actions
        player.movement(400*window.delta_time())


        #update phase
        window.update()
        window.set_background_color([0,0,0])
        player.draw()

# Esse é o tal do commit???