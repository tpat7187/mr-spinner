from __future__ import annotations
from typing import Tuple, Optional
from utils import load_image
import pygame

from animation import Animation
from enum import Enum, auto


class CollisionAxis(Enum): HORIZONTAL = auto(); VERTICAL = auto();
class EntityState(Enum): IDLE = auto(); MOVING = auto();

class PhysicsEntity(pygame.sprite.Sprite): 
  def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], e_type:str, asset_path:Optional[str]=None): 
    super().__init__()  
    self.display_surface = pygame.display.get_surface()
    
    # image data
    if asset_path is not None: 
      self.image = load_image(asset_path)
    else: 
      self.image = pygame.Surface(size)
      self.image.fill((255, 0, 0))

    # physics vectors
    self.position = pygame.math.Vector2(pos)
    self.velocity = pygame.math.Vector2(0, 0)
    self.direction = pygame.Vector2(0, 1)

    self.state = None
    self.assets = None
    self.anim = None

    self.e_type = e_type

    # hitbox data
    self.rect = self.image.get_frect(topleft=pos)
    self.anim_offset = [0, 0]

  def update_physics(self, dt: float):
    self.position += self.velocity * dt

    # check collisions here probably
    self.rect.x = self.position.x
    self.rect.y = self.position.y
  
  def set_state(self, new_state:Enum) -> str:
    if self.state != new_state:

      # when states change we need to reset the game_frame on the animation object
      # which means we need to know the animation object of the new state and reset it before rendering
      # or we could do it the opposite way: set the current animation game_frame state to 0 before rendering

      if self.anim: self.anim.reset()
      self.state = new_state



  def render(self, camera_scroll:pygame.Vector2): 
    screen_pos = (
      self.rect.x - camera_scroll.x - self.anim_offset[0],
      self.rect.y - camera_scroll.y - self.anim_offset[1]
    )
    self.display_surface.blit(self.image, screen_pos)


class StaticEntity(PhysicsEntity): 
  def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], e_type:str):
    super().__init__(pos, size, e_type)
    pass

class DynamicEntity(PhysicsEntity): 
  def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], e_type:str):
    super().__init__(pos, size, e_type)
    pass







