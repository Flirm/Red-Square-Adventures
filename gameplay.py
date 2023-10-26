from pplay.sprite import *
from pplay.window import *
from gameClasses.player import *
from pplay.text import *
from gameClasses.sword import *

def game(window):

    #init player
    player = Player("sprites/redSquare.png")
    player.set_position(window.width/2, window.height-player.height)

    #init sword
    sword = Sword("sprites/sword.png")
    sword.set_position(player.x-3*player.width/4, player.y)

    #init money
    moneyText = Text(60, 100, f"Money = {globalSettings.money}", (255,255,255), 24)

    #main loop
    while True:

    

        #break condition
        if window.keyboard.key_pressed("esc"):
            return

        #player actions
        player.movement(400*window.delta_time())
        sword.attack()

        #handle sword position
        if globalSettings.attacking:
            if globalSettings.direction == 0:
                sword.set_position(player.x+3*player.width/4, player.y)
            else:
                sword.set_position(player.x-3*player.width/4, player.y)
        else:
            if globalSettings.direction == 0:
                sword.set_position(player.x-3*player.width/4, player.y)
            else:
                sword.set_position(player.x+3*player.width/4, player.y)

        player.jump(globalSettings.jumpForce*window.delta_time())
        player.gravity(globalSettings.gravForce*window.delta_time())
        #testing gravity with random window height
        if player.y >= window.height-player.height:
            globalSettings.grounded = True

        #update phase#
        window.set_background_color([0,0,0])

        #draw life and energy bars
        pygame.draw.rect(window.get_screen(), (255,0,0), pygame.Rect(30, 30, globalSettings.playerLife, 20))
        pygame.draw.rect(window.get_screen(), (0,0,255), pygame.Rect(30, 60, globalSettings.playerEnergy, 20))
        #update and draw money
        moneyText.update_text(f"Money = {globalSettings.money}")
        moneyText.draw()
        player.draw()
        sword.draw()
        window.update()
