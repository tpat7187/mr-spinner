import pygame

from typing import Dict, List, Tuple
from utils import load_image



# all maps inside tilemaps need to be of the same size
class TileMap: 
  def __init__(self, tile_size=32, tilemap_size=(100, 100)): 
    self.maps = {
      'background': {}  
    }
    self.tile_size = tile_size
    self.tilemap_size = tilemap_size
    self.display_surface = pygame.display.get_surface()
    
    self.load_assets()
    
    self.maps['background'] = { 
      (0,0): 1, 
    }
  
  def load_assets(self): 
    self.tileIDtoTile = { 
      1: load_image('tilemaptest.png'),
    }

  def render(self, camera_scroll, camera_width, camera_height): 
    
    # Calculate visible tile range
    start_x = int(camera_scroll[0] // self.tile_size)
    end_x = min(self.tilemap_size[0], int((camera_scroll[0] + camera_width) // self.tile_size) + 1)
    start_y = int(camera_scroll[1] // self.tile_size)
    end_y = min(self.tilemap_size[1], int((camera_scroll[1] + camera_height) // self.tile_size) + 1)

    coordinates_to_render = [(x,y) for x in range(start_x, end_x) for y in range(start_y, end_y)]

    for layer, tile_dict in self.maps.items():
      for coord in coordinates_to_render:
        if coord in tile_dict:  # Only render if tile exists at coordinate
          screen_x = coord[0] * self.tile_size - camera_scroll[0]
          screen_y = coord[1] * self.tile_size - camera_scroll[1]
          
          tile_id = tile_dict[coord]
          self.display_surface.blit(self.tileIDtoTile[tile_id], (screen_x, screen_y))
  

  def mouse_position_to_tile(self, camera_scroll): 
    m_x, m_y = pygame.mouse.get_pos()

    m_tile_x = int((m_x + camera_scroll[0] ) // self.tile_size)
    m_tile_y = int((m_y + camera_scroll[1] ) // self.tile_size)

    return (m_tile_x, m_tile_y)
  
  # TODO: we need more tiles, we need to be able to select a tile and place it :) 
  def place_tile_at_mouse_position(self, camera_scroll): 
    tile_position = self.mouse_position_to_tile(camera_scroll)
    self.maps['background'][tile_position] = 1 
  



