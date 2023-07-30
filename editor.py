import pygame
from config import *
import json
import os
import csv
from utils import EventHandler

class Editor:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        # vars
        Editor.TILESIZE = TILESIZE
        self.active_slot = 0

        with open('config.json', 'r') as f:
            data = json.load(f)
            self.data = data
        self.TILEMAP_SIZE = data['size']
        atlas = pygame.transform.scale(pygame.image.load(os.path.join(data['palette']['path'], data['palette']['atlas'])).convert_alpha(),
                                       (TILESIZE * data['palette']['atlas_size'][0], TILESIZE * data['palette']['atlas_size'][1]))
        
        self.palette = []
        
        for name, item in data['palette']['tiles'].items():
            self.palette.append({'id': item['id'], 'image': atlas.subsurface(
                pygame.Rect(item['position'][0]*Editor.TILESIZE, 
                            item['position'][1]*Editor.TILESIZE, 
                            TILESIZE, 
                            TILESIZE)
            )})

        self.tilemap_surface = pygame.Surface((Editor.TILESIZE * self.TILEMAP_SIZE[0], Editor.TILESIZE * self.TILEMAP_SIZE[1]))
        
        if self.data['config']['tilemap_bg']:
            image = pygame.transform.scale(pygame.image.load(self.data['config']['tilemap_bg']).convert(), 
                                           (self.tilemap_surface.get_width(), self.tilemap_surface.get_height()))
            self.tilemap_surface.blit(image, (0,0))
        else:
            for x in range(self.TILEMAP_SIZE[0]):
                for y in range(self.TILEMAP_SIZE[1]):
                    if y % 2 != 0 and x % 2 != 0:
                        pygame.draw.rect(self.tilemap_surface, 
                                        self.data['config']['tilemap_grid_color_1'],
                                        pygame.Rect(x * Editor.TILESIZE, y * Editor.TILESIZE, Editor.TILESIZE, Editor.TILESIZE))
                    elif y % 2 == 0 and x % 2 == 0:
                        pygame.draw.rect(self.tilemap_surface, 
                                        self.data['config']['tilemap_grid_color_1'],
                                        pygame.Rect(x * Editor.TILESIZE, y * Editor.TILESIZE, Editor.TILESIZE, Editor.TILESIZE))
                    else:
                        pygame.draw.rect(self.tilemap_surface, 
                                        self.data['config']['tilemap_grid_color_0'],
                                        pygame.Rect(x * Editor.TILESIZE, y * Editor.TILESIZE, Editor.TILESIZE, Editor.TILESIZE))
        for x in range(self.TILEMAP_SIZE[0]):
            pygame.draw.line(self.tilemap_surface, "white", 
                             (x * Editor.TILESIZE, 0), 
                             (x * Editor.TILESIZE, Editor.TILESIZE * self.TILEMAP_SIZE[1]),
                             1)
        for y in range(self.TILEMAP_SIZE[1]):
            pygame.draw.line(self.tilemap_surface,
                             "white",
                             (0, Editor.TILESIZE * y),
                             (self.TILEMAP_SIZE[0] * Editor.TILESIZE, Editor.TILESIZE * y),
                             1)
        self.tile_map_rect = self.tilemap_surface.get_rect(topleft = (0,0))
        self.tile_map_surface_og = self.tilemap_surface.copy()
                    
        

        # entities
        self.tiles = {}
        self.tiles[(1,1)] = {'position': (Editor.TILESIZE, Editor.TILESIZE), 
                             'image':self.palette[0]['image'], 
                             'id':self.palette[0]['id']}

        # states
        self.palette_open: bool = False

        # assets
        self.bg = pygame.image.load('assets/berkbg.jpg').convert()
        self.bg = pygame.transform.scale_by(self.bg, 0.667)
    def run(self):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if keys[pygame.K_a]:
            self.tile_map_rect.x += 5
        if keys[pygame.K_d]:
            self.tile_map_rect.x -= 5
        if keys[pygame.K_w]:
            self.tile_map_rect.y += 5
        if keys[pygame.K_s]:
            self.tile_map_rect.y -= 5

       
        # placing
        if EventHandler.clicked() and self.tile_map_rect.collidepoint(mouse_pos):
            position = [mouse_pos[0] - self.tile_map_rect.x, mouse_pos[1] - self.tile_map_rect.y]
            coord = (position[0] // Editor.TILESIZE, position[1] // Editor.TILESIZE)
            if coord not in self.tiles:
                tile_pos = ((position[0] // Editor.TILESIZE) * TILESIZE, (position[1] // Editor.TILESIZE) * TILESIZE)
                self.tiles[coord] = {'position': tile_pos, 
                                     'image':self.palette[self.active_slot]['image'],
                                     'id':self.palette[self.active_slot]['id']}
        # removing
        if EventHandler.clicked(3) and self.tile_map_rect.collidepoint(mouse_pos):
            position = [mouse_pos[0] - self.tile_map_rect.x, mouse_pos[1] - self.tile_map_rect.y]
            coord = (position[0] // Editor.TILESIZE, position[1] // Editor.TILESIZE)
            if coord in self.tiles:
                self.tiles.pop(coord)

        if EventHandler.keydown(pygame.K_0):
            self.export()
        if EventHandler.keydown(pygame.K_p):
            self.palette_open = not self.palette_open

        if EventHandler.scroll_wheel_up():
            if self.active_slot > 0:
                self.active_slot -= 1
            else:
                self.active_slot = len(self.palette)-1
        if EventHandler.scroll_wheel_down():
            if self.active_slot < len(self.palette)-1:
                self.active_slot += 1
            else:
                self.active_slot = 0

        # --- drawing ---

        self.screen.blit(self.bg, (0,-50))
        self.screen.blit(self.tilemap_surface, self.tile_map_rect)

        for tile in self.tiles.values():
            self.screen.blit(tile['image'], (tile['position'][0] + self.tile_map_rect.x, tile['position'][1] + self.tile_map_rect.y))
    
        if self.palette_open:
            index = 0
            for item in self.palette:
                
                self.screen.blit(item['image'], (index * Editor.TILESIZE, self.screen.get_height() - (Editor.TILESIZE * 2)))
                if index == self.active_slot:
                    pygame.draw.rect(self.screen, 
                                     "white", 
                                     pygame.Rect(index * TILESIZE, 
                                                 self.screen.get_height() - (Editor.TILESIZE * 2), 
                                                 Editor.TILESIZE, 
                                                 Editor.TILESIZE), 
                                                 2)
                index += 1
    
    def export(self):
        self.output_dir = self.data['output']['output_folder']
        self.filename = self.data['output']['file_name']
        if os.path.exists(self.output_dir):
            pass
        else:
            os.makedirs(self.output_dir)

        output_data: list[list[int]] = []

        for y in range(self.TILEMAP_SIZE[1]):

            row = []

            for x in range(self.TILEMAP_SIZE[0]):
                if (x,y) in self.tiles:
                    row.append(self.tiles[(x,y)]['id'])
                else:
                    row.append(-1)
            output_data.append(row)

        count = 0
        name = self.filename
        while os.path.exists(os.path.join(self.output_dir, f'{self.filename}.csv')):
            self.filename = f'{name}({count})'
            count += 1
        with open(os.path.join(self.output_dir, f'{self.filename}.csv'), 'w', newline='') as f:
            writer = csv.writer(f)

            for row in output_data:
                writer.writerow(row)   

        if self.data['output']['produce_data_mapper']:
            with open(os.path.join(self.output_dir, f'{self.filename}.json'), 'w') as f:
                json.dump(self.data['palette']['tiles'], f)        
