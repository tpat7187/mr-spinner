from __future__ import annotations
from typing import Tuple, Optional
import pygame

from entities import DynamicEntity, HitboxProc
from animation import Animation
from enum import Enum, auto

class PlayerState(Enum): IDLE = auto(); MOVING = auto(); SPIN_STARTUP = auto(); SPINNING = auto(); SPIN_COOLDOWN = auto();

# TODO: write this as an extention of HitboxProc
class SpinningHBProc(HitboxProc): 
  def __init__(self, owner, offset, lifetime): 
    super().__init__(owner, offset, lifetime)
    pass


  def update(self): 
    pass
    # this will rotate


class Player(DynamicEntity): 
  def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
    super().__init__(pos, size) 
    self.max_speed = 200
    self.state = PlayerState.IDLE
    self.idle_direction = self.direction

    # spin stats
    self.spinning = False
    self.spin_frame_count = 0
    self.spin_startup_frames = 100
    self.spin_frames = 20
    self.spin_cooldown_frames = 100

    self.active_hb.append(HitboxProc(self, (0, 0), (10,50), 100))

    # load assets [state, animation]
    self.assets = {
      PlayerState.IDLE: {
        (0, 1): Animation("../assets/player/Sword_1_Template_Idle_Down-Sheet.png", 1, 6, frame_duration=15),
        (-1, 0): Animation("../assets/player/Sword_1_Template_Idle_Left-Sheet.png", 1, 6, frame_duration=15),
        (1, 0): Animation("../assets/player/Sword_1_Template_Idle_Right-Sheet.png", 1, 6, frame_duration=15),
        (0, -1): Animation("../assets/player/Sword_1_Template_Idle_Up-Sheet.png", 1, 6, frame_duration=15),
      },
      PlayerState.MOVING: {
        (0, 1): Animation("../assets/player/Sword_2_Template_Run_Down-Sheet.png", 1, 6, frame_duration=15),
        (-1, 0): Animation("../assets/player/Sword_2_Template_Run_Left-Sheet.png", 1, 6, frame_duration=15),
        (1, 0): Animation("../assets/player/Sword_2_Template_Run_Right-Sheet.png", 1, 6, frame_duration=15),
        (0, -1): Animation("../assets/player/Sword_2_Template_Run_Up-Sheet.png", 1, 6, frame_duration=15),
      },
      PlayerState.SPIN_STARTUP: Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=1, ed=7, total_animation_time=self.spin_startup_frames, loop=False),
      PlayerState.SPINNING: Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=7, ed=18, total_animation_time=self.spin_frames, loop=False),
      PlayerState.SPIN_COOLDOWN: Animation("../assets/player/Sword_10_Template_Special_Attack_Down-Sheet.png", 1, 24, st=18, ed=24, total_animation_time=self.spin_cooldown_frames, loop=False),
    }

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
  
  def spin_handler(self): 
    self.spinning = True
    if self.spin_frame_count < self.spin_startup_frames: 
      self.set_state(PlayerState.SPIN_STARTUP)
    elif self.spin_startup_frames <= self.spin_frame_count < self.spin_startup_frames + self.spin_frames:
      self.set_state(PlayerState.SPINNING)
      if pygame.key.get_pressed()[pygame.K_y]: self.spin_frame_count = self.spin_startup_frames
    elif self.spin_startup_frames + self.spin_frames <= self.spin_frame_count < self.spin_startup_frames + self.spin_frames + self.spin_cooldown_frames:
      self.set_state(PlayerState.SPIN_COOLDOWN)
    else:
      self.spin_frame_count = 0
      self.spinning = False

    self.spin_frame_count += 1
  
  def create_hb(self): 
    self.active_hb.append(HitboxProc(self, (0, 0), (25,25), 100))

  def get_animation_direction(self, direction: pygame.Vector2) -> tuple:
    if abs(direction.x) > abs(direction.y): 
      return (1, 0) if direction.x > 0 else (-1, 0)
    else: return (0, 1) if direction.y > 0 else (0, -1)
  
  def update(self, dt:float):

    self.direction = self.get_input_direction()
    is_moving = self.direction.magnitude() > 0

    if pygame.key.get_pressed()[pygame.K_y] or self.spinning is True:
      self.spin_handler()
    
    if is_moving:
      self.velocity = self.direction * self.max_speed
      if not self.spinning:
        self.set_state(PlayerState.MOVING)
      self.idle_direction = self.direction
    else:
      self.velocity = pygame.Vector2(0, 0)
      if not self.spinning:
        self.set_state(PlayerState.IDLE)

    # new state first, anim once we know our new state
    for hb in self.active_hb: 
      hb.update()

    if not self.spinning:
      self.anim = self.assets[self.state][self.get_animation_direction(self.idle_direction)]
    else:
      self.anim = self.assets[self.state]

    self.anim.update()
    self.renderer.image, self.renderer.anim_offset = self.anim.get_img()
    self.update_physics(dt)
  