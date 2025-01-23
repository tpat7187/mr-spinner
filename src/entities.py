from __future__ import annotations
from typing import Tuple, Optional
from utils import load_image, tmAsset
import pygame

from animation import Animation
from enum import Enum, auto


class CollisionAxis(Enum): HORIZONTAL = auto(); VERTICAL = auto();
class EntityState(Enum): IDLE = auto(); MOVING = auto();

'''
Entity: Base container for asset

StaticEntity: Has Rendering, Collision 

DynamicEntity: Has Movement, Rendering, Collision

RenderProc: Handle Drawing to Screen

PhysicsProc: Handles Collisions
; we can write this in such a way that we can use it for hitbox/damage related stuff
'''

class CollisionProc:
  def __init__(self, entity: 'DynamicEntity'):
    self.entity = entity
  
  def check_collision(self, entity_groups, axis: CollisionAxis):
    for group in entity_groups:
      for sprite in group:
        if sprite.rect.colliderect(self.entity.rect) and sprite != self.entity:
          self.handle_collision(sprite, axis)
  
  def handle_collision(self, other, axis: CollisionAxis):
    if axis == CollisionAxis.HORIZONTAL:
      if self.entity.velocity.x > 0: self.entity.rect.right = other.rect.left
      if self.entity.velocity.x < 0: self.entity.rect.left = other.rect.right
    elif axis == CollisionAxis.VERTICAL:
      if self.entity.velocity.y > 0: self.entity.rect.bottom = other.rect.top
      if self.entity.velocity.y < 0: self.entity.rect.top = other.rect.bottom

class RenderProc:
  def __init__(self, image: pygame.Surface, anim_offset: Tuple[int, int] = (0, 0)):
    self.image = image
    self.anim_offset = anim_offset
    self.display_surface = pygame.display.get_surface()
  
  def render(self, position: Tuple[float, float], camera_scroll: pygame.Vector2):
    screen_pos = (
      position[0] - camera_scroll.x - self.anim_offset[0],
      position[1] - camera_scroll.y - self.anim_offset[1]
    )
    self.display_surface.blit(self.image, screen_pos)


class Entity(pygame.sprite.Sprite): 
  def __init__(self, pos: Tuple[int, int], size: Optional[Tuple[int, int]]=None, asset:Optional[tmAsset]=None): 
    super().__init__()  
    self.display_surface = pygame.display.get_surface()
    self.asset = asset 
    self.image = asset.asset if asset else self._create_default_surface(size)

    self.rect = self.image.get_frect(topleft=pos)

  @property
  def get_pos(self): return (self.rect.x, self.rect.y)

  @property
  def get_asset_id(self): return self.asset.id

  def _create_default_surface(self, size: Tuple[int, int]) -> pygame.Surface:
    surface = pygame.Surface(size)
    surface.fill((255, 0, 0))
    return surface

  def set_state(self, new_state:Enum) -> str:
    if self.state != new_state:
      if self.anim: self.anim.reset()
      self.state = new_state

class StaticEntity(Entity):
  def __init__(self, pos: Tuple[int, int], size: Optional[Tuple[int, int]] = None, asset: Optional[tmAsset] = None):
    super().__init__(pos, size, asset)
    self.state = None

    self.assets = None
    self.anim = None
    self.anim_offset = [0, 0]

    self.phys = CollisionProc(self)
    self.renderer = RenderProc(self.image, self.anim_offset)

  def render(self, camera_scroll:pygame.Vector2): 
    self.renderer.render(self.get_pos, camera_scroll)

class DynamicEntity(Entity):
  def __init__(self, pos: Tuple[int, int], size: Optional[Tuple[int, int]] = None, asset: Optional[tmAsset] = None):
    super().__init__(pos, size, asset)
    self.velocity = pygame.math.Vector2(0, 0)
    self.direction = pygame.math.Vector2(0, 1)
    self.state = None

    self.assets = None
    self.anim = None
    self.anim_offset = [0, 0]

    # passing in reference to velocity for now
    self.phys = CollisionProc(self)
    self.renderer = RenderProc(self.image, self.anim_offset)
  
  def update_physics(self, dt: float):
    self.rect.x += self.velocity.x * dt
    self.phys.check_collision(self.groups(), CollisionAxis.HORIZONTAL)
    
    self.rect.y += self.velocity.y * dt
    self.phys.check_collision(self.groups(), CollisionAxis.VERTICAL)

  def render(self, camera_scroll:pygame.Vector2): 
    self.renderer.render(self.get_pos, camera_scroll)


