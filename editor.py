#this code is for creating, editiing and saving levels#


#importing modules
import sys

import pygame

from scripts.tilemap import Tilemap
from scripts.utils import load_images

RENDER_SCALE = 4.0

#making the game a class
class Editor:
    def __init__(self):

        #init module 
        pygame.init()

        #-------------------------------init screen--------------------------------#

        #set title
        pygame.display.set_caption("Editor")
        #creates screen obj reference named "screen"
        self.screen = pygame.display.set_mode((1280,960))

        #use display to scale images
        #important: display dimensions should be a multiple of screen dimensions for scaling to be possible
        self.display = pygame.Surface((320, 240))

        #--------------------------------------------------------------------------#

        #init clock, clock manages game fps
        self.clock = pygame.time.Clock()

        #load game images into dict
        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
            'border' : load_images('tiles/border'),
            'spawners' : load_images('tiles/spawners')
        }

        #----------spawners must be placed off grid-----------#
        
        #defines list for camera movement [left, right, up, down]
        self.movement = [False, False, False, False]

        #init tilemap
        self.tilemap = Tilemap(self, tile_size=16)

        #load map
        try:
            self.tilemap.load('data/maps/6.json')
        except FileNotFoundError:
            pass

        #init camera
        self.scroll = [0, 0]

        #gives a list with the diferent types os assets
        self.tile_list = list(self.assets)
        #tells wich asset is being used
        self.tile_group = 0
        #tells wich asset variant is used
        self.tile_variant = 0

        #var to check mouse activity
        self.clicking = False
        self.right_clicking = False
        #var to handle changing between tile variants
        self.shift = False

        self.ongrid = True

    def run(self):
        #game loop
        while True:

            #fills screen with background, avoids image 'shadow'
            self.display.fill((0, 0, 0))

            #moving camera
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)


            #gets curent tile selected
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            #make img partially transparent
            current_tile_img.set_alpha(100)

            #gets mouse position
            mpos = pygame.mouse.get_pos()
            #gets corrent cordinates after descaling
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE) 
            #gets coordinates in grid
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)

            #if clicked, adds tile to map
            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type' : self.tile_list[self.tile_group], 'variant' : self.tile_variant, 'pos' : tile_pos}
            #if clicked, remove tile
            if self.right_clicking:
                #rm tile on grid
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                #rm tile offgrid
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5, 5))

            #loop iterates through input events
            for event in pygame.event.get():
                #checks if input is clicking close button "X"
                if event.type == pygame.QUIT:
                    #is so, quits game
                    pygame.quit()
                    sys.exit()

                #check if mouse has input
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #left click
                    if event.button == 1:
                        self.clicking = True
                        #places tile on map offgrid
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type' : self.tile_list[self.tile_group], 'variant' : self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    #right click
                    if event.button == 3:
                        self.right_clicking = True

                    #changes current variant of current tile selected
                    if self.shift:
                        #mouse wheel scroll up
                        if event.button == 4:
                            #loops in tiles list
                            self.tile_variant = (self.tile_variant - 1) % (len(self.assets[self.tile_list[self.tile_group]]))
                        #mouse wheel scroll down
                        if event.button == 5:
                            #loops in tiles list
                            self.tile_variant = (self.tile_variant + 1) % (len(self.assets[self.tile_list[self.tile_group]]))
                    #changes tile selected
                    else:
                        #mouse wheel scroll up
                        if event.button == 4:
                            #loops in tiles list
                            self.tile_group = (self.tile_group - 1) % (len(self.tile_list))
                            self.tile_variant = 0
                        #mouse wheel scroll down
                        if event.button == 5:
                            #loops in tiles list
                            self.tile_group = (self.tile_group + 1) % (len(self.tile_list))
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False


                #checks for movement input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    #changes ongrid/offfgrid placement
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    #autotiles map
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    #save map
                    if event.key == pygame.K_o:
                        self.tilemap.save('data/maps/6.json')
                    #holding shift enables scroll between tile variants
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False                        

            #blits display in screen
            #pygame.transform.scale scales up display to fit in screen
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            #update screen
            pygame.display.update()
            #forces game to be in 60 fps
            self.clock.tick(60)

Editor().run()
