import os
import pygame.font

# 屏幕大小
SCREENSIZE = (800, 600)

# FPS
FPS = 90  # 或者 120

# 文件路径
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCE_PATH = os.path.join(CURRENT_PATH, 'resources')

# 图像路径
IMAGE_PATHS = {
    'hero': os.path.join(RESOURCE_PATH, 'images', 'hero.png'),
    'background': os.path.join(RESOURCE_PATH, 'images', 'background.png'),
    'gold': os.path.join(RESOURCE_PATH, 'images', 'gold.png'),
    'apple': os.path.join(RESOURCE_PATH, 'images', 'apple.png'),
}

# 打印路径以进行调试
print("RESOURCE_PATH:", RESOURCE_PATH)
print("Hero image path:", IMAGE_PATHS['hero'])
