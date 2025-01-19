from __future__ import annotations
from typing import Dict, List
import pygame
import sys
from entities import PhysicsEntity, Player
from tiles import TileMap
from utils import Camera

class Game:
  def __init__(self): 
    pygame.init()
    pygame.display.set_caption("Mr_Spinner")
    self.width, self.height = 1280, 720
    self.screen = pygame.display.set_mode((self.width, self.height))
    self.clock = pygame.time.Clock()
    self.running = True
    self.FPS = 144 # TODO: FRAME RATE INDEPENDENCE, VERY IMPORTANT
    
    self.camera = Camera(self.width, self.height)
    self.init_entity_groups()
    self.init_entities()

    self.mouse_position = None

    self.current_map = TileMap()



  # TODO: refactor, sprite groups are kinda cringe we could just use lists OMEGALUL
  def init_entity_groups(self) -> None:
    # Define entitiy rendering layers
    self.layers: Dict[str, pygame.sprite.Group] = {
      'entities': pygame.sprite.Group(),
    }
    self.layer_order: List[str] = list(self.layers.keys())
  
  # TODO: refactor
  def init_entities(self) -> None:
    # Initialize player and boxes
    self.player = Player((0, 0), (50, 50))
    box = PhysicsEntity((50, 50), (30, 30), 'box')
    self.layers['entities'].add(self.player)
    self.layers['entities'].add(box)

  def handle_events(self) -> None:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False
      
  def update(self) -> None:
    self.layers['entities'].update()
    self.camera.center_camera_on_target(self.player)
    self.handle_collisions()

    # TODO: put this somewhere
    if pygame.key.get_pressed()[pygame.K_t]: self.current_map.place_tile_at_mouse_position(self.camera.scroll)

  # TODO: this sucks
  def handle_collisions(self) -> None:
    collisions = pygame.sprite.spritecollide(self.player, self.layers['entities'], False)
    for entity in collisions:
      if entity != self.player:
        self.resolve_collision(self.player, entity)

  # TODO: this sucks
  def resolve_collision(self, entity1: PhysicsEntity, entity2: PhysicsEntity) -> None:
    # Handle vertical collisions
    if (entity1.rect.right > entity2.rect.left and 
        entity1.rect.left < entity2.rect.right):
      if (entity1.rect.bottom > entity2.rect.top and 
          entity1.pos.y + entity1.rect.height <= entity2.rect.top):
        entity1.rect.bottom = entity2.rect.top
      elif (entity1.rect.top < entity2.rect.bottom and 
            entity1.pos.y >= entity2.rect.bottom):
        entity1.rect.top = entity2.rect.bottom

    # Handle horizontal collisions
    if (entity1.rect.bottom > entity2.rect.top and 
        entity1.rect.top < entity2.rect.bottom):
      
      if (entity1.rect.right > entity2.rect.left and 
          entity1.pos.x + entity1.rect.width <= entity2.rect.left):
        entity1.rect.right = entity2.rect.left
      elif (entity1.rect.left < entity2.rect.right and 
            entity1.pos.x >= entity2.rect.right):
        entity1.rect.left = entity2.rect.right

  def render(self) -> None:
    self.screen.fill((0, 0, 0))


    ### RENDERING ORDER ### 
    '''
    Render Tilemap -> Layers: Hitbox, Background, Foreground
    Render Entities  -> Players, Enemies, Loot, Projectiles
    Render UI 
    
    '''

    # Render tilemap
    self.current_map.render([self.camera.scroll.x, self.camera.scroll.y], self.camera.width, self.camera.height)
    
    # Render Entities
    # TODO: Can we abtract away the rendering to the PhysicsEntity Object, so we'd just call render for every sprite in the layer
    for layer in self.layer_order:
      if self.layers[layer]:
        for sprite in self.layers[layer]:
          screen_pos = (
            sprite.rect.x - self.camera.scroll.x,
            sprite.rect.y - self.camera.scroll.y
          )
          self.screen.blit(sprite.image, screen_pos)
    

    # Render UI 
    # TODO: abstract this away to a UIElement Class which has its own rendering Protocol
    fps_t = self.clock.get_fps()
    pygame.font.init()
    my_font = pygame.font.SysFont('Times New Roman', 13)
    text_surface = my_font.render(f"FPS: <{int(fps_t)}> Mouse Tile Positiion: <{self.current_map.mouse_position_to_tile(self.camera.scroll)}>", False, (255, 255, 255))

    fps_counter_position = ( 
      self.player.rect.x - self.camera.scroll.x + 400, 
      self.player.rect.y - self.camera.scroll.y - 320
    )

    self.screen.blit(text_surface, fps_counter_position)

    
    pygame.display.update()

  def run(self) -> None:
    while self.running:
      self.handle_events()
      self.update()
      self.render()
      self.clock.tick(self.FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
  game = Game()
  game.run()