import pygame
import random
import numpy as np

class Hero(pygame.sprite.Sprite):
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.speed = 10  # Increase speed to adapt to larger image

    def move(self, screensize, direction):
        if direction == 'left':
            self.rect.left = max(self.rect.left - self.speed, 0)
        elif direction == 'right':
            self.rect.left = min(self.rect.left + self.speed, screensize[0] - self.rect.width)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Food(pygame.sprite.Sprite):
    def __init__(self, images, food_type, screensize):
        pygame.sprite.Sprite.__init__(self)
        self.type = food_type
        self.image = images[food_type]
        self.rect = self.image.get_rect()
        self.rect.left = random.randint(0, screensize[0] - self.rect.width)
        self.rect.top = random.randint(-100, -40)  # Random starting height
        self.speed = random.randint(2, 5)  # 增加下落速度范围
        self.score = 1 if food_type == 'gold' else 5
        self.screensize = screensize  # Save screen size

    def update(self):
        self.rect.top += self.speed
        if self.rect.top > self.screensize[1]:  # If food touches the ground
            self.kill()  # Directly remove sprite

def showEndGameInterface(screen, cfg, score, highest_score):
    font = pygame.font.Font(None, 36)
    screen.fill((240, 240, 240))  # 浅灰色背景
    
    game_over_text = font.render("Game Over!", True, (60, 60, 60))
    score_text = font.render(f'Your Score: {score}', True, (60, 60, 60))
    highest_score_text = font.render(f'Highest Score: {highest_score}', True, (60, 60, 60))
    
    game_over_rect = game_over_text.get_rect(center=(cfg.SCREENSIZE[0] // 2, cfg.SCREENSIZE[1] // 2 - 100))
    score_rect = score_text.get_rect(center=(cfg.SCREENSIZE[0] // 2, cfg.SCREENSIZE[1] // 2 - 30))
    highest_score_rect = highest_score_text.get_rect(center=(cfg.SCREENSIZE[0] // 2, cfg.SCREENSIZE[1] // 2 + 30))
    
    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(highest_score_text, highest_score_rect)
    
    # 添加作者名字
    author_font = pygame.font.Font(None, 24)
    author_text = author_font.render("PAN YANYING", True, (60, 60, 60))
    author_rect = author_text.get_rect(bottomright=(cfg.SCREENSIZE[0] - 10, cfg.SCREENSIZE[1] - 10))
    screen.blit(author_text, author_rect)
    
    pygame.display.flip()

def create_simple_sound(frequency, duration):
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    arr = np.array([4096 * np.sin(2.0 * np.pi * frequency * x / 44100) for x in range(0, 44100)]).astype(np.int16)
    sound = pygame.sndarray.make_sound(arr)
    sound.set_volume(0.5)
    return sound
