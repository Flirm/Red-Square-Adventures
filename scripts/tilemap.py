import json

import pygame

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])) : 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])) : 1,
    tuple(sorted([(-1, 0), (0, 1)])) : 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])) : 3,
    tuple(sorted([(-1, 0), (0, -1)])) : 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])) : 5,
    tuple(sorted([(1, 0), (0, -1)])) : 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])) : 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])) : 8
}

#list defines tiles that are neighbors with entity position
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}

#tilemap class handles placing and rendering scenario
class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    #takes list of id_pairs (type, variant etc) and passes in game information about them
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                #converting position from grid into pixels
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        
        return matches

    #return tiles around pos
    def tiles_around(self, pos, scale=1):
        
        #gets the scale of the sprite so it can get the correct neighbours
        if scale != 1:
            if scale == 2:
                n_offsets = [(-1, -1), (-1, 0), (-1, 1), (-1, 2), (0, -1), (0, 2), (1, -1), (1, 2), (2, -1), (2, 0), (2, 1), (2, 2), (0, 0), (0, 1), (1, 0), (1, 1)]
        else:
            n_offsets = NEIGHBOR_OFFSETS

        
        tiles = []
        #converts pixel pos into grid pos
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))

        for offset in n_offsets:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        
        return tiles
    
    #saves map
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap' : self.tilemap, 'tile_size': self.tile_size, 'offgrid' : self.offgrid_tiles}, f)
        f.close()

    #laods map
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    #check if a given position has a solid tile
    def solid_check(self, pos):
        #gets grid tile location coordinates
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        #check if location exists
        if tile_loc in self.tilemap:
            #check if location has physics (is solid object)
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
    
    #check if tiles around have physics (ex: collision)
    def physics_rects_around(self, pos, scale):
        rects = []
        for tile in self.tiles_around(pos, scale):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))

        return rects
    
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)

            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]


    def render(self, surf, offset=(0, 0), player_pos=(0, 0)):

        #on border defines if camera hitting border of map in [x, y]
        on_border = [False, False]
        player_pos = (player_pos[0]//self.tile_size + 1, player_pos[1]//self.tile_size + 1)

        for tile in self.offgrid_tiles:
           surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        #get x pos for tile and x pos for right side of screen in grid coordinates
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            #get y pos for tile and y pos for bottom side of screen in grid coordinates
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    #if there is a border type tile
                    if tile['type'] == 'border':
                        #if player distance from it is close and tile type is X, stop scrolling camera in x axis
                        if abs(tile['pos'][0] - player_pos[0]) < (surf.get_width()/2) // self.tile_size + 3 and tile['variant'] == 0:
                            on_border[0] = True
                        #if player distance from it is close and tile type is Y, stop scrolling camera in y axis
                        if abs(tile['pos'][1] - player_pos[1]) < (surf.get_height()/2) // self.tile_size + 3 and tile['variant'] == 1:
                            on_border[1] = True
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
        
        return on_border

        