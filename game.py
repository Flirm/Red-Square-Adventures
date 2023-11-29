#importing modules
import sys
import random
from math import sin

import pygame

from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy, EnemyCylinder, EnemyCone
from scripts.clouds import Clouds
from scripts.particle import Particle

#making the game a class
class Game:
    def __init__(self):

        #init module 
        pygame.init()

        #-------------------------------init screen--------------------------------#

        #set title
        pygame.display.set_caption("Red Square Adventures")
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
            'player' : load_image('entities/player.png'),
            'background' : load_image('background.png'),
            'clouds' : load_images('clouds'),
            'cylinder/idle' : Animation(load_images('entities/cylinder/idle'), img_dur=6),
            'cylinder/run' : Animation(load_images('entities/cylinder/run'), img_dur=4),
            'cylinder/shooting' : Animation(load_images('entities/cylinder/shooting'), loop=False),
            'cylinder/recover' : Animation(load_images('entities/cylinder/recover'), img_dur=8,loop=False),
            'cone/idle' : Animation(load_images('entities/cone/idle'), img_dur=20),
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump')),
            'player/slide' : Animation(load_images('entities/player/slide')),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
            'player/dash' : Animation(load_images('entities/player/dash'), img_dur=6, loop=False),
            'particle/leaf' : Animation(load_images('particles/leaf'), img_dur = 20, loop = False),
            'particle/particle' : Animation(load_images('particles/particle'), img_dur = 6, loop = False),
            'smoke/jump' : Animation(load_images('smokes/jump'), loop=False),
            'gun' : load_image('gun.png'),
            'projectile' : load_image('projectile.png')
        }

        #init clouds
        self.clouds = Clouds(self.assets['clouds'], count=16)

        #------------------------------init player---------------------------------#
        
    
        #defines list for player movement [left, right]
        self.movement = [False, False]

        #init player object
        self.player = Player(self, (50,50), (8,15))

        #--------------------------------------------------------------------------#

        #init tilemap
        self.tilemap = Tilemap(self, tile_size=16)
        self.load_level(0)

        

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        #handles particles leaf spawner in trees
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        #spawing enemies and player from spawners in map
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1), ('spawners', 2)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            elif spawner['variant'] == 1:
                self.enemies.append(EnemyCylinder(self, spawner['pos'], (8, 15)))
            else:
                self.enemies.append(EnemyCone(self, spawner['pos'], (16,16)))
            
        #init projectiles list
        self.projectiles = []
        
        #init particle list
        self.particles = []

        #init camera
        self.scroll = [0, 0]
        self.in_border = [False, False]


    def menus(self):

        #defines sarting variables
        self.current_menu = 'main'
        self.current_button = 0

        #loading assets
        self.menu_assets = {
            'play' : load_image('buttons/play_button.png'),
            'controls' : load_image('buttons/controls_button.png'),
            'exit' : load_image('buttons/exit_button.png'),
            'title' : pygame.image.load('data/images/red_square_adventures_title.png'),
            'menu_controls' : pygame.image.load('data/images/controls_menu.png')
        }

        #defining the kind of buttons available
        self.button_types = {
            0 : 'play',
            1 : 'controls',
            2 : 'exit'
        }

        #code changes color of current button
        new_color_button = pygame.PixelArray(self.menu_assets[self.button_types[self.current_button]])
        new_color_button.replace((250, 116, 27), (250, 143, 65))
        del new_color_button

        self.sounds= {
            'button_switch' : pygame.mixer.Sound('data/sfx/button_switch.wav'),
            'button_click' : pygame.mixer.Sound('data/sfx/button_click.wav')
        }

        pygame.mixer.set_num_channels(2)

        while True:
            
            #blit background 
            self.display.blit(self.assets['background'], (0, 0))
            
            if self.current_menu == 'main':
                #blit buttons and title
                self.display.blit(self.menu_assets['play'], (self.display.get_width()/2 - self.menu_assets['play'].get_width()/2, self.display.get_height()/2 - self.menu_assets['play'].get_height()/2))
                self.display.blit(self.menu_assets['controls'], (self.display.get_width()/2 - self.menu_assets['controls'].get_width()/2, 7*self.display.get_height()/10 - self.menu_assets['controls'].get_height()/2))
                self.display.blit(self.menu_assets['exit'], (self.display.get_width()/2 - self.menu_assets['exit'].get_width()/2, 9*self.display.get_height()/10 - self.menu_assets['exit'].get_height()/2))
                self.display.blit(self.menu_assets['title'], (self.display.get_width()/2 - self.menu_assets['title'].get_width()/2, self.display.get_height()/10))


                #input events (change button selected, click button, exit)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        #if k up or down, revert previous button color, changes button selected, updates color on new button
                        if event.key == pygame.K_UP:
                            
                            pygame.mixer.Channel(0).play(self.sounds['button_switch'])

                            new_color_button = pygame.PixelArray(self.menu_assets[self.button_types[self.current_button]])
                            new_color_button.replace((250, 143, 65), (250, 116, 27))
                            del new_color_button

                            self.current_button = (self.current_button - 1) % len(self.button_types)

                            new_color_button = pygame.PixelArray(self.menu_assets[self.button_types[self.current_button]])
                            new_color_button.replace((250, 116, 27), (250, 143, 65))
                            del new_color_button

                        if event.key == pygame.K_DOWN:

                            pygame.mixer.Channel(0).play(self.sounds['button_switch'])

                            new_color_button = pygame.PixelArray(self.menu_assets[self.button_types[self.current_button]])
                            new_color_button.replace((250, 143, 65), (250, 116, 27))
                            del new_color_button

                            self.current_button = (self.current_button + 1) % len(self.button_types)

                            new_color_button = pygame.PixelArray(self.menu_assets[self.button_types[self.current_button]])
                            new_color_button.replace((250, 116, 27), (250, 143, 65))
                            del new_color_button

                        if event.key == pygame.K_z or event.key == pygame.K_RETURN:

                            pygame.mixer.Channel(1).play(self.sounds['button_click'])

                            if self.button_types[self.current_button] == 'play':
                                self.run()
                            elif self.button_types[self.current_button] == 'controls':
                                self.current_menu = 'controls'
                            else:
                                pygame.quit()
                                sys.exit()
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            else:
                
                #blit controls
                self.display.blit(self.menu_assets['menu_controls'], (self.display.get_width()/2 - self.menu_assets['menu_controls'].get_width()/2, self.display.get_height()/2 - self.menu_assets['menu_controls'].get_height()/2))

                #input events (return to main, exit)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.current_menu = 'main'
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    

            
            #scale display to screen size and blit
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            #update screen
            pygame.display.update()
            #forces game to be in 60 fps
            self.clock.tick(60)
        

    def run(self):
        #game loop
        while True:

            #fills screen with background, avoids image 'shadow'
            self.display.blit(self.assets['background'], (0, 0))


            #update camera
            if not self.in_border[0]:
                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            if not self.in_border[1]:
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            #spawn leaf particles
            for rect in self.leaf_spawners:
                #defines chance/rate of spawning
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            #update clouds movement and render
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            #render map
            self.in_border = False
            self.in_border = self.tilemap.render(self.display, offset=render_scroll, player_pos=self.player.pos)

            #updating and rendering enemies
            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)

            #updates player position
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            #projectile list has the following format for each element
            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                #update x value
                projectile[0][0] += projectile[1]
                #increments timer
                projectile[2] += 1
                #defines image and blit
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width()/2 - render_scroll[0], projectile[0][1] - img.get_height()/2 - render_scroll[1]))
                
                #if projectile collides with solid tile, gets deleted
                if self.tilemap.solid_check(projectile[0]) or projectile[2] > 360:
                    self.projectiles.remove(projectile)
                #check if not in dash (player is invencible during dash)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)

            #rendering particles
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)

                #gives more natural movement to leaf
                if particle.type == 'leaf':
                    particle.pos[0] += sin(particle.animation.frame * 0.035) * 0.3

                if kill:
                    self.particles.remove(particle)

            #loop iterates through input events
            for event in pygame.event.get():
                #checks if input is clicking close button "X"
                if event.type == pygame.QUIT:
                    #is so, quits game
                    pygame.quit()
                    sys.exit()

                #checks for movement input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_z:
                        self.player.jump()
                    if event.key == pygame.K_c:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    #if esc is pressed, return to main menu
                    if event.key == pygame.K_ESCAPE:
                        return

            #blits display in screen
            #pygame.transform.scale scales up display to fit in screen
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            #update screen
            pygame.display.update()
            #forces game to be in 60 fps
            self.clock.tick(60)

Game().menus()
