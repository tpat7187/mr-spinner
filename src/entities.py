from __future__ import annotations
from typing import Tuple, Optional
from utils import load_image
import pygame

class Animation:
  def __init__(self, sprite_sheet_path, rows, columns, loop=False, st=0, ed=None): 
    self.sprite_sheet_path = sprite_sheet_path
    self.sheet_rows = rows
    self.sheet_columns = columns
    self.loop = loop

    # start / end animation image
    self.st, self.ed = st, ed if ed is not None else columns

    self.sheet = pygame.image.load(self.sprite_sheet_path).convert()


    self.animation_frame_duration = 5
    self.game_frame = st * self.animation_frame_duration
    
    # frame dim
    self.frame_width = self.sheet.get_width() // columns
    self.frame_height = self.sheet.get_height() // rows
  
  def update(self): 
    self.game_frame = (self.game_frame + 1) % (self.animation_frame_duration * self.ed)
  
  # returns img surface
  def get_img(self): 
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

    self.movement = [False, False]
    self.direction = [1, 0] # default direction is facing down
  
  @property
  def x(self): return self.rect.x

  @property
  def y(self): return self.rect.y


class Player(PhysicsEntity): 
  def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
    super().__init__(pos, size, 'player') 
    self.speed = 2
    self.state = None

    # spin stats
    self.spin_frame_count = 0
    self.spin_startup_frames = 10
    self.spin_frames = 30
    self.spin_cooldown_frames = 15

    # load assets [state, animation]
    self.animations = { 
      'idle_down' : Animation("../assets/player/Sword_1_Template_Idle_Down-Sheet.png", 1, 6),
      'idle_left' : Animation("../assets/player/Sword_1_Template_Idle_Left-Sheet.png", 1, 6),
      'idle_right' : Animation("../assets/player/Sword_1_Template_Idle_Right-Sheet.png", 1, 6),
      'idle_up' : Animation("../assets/player/Sword_1_Template_Idle_Up-Sheet.png", 1, 6),
      'run_right' : Animation("../assets/player/Sword_2_Template_Run_Right-Sheet.png", 1, 6),
      'run_left' : Animation("../assets/player/Sword_2_Template_Run_Left-Sheet.png", 1, 6),
      'run_up' : Animation("../assets/player/Sword_2_Template_Run_Up-Sheet.png", 1, 6),
      'run_down' : Animation("../assets/player/Sword_2_Template_Run_Down-Sheet.png", 1, 6),
      'spin_startup' : Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=0, ed=7),
      'spinning' : Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=8, ed=20),
      'spin_cooldown' : Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=20, ed=24),
    }

    self.set_state('idle_down')
  
  def set_state(self, new_state:str) -> str:
    if self.state != new_state:
      self.state = new_state
      # if the state changes the animation on the next frame needs to be reset
      self.animations[self.state].game_frame = 0
    
  def update(self):

    self.movement = [False, False]
    self.animations[self.state].update()
    self.image = self.animations[self.state].get_img()

    # store old position, probably doesnt work
    self.pos.x = self.x
    self.pos.y = self.y

    # states, should we abstract this or who cares
    # user controls should be in some dictionary or JSON dump somewhere
    # TODO: handle movement with a vec of bools
    moving = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]: 
      self.movement[0] = True
      self.rect.x += self.speed
      self.set_state('run_right')
      self.direction = (1, 0)
    if keys[pygame.K_a]: 
      self.movement[0] = True
      self.rect.x -= self.speed
      self.set_state('run_left')
      self.direction = (-1, 0)
    if keys[pygame.K_w]: 
      self.movement[1] = True
      self.rect.y -= self.speed
      self.set_state('run_up')
      self.direction = (0, -1)
    if keys[pygame.K_s]: 
      self.movement[1] = True
      self.rect.y += self.speed
      self.set_state('run_down')
      self.direction = (0, 1)
    
    if any(self.movement): moving = True 

    print(self.direction)
    
    
    if moving == False: 
      direction_to_anim = { 
        (-1, 0) : 'idle_left',
        (1, 0) : 'idle_right',
        (0, 1) : 'idle_down',
        (0, -1) : 'idle_up',
      }
      self.set_state(direction_to_anim[tuple(self.direction)])
  
  # tap spin button
  # starts spinning, one rotation of spin
  # checks if spin button is being held down
  # if spin button is held, continue to spin
  # else spin end
  def spinning_state_handler(self): 
    self.set_state('spin_startup')
    pass
    
    
