from pplay.window import *


def mainMenu(window):
    while True:

        if window.keyboard.key_pressed("space"):
            exit()

        window.update()

