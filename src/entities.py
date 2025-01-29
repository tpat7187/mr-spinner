from __future__ import annotations
from typing import Tuple, Optional
from utils import load_image, tmAsset, DEBUG
import pygame

from animation import Animation
from enum import Enum, auto
import math


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
  __slots__ = "entity"
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
  __slots__ = "image", "anim_offset", "display_surface"
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

# HITBOXES HAVE TO BE SURFACES SO WE CAN ROTATE THEM
# TODO: refactor more, take the spinny parts and put it in the SpinningHBProc in player
# make more general so we can use these for enemies n shit too
# I dont think for spinning the hitbox needs to rotate, I think it can just 'orbit' the player at an offset
class HitboxProc: 
  def __init__(self, owner: Entity, offset: Tuple[int, int], size: Tuple[int, int], lifetime: int):
    self.owner = owner
    self.offset, self.size, self.lifetime = offset, size, lifetime
    self.surf_orig = pygame.Surface(size, pygame.SRCALPHA)  
    self.surf_orig.fill((255, 0, 0, 128))  
    self.rect = self.surf_orig.get_rect()
    self.original_offset = pygame.math.Vector2(offset)
    
    # rotation shit
    self.rot = 0  
    self.rot_speed = 3
    self.radius = math.sqrt(offset[0]**2 + offset[1]**2)
    
    # Current surface that will be rotated
    self.current_surface = self.surf_orig
    
  def update(self):
    # update rot pos
    self.rot = (self.rot + self.rot_speed) % 360
    
    # spinning
    self.current_surface = pygame.transform.rotate(self.surf_orig, self.rot)
    self.rect = self.current_surface.get_rect()
    
    # update pos, center on owner
    self.rect.center = self.owner.rect.center


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

  @property
  def x(self): return self.rect.x

  @property
  def y(self): return self.rect.y

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

    self.active_hb = []

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

    # if you want to render the hitboxes
    if len(self.active_hb) > 0: 
      for hitbox in self.active_hb: 
        screen_pos = (
          hitbox.rect.x - camera_scroll[0] - self.anim_offset[0],
          hitbox.rect.y - camera_scroll[1] - self.anim_offset[1]
        )
        self.display_surface.blit(hitbox.current_surface, screen_pos)



