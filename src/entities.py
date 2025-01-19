from __future__ import annotations
from typing import Tuple, Optional
from utils import load_image
import pygame

class Animation:
  def __init__(self, sprite_sheet_path, rows, columns, loop=False): 
    self.sprite_sheet_path = sprite_sheet_path
    self.sheet_rows = rows
    self.sheet_columns = columns
    self.loop = loop

    # load sprite sheet
    self.sheet = pygame.image.load(self.sprite_sheet_path).convert()
    self.animation_frame = 0
    self.game_frame = 0 
    self.animation_frame_duration = 5
    
    # frame dim
    self.frame_width = self.sheet.get_width() // columns
    self.frame_height = self.sheet.get_height() // rows
  
  def update(self): 
    self.game_frame = (self.game_frame + 1) % (self.animation_frame_duration * self.sheet_columns)
  
  # returns img surface
  def e(self): 
    current_frame = self.game_frame // self.animation_frame_duration
    frame_x = current_frame * self.frame_width
    frame_y = 0 # TODO: update when we have more complicated sprite sheets
    frame_surface = pygame.Surface((self.frame_width, self.frame_height))
    frame_surface.blit(self.sheet, (0, 0), (frame_x, frame_y, self.frame_width, self.frame_height))
    frame_surface.set_colorkey((0, 0, 0))
    return frame_surface

class PhysicsEntity(pygame.sprite.Sprite): 
  def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], e_type:str, asset_path:Optional[str]=None): 
    super().__init__()  
    
    # image data
    if asset_path is not None: 
      self.image = load_image(asset_path)
    else: 
      self.image = pygame.Surface(size)
      self.image.fill((255, 0, 0))
    self.pos = pygame.math.Vector2(pos)

    # hb data
    self.rect = self.image.get_rect(topleft=pos)
    self.e_type = e_type
  
  @property
  def x(self): return self.rect.x

  @property
  def y(self): return self.rect.y


class Player(PhysicsEntity): 
  def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
    super().__init__(pos, size, 'player') 
    self.speed = 2
    
  def update(self):

    # store old position, probably doesnt work
    self.pos.x = self.x
    self.pos.y = self.y
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]: self.rect.x += self.speed
    if keys[pygame.K_LEFT]: self.rect.x -= self.speed
    if keys[pygame.K_UP]: self.rect.y -= self.speed
    if keys[pygame.K_DOWN]: self.rect.y += self.speed
    
