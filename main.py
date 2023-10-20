from pplay.window import *
import menus
import globalSettings

window = Window(1280,720)

globalSettings.init()
menus.mainMenu(window)
