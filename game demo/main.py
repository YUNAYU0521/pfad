import os
import cfg
import sys
import pygame
import random
from modules import *

# 修改调试信息
print("Current working directory:", os.getcwd())
print("RESOURCE_PATH:", cfg.RESOURCE_PATH)
print("Hero image path:", cfg.IMAGE_PATHS['hero'])

'''Game Initialization'''
def initGame():
    # 初始化pygame，设置显示窗口
    pygame.init()
    screen = pygame.display.set_mode(cfg.SCREENSIZE)
    pygame.display.set_caption('Catch Coins Game')
    # 加载必要的游戏资源
    game_images = {}
    for key, value in cfg.IMAGE_PATHS.items():
        try:
            img = pygame.image.load(value)
            if key == 'hero':
                img = pygame.transform.scale(img, (150, 150))  # 增加英雄大小到150x150
            elif key in ['gold', 'apple']:
                img = pygame.transform.scale(img, (50, 50))  # 保持食物大小不变
            elif key == 'background':
                img = pygame.transform.scale(img, cfg.SCREENSIZE)  # 将背景图片缩放至屏幕大小
            game_images[key] = img
            print(f"Successfully loaded image: {key}")
        except pygame.error as e:
            print(f"Error loading image {key}: {e}")
            # 如果无法加载图像，使用彩色矩形代替
            if key == 'background':
                game_images[key] = pygame.Surface(cfg.SCREENSIZE)
                game_images[key].fill((100, 100, 255))  # Blue background
            elif key == 'hero':
                game_images[key] = pygame.Surface((150, 150))
                game_images[key].fill((255, 0, 0))  # Red square as hero
            else:
                game_images[key] = pygame.Surface((50, 50))  # Modify food size to 50x50
                game_images[key].fill((0, 255, 0))  # Green square as food
    return screen, game_images

