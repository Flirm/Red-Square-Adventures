import random

#class for a singular cloud
class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    #moves cloud in sky
    def update(self):
        self.pos[0] += self.speed

    def render(self, surf, offset=(0, 0)):
        #multiplying position by depth creates paralax effect
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        #blits image in correct pos, % is used for cloud to loop in screen (cloud goes to the other side of screen)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))

#class handles multiple clouds
class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []

        for i in range(count):
            self.clouds.append(Cloud((random.random() * 99999, random.random() * 99999), random.choice(cloud_images), random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))

        #sort clouds by depth, this way clouds that are closer to camera are rendered on top of the ones in the back
        self.clouds.sort(key=lambda x: x.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset=(0,0)):
        for cloud in self.clouds:
            cloud.render(surf, offset)
            