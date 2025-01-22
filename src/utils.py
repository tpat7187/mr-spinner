import pygame
from enum import Enum, auto
from dataclasses import dataclass



BASE_PATH = '../assets/'
BASE_PIXEL_SCALE = 2

MAP_TO_JSON = { 
  'dev' : BASE_PATH + 'maps/map_data.json'
}

class GameState(Enum): PLAYING = auto(); PAUSED = auto(); MAP_EDITOR = auto(); INIT = auto();
class AssetType(Enum): ON_GRID = auto(); OFF_GRID = auto();

@dataclass
class tmAsset:
  asset: pygame.Surface
  type: AssetType
  id: int

class Camera: 
  def __init__(self, width, height): 
    self.width, self.height = width, height
    self.scroll = pygame.math.Vector2(0,0)
  
  def center_camera_on_target(self, target): 
    self.scroll.x = target.rect.centerx - self.width // 2
    self.scroll.y = target.rect.centery - self.height // 2    


def load_image(path:str, pixel_scale=BASE_PIXEL_SCALE, scale:bool=True) -> pygame.Surface:
  scale = pixel_scale if scale else 1
  img = pygame.image.load(BASE_PATH + path).convert()
  return pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))