def showStartScreen(screen, font):
    screen.fill((255, 255, 255))
    start_text = font.render("Press any key to start", True, (0, 0, 0))
    start_rect = start_text.get_rect(center=(cfg.SCREENSIZE[0] // 2, cfg.SCREENSIZE[1] // 2))
    screen.blit(start_text, start_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

def create_button(x, y, width, height, text, font, color, hover_color):
    button = pygame.Rect(x, y, width, height)
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=button.center)
    return button, text_surf, text_rect, color, hover_color

def draw_rounded_rect(surface, rect, color, corner_radius):
    """ Draw a rounded rectangle """
    pygame.draw.rect(surface, color, (rect.x, rect.y + corner_radius, rect.width, rect.height - 2*corner_radius))
    pygame.draw.rect(surface, color, (rect.x + corner_radius, rect.y, rect.width - 2*corner_radius, rect.height))
    pygame.draw.circle(surface, color, (rect.x + corner_radius, rect.y + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.x + rect.width - corner_radius, rect.y + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.x + corner_radius, rect.y + rect.height - corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.x + rect.width - corner_radius, rect.y + rect.height - corner_radius), corner_radius)

def showPauseScreen(screen, font):
    pause_surface = pygame.Surface(cfg.SCREENSIZE, pygame.SRCALPHA)
    pause_surface.fill((255, 255, 255, 200))  # 半透明白色背景
    screen.blit(pause_surface, (0, 0))
    
    pause_text = font.render("Game Paused", True, (60, 60, 60))
    resume_text = font.render("Click anywhere to Resume", True, (60, 60, 60))
    
    pause_rect = pause_text.get_rect(center=(cfg.SCREENSIZE[0] // 2, cfg.SCREENSIZE[1] // 2 - 30))
    resume_rect = resume_text.get_rect(center=(cfg.SCREENSIZE[0] // 2, cfg.SCREENSIZE[1] // 2 + 30))
    
    screen.blit(pause_text, pause_rect)
    screen.blit(resume_text, resume_rect)
    pygame.display.flip()

'''Main Function'''
def main():
    screen, game_images = initGame()
    font = pygame.font.Font(None, 40)  # Use system default font
    showStartScreen(screen, font)
    
    # Adjust hero's initial position
    hero_x = (cfg.SCREENSIZE[0] - 150) // 2  # 150 is hero's new width
    hero_y = cfg.SCREENSIZE[1] - 170  # Adjust bottom space for larger hero
    hero = Hero(game_images['hero'], position=(hero_x, hero_y))
    food_sprites_group = pygame.sprite.Group()
    score = 0
    highest_score = 0
    
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    running = True
    
    pause_button, pause_text, pause_text_rect, button_color, button_hover_color = create_button(
        cfg.SCREENSIZE[0] - 110, 10, 100, 40, "Pause", font, (200, 200, 200, 150), (150, 150, 150, 200)
    )
    
    paused = False
    pause_start_time = 0
    
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()  # 直接退出游戏，不显示结算界面
            if event.type == pygame.MOUSEBUTTONDOWN:
                if paused:
                    paused = False
                    start_time += current_time - pause_start_time
                elif pause_button.collidepoint(event.pos):
                    paused = True
                    pause_start_time = current_time
                    showPauseScreen(screen, font)
        
        if not paused:
            # 直接绘制背景图片，不再填充灰色背景
            screen.blit(game_images['background'], (0, 0))
            
            # 绘制圆角矩形暂停按钮
            mouse_pos = pygame.mouse.get_pos()
            if pause_button.collidepoint(mouse_pos):
                draw_rounded_rect(screen, pause_button, button_hover_color, 10)
            else:
                draw_rounded_rect(screen, pause_button, button_color, 10)
            screen.blit(pause_text, pause_text_rect)
            
            elapsed_time = current_time - start_time
            countdown_text = f'Time: {30 - elapsed_time // 1000}'
            countdown_text = font.render(countdown_text, True, (0, 0, 0))
            countdown_rect = countdown_text.get_rect()
            countdown_rect.topright = [cfg.SCREENSIZE[0]-120, 5]
            screen.blit(countdown_text, countdown_rect)
            
            # 获取鼠标位置
            mouse_x, _ = pygame.mouse.get_pos()
            
            # 移动英雄到鼠标的x坐标位置
            hero.rect.centerx = mouse_x
            hero.rect.centerx = max(hero.rect.width // 2, min(hero.rect.centerx, cfg.SCREENSIZE[0] - hero.rect.width // 2))
            
            # Randomly generate food
            if random.randint(1, 250) <= 3:  # 将生成概率调整为1.2% (3/250)
                food_count = random.randint(1, 2)  # 随机生成1到2个食物
                for _ in range(food_count):
                    if random.random() < 0.8:  # 80% chance to generate gold
                        food_type = 'gold'
                    else:  # 20% chance to generate apple
                        food_type = 'apple'
                    food = Food(game_images, food_type, cfg.SCREENSIZE)
                    food_sprites_group.add(food)
            
            # Remove food that's out of screen
            for food in food_sprites_group:
                if food.rect.top > cfg.SCREENSIZE[1]:
                    food.kill()
            
            # Update food
            food_sprites_group.update()
            
            # Collision detection
            for food in pygame.sprite.spritecollide(hero, food_sprites_group, True):
                score += food.score
                if score > highest_score:
                    highest_score = score
            
            hero.draw(screen)
            food_sprites_group.draw(screen)
            
            score_text = f'Score: {score}, Highest: {highest_score}'
            score_text = font.render(score_text, True, (0, 0, 0))
            score_rect = score_text.get_rect()
            score_rect.topleft = [5, 5]
            screen.blit(score_text, score_rect)
            
            # 添加作者名字
            author_font = pygame.font.Font(None, 24)
            author_text = author_font.render("PAN YANYING", True, (60, 60, 60))
            author_rect = author_text.get_rect(bottomright=(cfg.SCREENSIZE[0] - 10, cfg.SCREENSIZE[1] - 10))
            screen.blit(author_text, author_rect)
            
            if elapsed_time >= 30000:
                running = False
            
            pygame.display.flip()
        
        clock.tick(cfg.FPS)
    
    # 游戏正常结束时显示结算界面
    showEndGameInterface(screen, cfg, score, highest_score)
    
    # 等待15秒
    pygame.time.wait(15000)
    pygame.quit()
    sys.exit()

'''run'''
if __name__ == '__main__':
    main()
