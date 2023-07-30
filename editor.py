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
        self.font = pygame.font.Font(None, 40)

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
        self.layers = []
        if len(self.data['input']['files']) > 0:
            print('generating layers!')
            files = self.data['input']['files']
            for index in range(len(files)):
                layer = {}
                with open(files[index], 'r', newline='') as f:
                    reader = csv.reader(f)
                    for y, row in enumerate(reader):
                        for x, id in enumerate(row):
                            for name, item in self.data['palette']['tiles'].items():
                                if item['id'] == int(id):
                                    if x < self.data['size'][0] and y < self.data['size'][1]:
                                        layer[(x,y)] = {'position': (x*Editor.TILESIZE, y*Editor.TILESIZE), 
                                                        'image':self.palette[item['id']]['image'],
                                                        'id':item['id'],
                                                        'layer':index}
                
                self.layers.append(layer)
        else:
            self.layers = [
                {}
            ]

        # states
        self.palette_open: bool = True
        self.active_layer = 0
        self.layers_on = self.data['config']['layers']

        # assets
        self.bg = pygame.image.load(self.data['config']['background']).convert()
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
            if not self.active_layer < len(self.layers):
                self.layers.append({})
                print('created new layer!')
            if coord not in self.layers[self.active_layer]:
                tile_pos = ((position[0] // Editor.TILESIZE) * TILESIZE, (position[1] // Editor.TILESIZE) * TILESIZE)
                self.layers[self.active_layer][coord] = {'position': tile_pos, 
                                                        'image':self.palette[self.active_slot]['image'],
                                                        'id':self.palette[self.active_slot]['id'],
                                                        'layer':self.active_layer}
        # removing
        if EventHandler.clicked(3) and self.tile_map_rect.collidepoint(mouse_pos):
            position = [mouse_pos[0] - self.tile_map_rect.x, mouse_pos[1] - self.tile_map_rect.y]
            coord = (position[0] // Editor.TILESIZE, position[1] // Editor.TILESIZE)
            if coord in self.layers[self.active_layer]:
                self.layers[self.active_layer].pop(coord)

        if EventHandler.keydown(pygame.K_0):
            self.export()
        if EventHandler.keydown(pygame.K_9):
            self.render_to_surface()
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
        if self.layers_on:
            if EventHandler.keydown(pygame.K_UP):
                self.active_layer += 1
                print(self.active_layer)
            if EventHandler.keydown(pygame.K_DOWN):
                self.active_layer -= 1
                if self.active_layer < 0:
                    self.active_layer = 0
                print(self.active_layer)

        # --- drawing ---

        self.screen.blit(self.bg, (0,-50))
        self.screen.blit(self.tilemap_surface, self.tile_map_rect)

        for layer in self.layers:
            for tile in layer.values():
                self.screen.blit(tile['image'], (tile['position'][0] + self.tile_map_rect.x, tile['position'][1] + self.tile_map_rect.y))
    
        if self.palette_open:
            index = 0
            for item in self.palette:
                
                self.screen.blit(item['image'], (index * Editor.TILESIZE + Editor.TILESIZE, self.screen.get_height() - (Editor.TILESIZE * 2)))
                if index == self.active_slot:
                    pygame.draw.rect(self.screen, 
                                     "white", 
                                     pygame.Rect(index * TILESIZE + Editor.TILESIZE, 
                                                 self.screen.get_height() - (Editor.TILESIZE * 2), 
                                                 Editor.TILESIZE, 
                                                 Editor.TILESIZE), 
                                                 2)
                index += 1
        if self.layers_on:
            self.active_layer_text = self.font.render(f'Layer: {self.active_layer}', True, "white", "black")
            self.screen.blit(self.active_layer_text, (0,0))
        
    
    def export(self):
        self.output_dir = self.data['output']['output_folder']
        self.filename = self.data['output']['file_name']
        if os.path.exists(self.output_dir):
            pass
        else:
            os.makedirs(self.output_dir)
        if self.data['config']['layers']:
            output_data: list[list[list[int]]] = []

            for index in range(len(self.layers)):
                layer_data = []

                for y in range(self.TILEMAP_SIZE[1]):
                    row = []
                    for x in range(self.TILEMAP_SIZE[0]):
                        if (x,y) in self.layers[index]:
                            row.append(self.layers[index][(x,y)]['id'])
                        else:
                            row.append(-1)
                    layer_data.append(row)
                output_data.append(layer_data)
            print(len(output_data))

            count = 0
            name = self.filename
            og_name = name
            while os.path.exists(os.path.join(self.output_dir, f'{self.data["config"]["layer_leader"]}{index}-{name}.csv')):
                    count += 1
                    name = f'{og_name}({count})'
                    

            for index in range(len(self.layers)):
                name= f'{self.data["config"]["layer_leader"]}{index}-{name}'
                print(name)
                with open(os.path.join(self.output_dir, f'{name}.csv'), 'w', newline='') as f:
                    writer = csv.writer(f)

                    for row in output_data[index]:
                        writer.writerow(row)
                if name.endswith(')'):
                    name = f'{og_name}({count})'
                else:
                    name = og_name

            if self.data['output']['produce_data_mapper']:
                with open(os.path.join(self.output_dir, f'{self.filename}.json'), 'w') as f:
                    json.dump(self.data['palette']['tiles'], f)   
        else:
            output_data: list[list[int]] = []

            for y in range(self.TILEMAP_SIZE[1]):

                row = []

                for x in range(self.TILEMAP_SIZE[0]):
                    if (x,y) in self.layers[0]:
                        row.append(self.layers[0][(x,y)]['id'])
                    else:
                        row.append(-1)
                output_data.append(row)

            count = 0
            name = self.filename

            while os.path.exists(os.path.join(self.output_dir, f'{self.filename}.csv')):
                count += 1
                self.filename = f'{name}({count})'
                
            with open(os.path.join(self.output_dir, f'{self.filename}.csv'), 'w', newline='') as f:
                writer = csv.writer(f)

                for row in output_data:
                    writer.writerow(row)   

            if self.data['output']['produce_data_mapper']:
                with open(os.path.join(self.output_dir, f'{self.filename}.json'), 'w') as f:
                    json.dump(self.data['palette']['tiles'], f)      
    def render_to_surface(self):
        if self.data['export']['image_gridlines']:
            surface = self.tilemap_surface.copy()
        else:
            surface = pygame.Surface(self.tilemap_surface.get_size())
        for layer in self.layers:
            for tile in layer.values():
                surface.blit(tile['image'], (tile['position'][0],tile['position'][1]))

        if not os.path.exists('output/saves'):
            os.makedirs('output/saves')

        filename = 'save'
        count = 0
        while os.path.exists(f'output/saves/{filename}.png'):
            filename = f'save({count})'
            count += 1
        pygame.image.save(surface, f'output/saves/{filename}.png')  
