import pygame
import json
from typing import Dict, List, Tuple, Optional
from utils import load_image, BASE_PIXEL_SCALE, MAP_TO_JSON, GameState, tmAsset, AssetType
from enum import Enum, auto
from entities import StaticEntity

MAX_LAYERS = 3

class TileMapState(Enum): DRAW = auto(); DELETE = auto();


class TileMap:
  def __init__(self, tile_size=31, map_name: Optional[str]=None):
    self.load_assets()

    if map_name:
      self.maps, self.off_grid_assets = self.load_map(MAP_TO_JSON[map_name])

    self.tile_size = tile_size * BASE_PIXEL_SCALE
    self.display_surface = pygame.display.get_surface()

    self.layers = list(self.maps.keys()) 

    # For tile editor
    self.selected_tile_id = 1
    self.selected_layer = 1
    self.state = TileMapState.DRAW
    self.game_state = GameState.PLAYING

    # Make sure offgrid layer and asset list exist
    if 'offgrid' not in self.maps: self.maps['offgrid'] = {}
    if self.off_grid_assets is None: self.off_grid_assets = []

  def load_assets(self):
    self.tileIDtoTile = {
      1: tmAsset(load_image('tilemaptest.png'), AssetType.ON_GRID, 1),
      2: tmAsset(load_image('redtile.png'), AssetType.ON_GRID, 2),
      3: tmAsset(load_image('../assets/danyaseethe.png', scale=False), AssetType.OFF_GRID, 3)
    }

  def event_handler(self, event: pygame.event.Event, camera_scroll: Tuple[int,int]) -> Optional[dict]:
    result = {'spawned_entity': None, 'removed_entity': None}

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a: self.cycle_tiles()
      elif event.key == pygame.K_d: self.cycle_layers()
      elif event.key == pygame.K_f:
        if self.state == TileMapState.DRAW: self.set_state(TileMapState.DELETE)
        elif self.state == TileMapState.DELETE: self.set_state(TileMapState.DRAW)

    # Check for mouse press
    if pygame.mouse.get_pressed()[0]:
      if self.state == TileMapState.DRAW:
        newly_spawned = self.place_tile_at_mouse_position(camera_scroll)
        if newly_spawned: result['spawned_entity'] = newly_spawned
      elif self.state == TileMapState.DELETE:
        removed = self.delete_tile_at_mouse_position(camera_scroll)
        if removed: result['removed_entity'] = removed

    # return None if no entities were spaned
    if not result['spawned_entity'] and not result['removed_entity']: return None
    return result

  @property
  def layer_k(self) -> str: return f"layer_{self.selected_layer}"

  @property
  def selected_asset(self) -> tmAsset: return self.tileIDtoTile[self.selected_tile_id]

  def layer_k_to_layer(self, k_str: str) -> int: return int(k_str.replace("layer_", ""))

  def render(self, camera_scroll, camera_width, camera_height):
    # Calculate the visible tile range
    start_x = int(camera_scroll[0] // self.tile_size)
    end_x   = int((camera_scroll[0] + camera_width) // self.tile_size) + 1
    start_y = int(camera_scroll[1] // self.tile_size)
    end_y   = int((camera_scroll[1] + camera_height) // self.tile_size) + 1

    coordinates_to_render = [(x, y) for x in range(start_x, end_x) for y in range(start_y, end_y)]

    for layer, tile_dict in self.maps.items():
      # skip offgrid layer in tile rendering
      if layer == 'offgrid':
        continue
      for coord in coordinates_to_render:
        if coord in tile_dict:
          screen_x = coord[0] * self.tile_size - camera_scroll[0]
          screen_y = coord[1] * self.tile_size - camera_scroll[1]
          tile_id = tile_dict[coord]
          tile_surf = self.tileIDtoTile[tile_id].asset

          if self.game_state == GameState.MAP_EDITOR:
            layer_num = self.layer_k_to_layer(layer)
            temp = tile_surf.copy()
            temp.set_alpha(255 if layer_num == self.selected_layer else 128)
            self.display_surface.blit(temp, (screen_x, screen_y))
          else:
            self.display_surface.blit(tile_surf, (screen_x, screen_y))

  def mouse_position_to_tile(self, camera_scroll):
    m_x, m_y = self.mouse_position(camera_scroll)
    m_tile_x = int(m_x // self.tile_size)
    m_tile_y = int(m_y // self.tile_size)
    return (m_tile_x, m_tile_y)

  def mouse_position(self, camera_scroll):
    m_x, m_y = pygame.mouse.get_pos()
    return (m_x + camera_scroll[0], m_y + camera_scroll[1])

  def cycle_tiles(self) -> int:
    self.selected_tile_id = (self.selected_tile_id % len(self.tileIDtoTile)) + 1
    return self.selected_tile_id

  def cycle_layers(self) -> int:
    self.selected_layer = (self.selected_layer % MAX_LAYERS) + 1
    if self.selected_layer > len(self.layers):
      self.maps[self.layer_k] = {}
    return self.selected_layer

  def set_state(self, state: TileMapState):
    if self.state != state:
      self.state = state

  def place_tile_at_mouse_position(self, camera_scroll) -> Optional[StaticEntity]:
    if self.selected_asset.type == AssetType.OFF_GRID:
      mouse_position = self.mouse_position(camera_scroll)
      new_e = StaticEntity(mouse_position, asset=self.selected_asset)
      self.off_grid_assets.append(new_e)
      self.maps['offgrid'][mouse_position] = self.selected_asset.id
      return new_e
    else:
      tile_position = self.mouse_position_to_tile(camera_scroll)
      self.maps[self.layer_k][tile_position] = self.selected_tile_id
    return None

  def delete_tile_at_mouse_position(self, camera_scroll) -> Optional[StaticEntity]:
    mp = self.mouse_position(camera_scroll)
    for entity in self.off_grid_assets:
      if entity.rect.collidepoint(mp):
        self.off_grid_assets.remove(entity)
        if mp in self.maps['offgrid']:
          del self.maps['offgrid'][mp]
        return entity 

    tile_position = self.mouse_position_to_tile(camera_scroll)
    if tile_position in self.maps[self.layer_k]:
      del self.maps[self.layer_k][tile_position]
    return None

  def save_current_map(self):
    dict_to_save = {}

    for map_name, map_data in self.maps.items():
      print(map_name)
      if map_name != 'offgrid':
        dict_to_save[map_name] = {
          str(key): value
          for key, value in map_data.items()
        }
      else:
        for j in self.off_grid_assets: 
          dict_to_save[map_name] = { 
            str(j.get_pos): j.get_asset_id
          }

          print(dict_to_save[map_name])
      
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

    off_grid = []

    if 'offgrid' in maps_dict:
      for pos, tile_id in maps_dict['offgrid'].items():
        asset = self.tileIDtoTile[tile_id]
        ent = StaticEntity(tuple(pos), asset=asset)
        off_grid.append(ent)

    return maps_dict, off_grid


