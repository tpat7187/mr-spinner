import pygame
import os


BASE_PATH = '../assets/'

class Camera: 
  def __init__(self, width, height): 
    self.width, self.height = width, height
    self.scroll = pygame.math.Vector2(0,0)
  
  def center_camera_on_target(self, target): 
    self.scroll.x = target.rect.centerx - self.width // 2
    self.scroll.y = target.rect.centery - self.height // 2    


def load_image(path:str) -> pygame.Surface:
  img = pygame.image.load(BASE_PATH + path).convert()
  return img