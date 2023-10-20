from pplay.window import *
from pplay.sprite import *
import gameplay

def mainMenu(window):
    
    #init phase
    playButton = Sprite("sprites/playButton.png")
    playButton.set_position(window.width/2-playButton.width/2, 3*(window.height/10))

    #main loop
    while True:

        #handle buttons
        if window.mouse.is_over_object(playButton):
            if window.mouse.is_button_pressed(1):
                gameplay.game(window)
                

        #update phase
        window.update()
        window.set_background_color([0,0,0])
        playButton.draw()


