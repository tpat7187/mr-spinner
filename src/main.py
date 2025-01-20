from __future__ import annotations
from typing import Dict, List
import pygame
import sys
import time



from entities import PhysicsEntity
from player import Player
from tiles import TileMap
from utils import Camera, MAP_TO_JSON
from enum import Enum, auto


class GameState(Enum): PLAYING = auto(); PAUSED = auto(); MAP_EDITOR = auto(); INIT = auto();
class CollisionType(Enum): HORIZONTAL = auto(); VERTICAL = auto();

'''
game states 

map_editor -> allow user to save/load maps and place tiles
playing -> play the game
paused -> no update entities call
init -> Game startup

'''

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

    self.current_map = TileMap(tile_size=32, map_name='dev')

  # what are the benifits of using pygame sprite groups over arrays for storage?
  def init_entity_groups(self) -> None:
    # Define entitiy rendering layers
    self.layers: Dict[str, pygame.sprite.Group] = {
      'entities': pygame.sprite.Group(),
    }
    self.layer_order: List[str] = list(self.layers.keys())
  
  def set_state(self, new_state:GameState) -> str:
    if self.state != new_state:
      self.state = new_state
    
  
  # TODO: refactor
  def init_entities(self) -> None:
    # Initialize player and boxes
    self.player = Player((0, 0), (32, 32))
    box = PhysicsEntity((50, 50), (30, 30), 'box')
    self.layers['entities'].add(self.player)
    self.layers['entities'].add(box)

  def handle_events(self) -> None:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False
      
      
      # swap between game states
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_t:
          if self.state == GameState.MAP_EDITOR :self.set_state(GameState.PLAYING)
          elif self.state == GameState.PLAYING: self.set_state(GameState.MAP_EDITOR)
        elif event.key == pygame.K_ESCAPE:
          if self.state == GameState.PAUSED: self.set_state(GameState.PLAYING)
          elif self.state == GameState.PLAYING: self.set_state(GameState.PAUSED)
      
      
  def update(self, dt:float) -> None:
    if self.state == GameState.PLAYING:
      self.layers['entities'].update(dt)
      self.camera.center_camera_on_target(self.player)
    
    if self.state == GameState.MAP_EDITOR:
      if pygame.key.get_pressed()[pygame.K_g]: self.current_map.place_tile_at_mouse_position(self.camera.scroll)


  def render(self) -> None:
    self.screen.fill((0, 0, 0))


    ### RENDERING ORDER ### 
    '''
    Render Tilemap -> Layers: Hitbox, Background, Foreground
    Render Entities  -> Players, Enemies, Loot, Projectiles
    Render UI 


    TODO : Y-SORTED RENDERING ORDER
    Objects 'above' the player should be rendered before the player
    Objects 'below' the player should be rendered after the player
    
    '''

    # Render tilemap
    self.current_map.render([self.camera.scroll.x, self.camera.scroll.y], self.camera.width, self.camera.height)
    
    # Render Entities
    for layer in self.layer_order:
      if self.layers[layer]:
        for sprite in self.layers[layer]:
          sprite.render(self.camera.scroll)
    

    # Render UI 
    # TODO: abstract this away to a UIElement Class which has its own rendering Protocol
    fps_t = self.dt ** -1 if self.dt != 0 else 0
    pygame.font.init()
    my_font = pygame.font.SysFont('Times New Roman', 13)
    text_surface = my_font.render(f"FPS: <{int(fps_t)}>\nMouse Tile Positiion: <{self.current_map.mouse_position_to_tile(self.camera.scroll)}>\nState: {self.player.state}\nDirection: {self.player.direction}\nGame State: {self.state}", False, (255, 255, 255))

    fps_counter_position = ( 
      self.player.rect.x - self.camera.scroll.x + 400, 
      self.player.rect.y - self.camera.scroll.y - 320
    )

    self.screen.blit(text_surface, fps_counter_position)

    
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