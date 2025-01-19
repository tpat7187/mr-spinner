import pygame

from utils import load_image, BASE_PIXEL_SCALE

class Animation:
  def __init__(self, sprite_sheet_path, rows, columns, frame_duration = 5, hit_box_size=(32, 32), loop=False, st=0, ed=None): 
    self.sprite_sheet_path = sprite_sheet_path
    self.sheet_rows = rows 
    self.sheet_columns = columns
    self.loop = loop
    self.hitbox_width, self.hitbox_height = hit_box_size

    # start / end animation image
    self.st, self.ed = st, ed if ed is not None else columns

    self.sheet = load_image(self.sprite_sheet_path, BASE_PIXEL_SCALE)

    self.animation_frame_duration = frame_duration
    self.game_frame = st * self.animation_frame_duration
    
    # frame dim
    self.frame_width = self.sheet.get_width() // columns
    self.frame_height = self.sheet.get_height() // rows

    # Calculate offsets for centering the large animation around the hitbox
    self.x_offset = (self.frame_width - self.hitbox_width) // 2
    self.y_offset = (self.frame_height - self.hitbox_height) // 2
  
  def update(self): 
    self.game_frame = (self.game_frame + 1) % (self.animation_frame_duration * self.ed)
  
  def get_img(self): 
    current_frame = self.game_frame // self.animation_frame_duration
    frame_x = current_frame * self.frame_width
    frame_y = 0  # TODO: update when we have more complicated sprite sheets

    # Create full-size surface for the animation frame
    frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
    frame_surface.blit(self.sheet, (0, 0), (frame_x, frame_y, self.frame_width, self.frame_height))
    frame_surface.set_colorkey((0, 0, 0))
    
    return frame_surface, (self.x_offset, self.y_offset)