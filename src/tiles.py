import pygame
import json

from typing import Dict, List, Tuple, Optional
from utils import load_image, BASE_PIXEL_SCALE, MAP_TO_JSON, GameState
from enum import Enum, auto

from dataclasses import dataclass

from entities import StaticEntity


MAX_LAYERS = 3

# all maps inside tilemaps need to be of the same size
# TODO: offtile rendering, Tiles with Animations
# Static Entities are saved on the tilemap but get rendered during the entitiy rendeirng pass

class TileMapState(Enum): DRAW = auto(); DELETE = auto();
class AssetType(Enum): ON_GRID = auto(); OFF_GRID = auto()

@dataclass
class tmAsset: 
  asset: pygame.Surface
  type: AssetType


class TileMap: 
  def __init__(self, tile_size=32, map_name:Optional[str]=None): 

    if map_name: 
      self.maps = self.load_map(MAP_TO_JSON[map_name])

    #self.maps = self.load_map()
    self.tile_size = tile_size * BASE_PIXEL_SCALE
    self.display_surface = pygame.display.get_surface()
    
    self.load_assets()

    self.layers = list(self.maps.keys())

    # stuff for tile editor
    self.selected_tileID = 1
    self.selected_layer = 1

    self.state = TileMapState.DRAW
    self.game_state = GameState.PLAYING

    self.off_grid_assets = []

    
  # whats the best way to load assets for Static Entities
  def load_assets(self): 
    self.tileIDtoTile = { 
      1: tmAsset(load_image('tilemaptest.png'), AssetType.ON_GRID),
      2: tmAsset(load_image('redtile.png'), AssetType.ON_GRID),
      3: tmAsset(load_image('../assets/danyaseethe.png', scale=False), AssetType.OFF_GRID)
    }
  
  def init_asset_cache(self): 
    pass



  def event_handler(self, event: pygame.event, camera_scroll: list[int, int]): 
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a: self.cycle_tiles()
      elif event.key == pygame.K_d: self.cycle_layers()
      elif event.key == pygame.K_f: 
        if self.state == TileMapState.DRAW: self.set_state(TileMapState.DELETE)
        elif self.state == TileMapState.DELETE: self.set_state(TileMapState.DRAW)

    # get_pressed returns (bool, bool, bool) for all 3 mouse buttons
    if pygame.mouse.get_pressed()[0]:
      if self.state == TileMapState.DRAW:
        self.place_tile_at_mouse_position(camera_scroll)

      if self.state == TileMapState.DELETE:
        self.delete_tile_at_mouse_position(camera_scroll)
  
  @property
  def layer_k(self): return f"layer_{self.selected_layer}"

  @property
  def selected_asset(self): return self.tileIDtoTile[self.selected_tileID]

  def layer_k_to_layer(self, k_str): return int(k_str.replace("layer_", ""))


  # offtile assets get rendered at entity render time
  def render(self, camera_scroll, camera_width, camera_height): 
    
    # Calculate visible tile range
    start_x = int(camera_scroll[0] // self.tile_size)
    end_x = int((camera_scroll[0] + camera_width) // self.tile_size) + 1
    start_y = int(camera_scroll[1] // self.tile_size)
    end_y = int((camera_scroll[1] + camera_height) // self.tile_size) + 1

    coordinates_to_render = [(x,y) for x in range(start_x, end_x) for y in range(start_y, end_y)]

    for layer, tile_dict in self.maps.items():
      for coord in coordinates_to_render:
        if coord in tile_dict:  # Only render if tile exists at coordinate
          screen_x = coord[0] * self.tile_size - camera_scroll[0]
          screen_y = coord[1] * self.tile_size - camera_scroll[1]

          tile_id = tile_dict[coord]
          tile_to_render = self.tileIDtoTile[tile_id].asset

          # we can make this a lot faster but I dont think it matters
          if self.game_state == GameState.MAP_EDITOR:
            layer_num = self.layer_k_to_layer(layer)
            opacity_tile = tile_to_render.copy()
            opacity_tile.set_alpha(255 if layer_num == self.selected_layer else 128)
          
            self.display_surface.blit(opacity_tile, (screen_x, screen_y))

          else:
            self.display_surface.blit(tile_to_render, (screen_x, screen_y))
    

    return self.off_grid_assets
  

  def mouse_position_to_tile(self, camera_scroll): 
    m_x, m_y = self.mouse_position(camera_scroll)

    m_tile_x = int((m_x) // self.tile_size)
    m_tile_y = int((m_y) // self.tile_size)

    return (m_tile_x, m_tile_y)
  
  def mouse_position(self, camera_scroll): 
    m_x, m_y = pygame.mouse.get_pos()
    return (m_x + camera_scroll[0], m_y + camera_scroll[1])

  # cycle through tiles
  def cycle_tiles(self):
    self.selected_tileID = (self.selected_tileID % len(self.tileIDtoTile)) + 1
    return self.selected_tileID

  # change current layer 
  def cycle_layers(self): 
    self.selected_layer = (self.selected_layer % MAX_LAYERS) + 1
    if self.selected_layer > len(self.layers): 
      self.maps[self.layer_k] = {}
    return self.selected_layer

  def set_state(self, state:TileMapState):
    if self.state != state: self.state = state

  
  # TODO: we need more tiles, we need to be able to select a tile and place it :) 
  def place_tile_at_mouse_position(self, camera_scroll): 
    if self.selected_asset.type == AssetType.OFF_GRID:
      mouse_position = self.mouse_position(camera_scroll)
      new_e = StaticEntity(mouse_position, (25,25), 'test', self.selected_asset.asset)
      self.off_grid_assets.append(new_e)
    else:
      tile_position = self.mouse_position_to_tile(camera_scroll)
      self.maps[self.layer_k][tile_position] = self.selected_tileID
  
  # this should check if the mouse is colliderecting with the StaticEntity
  def delete_tile_at_mouse_position(self, camera_scroll):
    tile_position = self.mouse_position_to_tile(camera_scroll)
    if tile_position in self.maps[self.layer_k]:
      del self.maps[self.layer_k][tile_position]
    
  
  def save_current_map(self): 
    # offgrid are saved as (pos, size, asset)
    dict_to_save = {}
    
    for map_name, map_data in self.maps.items():
      dict_to_save[map_name] = {
        str(key): value 
        for key, value in map_data.items()
      }
    
    with open('../assets/maps/map_data.json', 'w') as f:
      json.dump(dict_to_save, f, indent=2)
  
  def load_map(self, map_path): 
    with open(map_path, 'r') as f:
      json_data = json.load(f)
      
    maps_dict = {}
    for map_name, map_data in json_data.items():
      maps_dict[map_name] = {
        eval(key): value 
        for key, value in map_data.items()
      }
      
    return maps_dict
    



