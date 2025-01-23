import pygame
import json
from typing import Dict, List, Tuple, Optional
from utils import load_image, BASE_PIXEL_SCALE, MAP_TO_JSON, GameState, tmAsset, AssetType
from enum import Enum, auto
from entities import StaticEntity

MAX_LAYERS = 3

class TileMapState(Enum): DRAW_ON_GRID = auto(); DELETE = auto(); DRAW_OFF_GRID = auto();


class TileMap:
  def __init__(self, tile_size=32, map_name: Optional[str]=None):
    self.load_assets()


    self.maps, self.off_grid_assets = self._init_map(map_name) 

    self.tile_size = tile_size * BASE_PIXEL_SCALE
    self.display_surface = pygame.display.get_surface()

    self.layers = list(self.maps.keys()) 

    # For tile editor
    self.selected_tile_id = 1
    self.selected_layer = 1
    self.state = TileMapState.DRAW_ON_GRID
    self.game_state = GameState.PLAYING

    self.to_entity_renderer = []

  def _init_map(self, map_name:Optional[str]=None) -> Tuple[Dict, List[StaticEntity]]: 
    if map_name: return self.load_map(MAP_TO_JSON[map_name])
    else: return ({'layer_1': {}, 'offgrid': {}, 'boundary': {}}, [])
  
  @property
  def selected_asset_type(self): return self.tileIDtoTile[self.selected_tile_id].type


  # AssetTypes
  # TileRend : Render at Tile Map Rendering Time
  # EntityRend : Render at Entity Rendering Time (Y Sorted)
  # EntityRend Assets do NOT have collision physics
  # Drawing Mode : Off Grid / On Grid

  # Off Grid -> All drawn asses will be Entities With Collisions
  # On Grid -> We need to place Collision boxes manually using the boundary layer
  def load_assets(self):
    self.tileIDtoTile = {
      1: tmAsset(load_image('tilemaptest.png'), AssetType.TileRend, 1),
      2: tmAsset(load_image('redtile.png'), AssetType.TileRend, 2),
      3: tmAsset(load_image('danyaseethe.png', scale=False), AssetType.EntityRend, 3),
      4: tmAsset(load_image('passthrutest.png', scale=True), AssetType.EntityRend, 4)
    }


  # TODO: do we still want boundary edit ops to happen during runtime
  def event_handler(self, event: pygame.event.Event, camera_scroll: Tuple[int,int]) -> Optional[dict]:
    result = {'spawned_entity': None,
              'added_boundary' : None,
              'removed_entity': None, 
              'removed_boundary': None}

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a: self.cycle_tiles()
      elif event.key == pygame.K_d: self.cycle_layers()
      elif event.key == pygame.K_f:
        if self.state == TileMapState.DRAW_ON_GRID: self.set_state(TileMapState.DELETE)
        elif self.state == TileMapState.DELETE: self.set_state(TileMapState.DRAW_OFF_GRID)
        elif self.state == TileMapState.DRAW_OFF_GRID: self.set_state(TileMapState.DRAW_ON_GRID)
      elif event.key == pygame.K_e: 
        if self.selected_layer != 'Boundary': self.selected_layer = 'Boundary'
        elif self.selected_layer == 'Boundary': self.selected_layer = 1

    # Check for mouse press
    if pygame.mouse.get_pressed()[0]:
      if self.state in (TileMapState.DRAW_ON_GRID, TileMapState.DRAW_OFF_GRID):
        newly_spawned = self.place_tile_at_mouse_position(camera_scroll)
        if newly_spawned: result['spawned_entity'] = newly_spawned

      elif self.state == TileMapState.DELETE:
        removed = self.delete_tile_at_mouse_position(camera_scroll)
        if removed: result['removed_entity'] = removed

    # return None if no entities were spaned
    if all(result.values()) is None: return None
    return result

  @property
  def layer_k(self) -> str: 
      return f"layer_{self.selected_layer}" if self.selected_layer != "Boundary" else 'boundary'

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

    # when in map editor, show boundary tiles
    for layer, tile_dict in self.maps.items():
      # skip offgrid / Boundary tiles layer in tile rendering
      if 'layer' not in layer:
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

    if self.game_state == GameState.MAP_EDITOR:
      for coord in coordinates_to_render:
        if coord in self.maps['boundary']:
          screen_x = coord[0] * self.tile_size - camera_scroll[0]
          screen_y = coord[1] * self.tile_size - camera_scroll[1]
          tile_surf = pygame.Surface((self.tile_size, self.tile_size))
          tile_surf.fill((255, 0, 0))

          self.display_surface.blit(tile_surf, (screen_x, screen_y))
  
    return self.to_entity_renderer

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
    if self.selected_layer != 'Boundary':
      self.selected_layer = (self.selected_layer % MAX_LAYERS) + 1
      if self.selected_layer > len(self.layers):
        self.maps[self.layer_k] = {}
      return self.selected_layer

  def set_state(self, state: TileMapState):
    if self.state != state: self.state = state

  def place_tile_at_mouse_position(self, camera_scroll) -> Optional[StaticEntity]:
    m_p = self.mouse_position(camera_scroll) if self.state == TileMapState.DRAW_OFF_GRID else self.mouse_position_to_tile(camera_scroll)

    if self.selected_layer == 'Boundary':
      self.maps[self.layer_k][m_p] = 0

    if self.state == TileMapState.DRAW_OFF_GRID:
      new_e = StaticEntity(m_p, asset=self.selected_asset)
      self.off_grid_assets.append(new_e)
      self.maps['offgrid'][m_p] = self.selected_asset.id
      return new_e
    
    if self.selected_asset_type == AssetType.EntityRend:
      # this should be a part of off_grid assets but shouldnt be colliding with the player
      n_p = (m_p[0] * self.tile_size, m_p[1] * self.tile_size)
      new_e = StaticEntity(n_p, asset=self.selected_asset)
      self.to_entity_renderer.append(new_e)
      self.maps[self.layer_k][n_p] = self.selected_tile_id if self.selected_layer != 'Boundary' else 0 
    
    else:
      self.maps[self.layer_k][m_p] = self.selected_tile_id

    return None
    
    
  
  def get_boundary_tiles(self): return self.maps['boundary']

  def delete_tile_at_mouse_position(self, camera_scroll) -> Optional[StaticEntity]:
    mp = self.mouse_position(camera_scroll)
    for entity in self.off_grid_assets:
      if entity.rect.collidepoint(mp):
        self.off_grid_assets.remove(entity)
        return entity 

    tile_position = self.mouse_position_to_tile(camera_scroll)
    layer_key = self.layer_k if self.selected_layer != 'Boundary' else 'boundary'
    if tile_position in self.maps[layer_key]:
      del self.maps[layer_key][tile_position]
    return None

  def save_current_map(self):
    dict_to_save = {}

    for map_name, map_data in self.maps.items():
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
      
    with open('../assets/maps/map_data.json', 'w') as f:
      json.dump(dict_to_save, f, indent=2)

  def load_map(self, map_path):
    # TODO: pass AssetType.Entities on grid to the entity renderer
    with open(map_path, 'r') as f:
      json_data = json.load(f)

    maps_dict, off_grid = self._init_map(None)

    for map_name, map_data in json_data.items():
      maps_dict[map_name] = {
        eval(key): value
        for key, value in map_data.items()
      }

    if 'offgrid' in maps_dict:
      for pos, tile_id in maps_dict['offgrid'].items():
        asset = self.tileIDtoTile[tile_id]
        ent = StaticEntity(tuple(pos), asset=asset)
        off_grid.append(ent)

    return maps_dict, off_grid


