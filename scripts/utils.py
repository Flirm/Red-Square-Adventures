import os

import pygame

BASE_IMG_PATH = 'data/images/'
BASE_SFX_PATH = 'data/sfx/'

#loads singular images into memory
def load_image(path):
    #loads image into memory
    #convert() makes image more eficient to render
    img = pygame.image.load(BASE_IMG_PATH + path).convert()

    #colorkey tells to convert the color given to transparent (remove image background)
    img.set_colorkey((0,0,0))

    return img

#loads many images (folder) to memory
def load_images(path):
    images = []
    #os.listdir gives all files in path
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(load_image(path + '/' + img_name))
    
    return images

def load_sound(path, volume=1):
    sound = pygame.mixer.Sound(BASE_SFX_PATH + path)
    sound.set_volume(volume)
    return sound

def play_sound(sound_file, chanel_num):
    pygame.mixer.Channel(chanel_num).play(sound_file)



class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            #loops animation frames
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            #goes to the end of animation then stops
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    
