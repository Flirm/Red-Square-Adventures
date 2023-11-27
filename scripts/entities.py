from math import pi, sin, cos
from random import random, randint

import pygame

from scripts.particle import Particle

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up' : False, 'down' : False, 'right' : False, 'left' : False}

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up' : False, 'down' : False, 'right' : False, 'left' : False}

        #create vector that represents how much said entity should move in the frame
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        
        #handles X collision and update
        self.pos[0] += frame_movement[0]

        entity_rect = self.rect()

        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                #if moving left or right and collide, handles accordingly
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                #update pos
                self.pos[0] = entity_rect.x

        #handles Y collision and update
        self.pos[1] += frame_movement[1]

        entity_rect = self.rect()
        
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                #if moving left or right and collide, handles accordingly
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                #update pos
                self.pos[1] = entity_rect.y

        #sets if image should be flipped when rendering based on movement
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        #defines vertical velocity with gravity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        #resets gravity if collided with ground or roof
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        #update animation frame
        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

#enemy class template  
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0,0)):
        if self.walking:
            #check to see if there is a walkable tile in front
            #checks 7 pixels to left or right dependent on movement, and 23 pixels below
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                #if collided wall
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:   
                    #defines move direction
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)

            #shoots a projectile once it stops walking (1 shoot/walk cicle)
            if not self.walking:
                #defines distane between player and enemy
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                #if y distance < 16
                if (abs(dis[1]) < 16):
                    #if looking left and player at left
                    if (self.flip and dis[0] < 0):
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                    #if looking right and player at right
                    if (not self.flip and dis[0] > 0):
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], +1.5, 0])

        elif random() < 0.01:
            #random chance to start walking
            self.walking = randint(30, 120)

        super().update(tilemap, movement=movement)

        #set correct animation based on movement
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

    def render(self, surf, offset=(0, 0)):
        #render enemy
        super().render(surf, offset=offset)

        #render gun
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1])) 
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))


#walks and shoots at player direction
class EnemyCylinder(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'cylinder', pos, size)
        self.shoot_delay = 0
        self.walking = 0
        self.in_recover = False
        self.lock_in = False

    def update(self, tilemap, movement=(0,0)):
        #defines distane between player and enemy
        dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])

        #if x distance < 8 tiles (128 pixels) and y distance < 1 tile (16 pixels), enemy moves towards player
        if (abs(dis[0]) < 128) and (abs(dis[1]) < 10):

            #if not aiming at player, can change direction
            if not self.lock_in:
                #makes enemy face at player direction
                self.flip = True if dis[0] < 0 else False

            #if distance < 5 tiles (128 pixels), stop moving and shoot
            if(abs(dis[0]) < 80) and (abs(dis[1] < 10)):
                if not self.in_recover:
                    self.set_action('shooting')
                    self.lock_in = True
                    #shoots once every 1 seconds
                    if self.shoot_delay >= 50:
                        self.shoot_delay = 0
                        self.in_recover = True
                        self.set_action('recover')

                        #if looking left and player at left
                        if (self.flip):
                            self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])

                        #if looking right and player at right
                        if (not self.flip):
                            self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], +1.5, 0])

                    else:
                        self.shoot_delay += 1
            else:
                self.shoot_delay = 0
                #check if movement is possible
                if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                    if self.collisions['right'] or self.collisions['left']:
                        pass
                    else:
                        movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
                else:
                    pass
        else:
            self.lock_in = False
            self.shoot_delay = 0
            if self.walking:
                #check to see if there is a walkable tile in front
                #checks 7 pixels to left or right dependent on movement, and 23 pixels below
                if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                    #if collided wall
                    if self.collisions['right'] or self.collisions['left']:
                        self.flip = not self.flip
                    else:   
                        #defines move direction
                        movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
                else:
                    self.flip = not self.flip
                self.walking = max(0, self.walking - 1)          

            elif random() < 0.01:
                #random chance to start walking
                self.walking = randint(30, 120)

        super().update(tilemap, movement=movement)

        #set correct animation based on movement
        if self.in_recover:
            self.set_action('recover')
            if self.animation.done:
                self.in_recover = False
                self.lock_in = False
        elif movement[0] != 0:
            self.set_action('run')  
        elif not self.shoot_delay:
            self.set_action('idle')

#flies around, if player passes below it, falls
class EnemyPiramid(Enemy):
    pass

#walks around, if player gets close, dashes in player direction (mario world's chargin' chuck)
class EnemyCircle(Enemy):
    pass

        
    



class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.double_jump = False
        self.wall_slide = False
        self.wall_jump = False
        self.dashing = 0

    def update(self, tilemap, movement=(0 ,0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        #if on ground, resets air time and jump delay
        if self.collisions['down']:
            self.air_time = 0
            self.restore_jumps()

        #handles wall slide
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        if not self.wall_slide:
            #if on air for a 'long' time sets jump anim
            if self.air_time > 4:
                self.set_action('jump')
            #if moving, sets run anim
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')


        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                #getting dash burst particles anim randomly
                angle = random() * pi * 2
                speed = random() * 0.5 + 0.5
                pvelocity = [cos(angle) * speed, sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=randint(0, 7)))

        #brings dash vel closer to 0
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        elif self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        
        #makes vel move player in the first frames, then sudden stop in vel
        if abs(self.dashing) > 50:
            self.set_action('dash')
            self.velocity[0] = abs(self.dashing) / self.dashing * 5
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            #makes gravity not work while in dash
            self.velocity[1] = 0

            #get anim for dash stream
            pvelocity = [abs(self.dashing) / self.dashing * random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=randint(0, 7)))


        #adds 'air resistence' to horizontal movement
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0, 0)):
        #if not in dash renders normally
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    def jump(self):
        if self.wall_slide and self.wall_jump:
            #if facing left and move atempt is to left
            if self.flip and self.last_movement[0] < 0:
                #push to right then up to make wall_slide jump
                self.velocity[0] = 2.0
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -2.0
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        #check if there are jumps left
        elif self.jumps:
            self.jumps -= 1
            self.velocity[1] = -3
            #puts air time in 5 to force jumping anim to start playing
            self.air_time = 5
            return True
    
    def restore_jumps(self):
        if not self.double_jump:
            self.jumps = 1
        else:
            self.jumps = 2

    def dash(self):
        #only dashes if not in dash
        if not self.dashing:
            #defines if dash goes left or right
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60