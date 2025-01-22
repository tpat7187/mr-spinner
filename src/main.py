from __future__ import annotations
from typing import Dict, List
import pygame
import sys
import time

from player import Player
from tiles import TileMap
from utils import Camera, MAP_TO_JSON, GameState
from enum import Enum, auto


class CollisionType(Enum):
  HORIZONTAL = auto()
  VERTICAL = auto()

class Game:
  def __init__(self):
    pygame.init()
    pygame.display.set_caption("Mr_Spinner")
    self.width, self.height = 1280, 720
    self.screen = pygame.display.set_mode((self.width, self.height))
    self.running = True
    self.state = GameState.PLAYING

    self.camera = Camera(self.width, self.height)
    self.init_entity_groups()
    self.init_entities()

    self.mouse_position = None

    # init tilemap
    self.current_map = TileMap(tile_size=32, map_name='dev')
    
    for offgrid_entity in self.current_map.off_grid_assets:
      self.entities.add(offgrid_entity)

  def init_entity_groups(self) -> None:
    self.entities = pygame.sprite.Group()

  def set_state(self, new_state: GameState) -> None:
    if self.state != new_state:
      self.state = new_state
      self.current_map.game_state = new_state

  def init_entities(self) -> None:
    self.player = Player((0, 0), (32, 32))
    self.entities.add(self.player)

  def handle_events(self) -> None:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.current_map.save_current_map()
        self.running = False

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_t:
          if self.state == GameState.MAP_EDITOR: self.set_state(GameState.PLAYING)
          elif self.state == GameState.PLAYING: self.set_state(GameState.MAP_EDITOR)
        elif event.key == pygame.K_ESCAPE:
          if self.state == GameState.PAUSED: self.set_state(GameState.PLAYING)
          elif self.state == GameState.PLAYING: self.set_state(GameState.PAUSED)

      if self.state == GameState.MAP_EDITOR:
        tilemap_action = self.current_map.event_handler(event, self.camera.scroll)
        
        if tilemap_action and tilemap_action.get('spawned_entity'):
          new_entity = tilemap_action['spawned_entity']
          self.entities.add(new_entity)

        if tilemap_action and tilemap_action.get('removed_entity'):
          rm_entity = tilemap_action['removed_entity']
          if rm_entity in self.entities:
            self.entities.remove(rm_entity)

  def update(self, dt: float) -> None:
    if self.state == GameState.PLAYING:
      self.entities.update(dt)
      self.camera.center_camera_on_target(self.player)

  def render(self) -> None:
    self.screen.fill((0, 0, 0))

    # 1) Render Tilemap
    self.current_map.render([self.camera.scroll.x, self.camera.scroll.y], self.camera.width, self.camera.height)

    # 2) Render y-sorted entities
    for sprite in sorted(self.entities, key=lambda s: s.rect.bottom):
      sprite.render(self.camera.scroll)

    # 3) Render UI
    fps_t = 1 / self.dt if self.dt else 0
    pygame.font.init()
    my_font = pygame.font.SysFont('Times New Roman', 13)
    text_surface = my_font.render(
      f"FPS: <{int(fps_t)}>\n"
      f"Mouse Tile Position: <{self.current_map.mouse_position_to_tile(self.camera.scroll)}>\n"
      f"State: {self.player.state}\n"
      f"Direction: {self.player.direction}\n"
      f"Game State: {self.state}", 
      False, (255, 255, 255)
    )

    fps_counter_position = (
      self.player.rect.x - self.camera.scroll.x + 400,
      self.player.rect.y - self.camera.scroll.y - 320
    )
    self.screen.blit(text_surface, fps_counter_position)

    # If in MAP_EDITOR, show tile selection info
    if self.state == GameState.MAP_EDITOR:
      map_editor_ui = my_font.render(
        f"selected tile: {self.current_map.selected_tile_id}\n"
        f"selected layer: {self.current_map.selected_layer}\n"
        f"editor state: {self.current_map.state}",
        False, (255, 255, 255)
      )
      map_editor_ui_pos = ( 
        self.player.rect.x - self.camera.scroll.x - 600,
        self.player.rect.y - self.camera.scroll.y - 320
      )
      self.screen.blit(map_editor_ui, map_editor_ui_pos)

    pygame.display.update()

  def run(self) -> None:
    previous_time = time.time()
    while self.running:
      self.dt = (time.time() - previous_time)
      previous_time = time.time()

      self.handle_events()
      self.update(self.dt)
      self.render()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
  game = Game()
  game.run()