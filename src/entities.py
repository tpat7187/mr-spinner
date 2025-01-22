from __future__ import annotations
from typing import Tuple, Optional
from utils import load_image, tmAsset
import pygame

from animation import Animation
from enum import Enum, auto


class CollisionAxis(Enum): HORIZONTAL = auto(); VERTICAL = auto();
class EntityState(Enum): IDLE = auto(); MOVING = auto();

# require a size or a asset
class PhysicsEntity(pygame.sprite.Sprite): 
  def __init__(self, pos: Tuple[int, int], size: Optional[Tuple[int, int]]=None, asset:Optional[tmAsset]=None): 
    super().__init__()  
    self.display_surface = pygame.display.get_surface()
    
    # this is terrible
    if asset:
      self.asset = asset
      self.image = asset.asset
    else: 
      self.image = pygame.Surface(size)
      self.image.fill((255, 0, 0))
      self.asset = None

    # physics vectors
    self.velocity = pygame.math.Vector2(0, 0)
    self.direction = pygame.Vector2(0, 1)

    self.state = None
    self.assets = None
    self.anim = None

    # hitbox data
    self.rect = self.image.get_frect(topleft=pos)
    # interesting behaviour
    #self.rect = pygame.FRect(pos[0], pos[1], size[0], size[1])
    self.anim_offset = [0, 0]
  
  @property
  def get_pos(self): return (self.rect.x, self.rect.y)

  @property
  def get_asset_id(self): return self.asset.id

  def update_physics(self, dt: float):

    self.rect.x += self.velocity.x * dt
    self.collision(CollisionAxis.HORIZONTAL)

    self.rect.y += self.velocity.y * dt
    self.collision(CollisionAxis.VERTICAL)
  
  def collision(self, type:CollisionAxis): 
    for sp in self.groups()[0]:
      if sp.rect.colliderect(self.rect) and sp != self: 
        if type == CollisionAxis.HORIZONTAL:
          if self.velocity.x > 0: self.rect.right = sp.rect.left
          if self.velocity.x < 0: self.rect.left = sp.rect.right

        if type == CollisionAxis.VERTICAL:
          if self.velocity.y > 0: self.rect.bottom = sp.rect.top
          if self.velocity.y < 0: self.rect.top = sp.rect.bottom
  
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
  def __init__(self, pos: Tuple[int, int], size: Optional[Tuple[int, int]]=None, asset:Optional[tmAsset]=None): 
    super().__init__(pos, size, asset)
  

class DynamicEntity(PhysicsEntity): 
  def __init__(self, pos: Tuple[int, int], size: Optional[Tuple[int, int]]=None, surface:Optional[pygame.Surface]=None): 
    super().__init__(pos, size, surface)







