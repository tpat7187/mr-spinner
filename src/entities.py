from __future__ import annotations
from typing import Tuple, Optional
from utils import load_image
import pygame

from animation import Animation


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
    self.pos = pygame.math.Vector2(pos)

    # hb data
    self.rect = self.image.get_frect(topleft=pos)

    self.e_type = e_type

    self.movement = [False, False]
    self.direction = [1, 0] # default direction is facing down
  
  @property
  def x(self): return self.rect.x

  @property
  def y(self): return self.rect.y

  def render(self, camera_scroll:pygame.Vector2): 
    screen_pos = (
      self.rect.x - camera_scroll.x,
      self.rect.y - camera_scroll.y
    )
    self.display_surface.blit(self.image, screen_pos)
    

class Player(PhysicsEntity): 
  def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
    super().__init__(pos, size, 'player') 
    self.speed = 200
    self.state = None
    self.direction = pygame.Vector2()
    self.idle_direction = pygame.Vector2(0, 1)

    # spin stats
    self.spin_frame_count = 0
    self.spin_startup_frames = 10
    self.spin_frames = 30
    self.spin_cooldown_frames = 15

    # load assets [state, animation]
    self.animations = { 
      'idle_down' : Animation("../assets/player/Sword_1_Template_Idle_Down-Sheet.png", 1, 6, frame_duration=15),
      'idle_left' : Animation("../assets/player/Sword_1_Template_Idle_Left-Sheet.png", 1, 6, frame_duration=15),
      'idle_right' : Animation("../assets/player/Sword_1_Template_Idle_Right-Sheet.png", 1, 6, frame_duration=15),
      'idle_up' : Animation("../assets/player/Sword_1_Template_Idle_Up-Sheet.png", 1, 6, frame_duration=15),
      'run_right' : Animation("../assets/player/Sword_2_Template_Run_Right-Sheet.png", 1, 6, frame_duration=15),
      'run_left' : Animation("../assets/player/Sword_2_Template_Run_Left-Sheet.png", 1, 6, frame_duration=15),
      'run_up' : Animation("../assets/player/Sword_2_Template_Run_Up-Sheet.png", 1, 6, frame_duration=15),
      'run_down' : Animation("../assets/player/Sword_2_Template_Run_Down-Sheet.png", 1, 6, frame_duration=15),
      'spin_startup' : Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=0, ed=7, frame_duration=self.spin_startup_frames),
      'spinning' : Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=8, ed=20, frame_duration=self.spin_frames),
      'spin_cooldown' : Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=20, ed=24, frame_duration=self.spin_cooldown_frames),
    }

    self.set_state('idle_down')
  
  def set_state(self, new_state:str) -> str:
    if self.state != new_state:
      self.state = new_state
      self.animations[self.state].game_frame = 0
  
  def get_input_direction(self) -> pygame.Vector2:
    direction = pygame.Vector2(0, 0)
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_d]: direction.x += 1
    if keys[pygame.K_a]: direction.x -= 1
    if keys[pygame.K_w]: direction.y -= 1
    if keys[pygame.K_s]: direction.y += 1
    
    if direction.magnitude() > 0:
      return direction.normalize()
    return direction

  # closest cardinal direction
  def get_animation_direction(self, direction: pygame.Vector2) -> tuple:
    if abs(direction.x) > abs(direction.y):
      return (1, 0) if direction.x > 0 else (-1, 0)
    else:
      return (0, 1) if direction.y > 0 else (0, -1)

  def update(self, dt:float):
    self.animations[self.state].update()
    self.image, self.anim_offset = self.animations[self.state].get_img()

    # store old position
    self.pos.x = self.rect.x
    self.pos.y = self.rect.y

    # get input and update position
    self.direction = self.get_input_direction()
    is_moving = self.direction.magnitude() > 0
    
    if is_moving:
      self.rect.x += self.direction.x * self.speed * dt
      self.rect.y += self.direction.y * self.speed * dt
      
      # get the closest cardinal direction for animation
      anim_direction = self.get_animation_direction(self.direction)
      
      direction_to_anim = { 
        (-1, 0) : 'run_left',
        (1, 0) : 'run_right',
        (0, 1) : 'run_down',
        (0, -1) : 'run_up',
      }
      self.set_state(direction_to_anim[anim_direction])
      self.idle_direction = pygame.Vector2(anim_direction)

    else:
      direction_to_anim = { 
        (-1, 0) : 'idle_left',
        (1, 0) : 'idle_right',
        (0, 1) : 'idle_down',
        (0, -1) : 'idle_up',
      }
      idle_direction_tuple = (int(self.idle_direction.x), int(self.idle_direction.y))
      self.set_state(direction_to_anim[idle_direction_tuple])
  
  def render(self, camera_scroll): 
    screen_pos = (
      self.rect.x - camera_scroll.x - self.anim_offset[0],
      self.rect.y - camera_scroll.y - self.anim_offset[1]
    )
    self.display_surface.blit(self.image, screen_pos)
    
    
