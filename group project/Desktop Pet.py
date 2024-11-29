import tkinter as tk
import pyautogui as pt
import random
import os
import time
import erniebot
import tkinter.ttk as ttk
from tkinter import scrolledtext
import json
from chat_window import ChatWindow
import winsound
import pygame.mixer

# 首先定义SOUND_EFFECTS
SOUND_EFFECTS = {
    "click": "./sounds/click.wav",
    "drag": "./sounds/drag.wav",
    "chat": "./sounds/chat.wav",
    "fall": "./sounds/fall.wav"
}

# 然后再初始化pygame和加载音效
try:
    pygame.mixer.init()
except Exception as e:
    print(f"无法初始化音频系统: {e}")
    # 创建一个备用的play_sound函数，只使用winsound
    def play_sound(action):
        try:
            if action == "click":
                winsound.Beep(1000, 50)
            elif action == "drag":
                winsound.Beep(8000, 30)
            elif action == "chat":
                winsound.Beep(1200, 100)
            elif action == "fall":
                winsound.Beep(500, 150)
        except:
            pass
else:
    # pygame初始化成功后的音效加载代码
    sounds = {}
    try:
        for action, path in SOUND_EFFECTS.items():
            if os.path.exists(path):
                sounds[action] = pygame.mixer.Sound(path)
                print(f"成功加载音效: {path}")
            else:
                print(f"找不到音效文件: {path}")
    except Exception as e:
        print(f"加载音效时出错: {e}")

    def play_sound(action):
        try:
            if action in sounds:
                print(f"正在播放音效: {action}")
                sounds[action].play()
            else:
                print(f"找不到音效: {action}，使用默认蜂鸣声")
                if action == "click":
                    winsound.Beep(1000, 50)
                elif action == "drag":
                    winsound.Beep(8000, 30)
                elif action == "chat":
                    winsound.Beep(1200, 100)
                elif action == "fall":
                    winsound.Beep(500, 150)
        except Exception as e:
            print(f"播放音效时出错: {e}")

# Get main screen resolution
WIDTH, HEIGHT = pt.size()

# 计算合适的窗口大小（比如屏幕宽度的15%）
scale_factor = 0.15  # 你可以调整这个值来改变大小比例
imgWidth = int(WIDTH * scale_factor)
imgHeight = int(imgWidth * 0.74)  # 保持原来的宽高比

# Height of your task bar.
taskbarHeight = 40
# The initial position of the window.
posX, posY = int(WIDTH/2-imgWidth/2), 0

# Create TK.
root = tk.Tk()
# Set window's size and position
root.geometry(f"{int(imgWidth)}x{int(imgHeight)}+{int(posX)}+{int(posY)}")
root.overrideredirect(1)
# 设置窗口完全透明
root.attributes('-alpha', 1.0)
root.attributes('-transparentcolor', 'white')  # 使用白色作为透明色
root.configure(bg='white')
root.wm_attributes('-topmost', 1)

# Read images. 修改帧数以匹配实际GIF并缩小图片
idleRight = [tk.PhotoImage(file='./Gif/IdleRight.gif',
                           format='gif -index %i' % (i)).subsample(2, 2) for i in range(3)]  # 缩小为原来的1/2
idleLeft = [tk.PhotoImage(file='./Gif/IdleLeft.gif',
                          format='gif -index %i' % (i)).subsample(2, 2) for i in range(3)]   # 缩小为原来的1/2
runRight = [tk.PhotoImage(file='./Gif/RunRight.gif',
                          format='gif -index %i' % (i)).subsample(2, 2) for i in range(3)]   # 缩小为原来的1/2
runLeft = [tk.PhotoImage(file='./Gif/RunLeft.gif',
                         format='gif -index %i' % (i)).subsample(2, 2) for i in range(3)]    # 缩小为原来的1/2
fall = [tk.PhotoImage(file='./Gif/Fall.gif',
                      format='gif -index %i' % (i)).subsample(2, 2) for i in range(2)]       # 缩小为原来的1/2
wait = [tk.PhotoImage(file='./Gif/Wait.gif',
                      format='gif -index %i' % (i)).subsample(2, 2) for i in range(3)]  # 假设wait动画有3帧

# Set status dictionary.
status = {0: fall,
          1: idleRight,
          2: idleLeft,
          3: runRight,
          4: runLeft,
          5: wait}  # 添加wait动画状态
# Initialize current status
status_num = 0

# Create label object
player = tk.Label(root, image=idleLeft[0],
                  bg='white', bd=0, cursor="hand2")  # 使用相同的特殊颜色值
player.pack(expand=True)

# Add mouse interaction variables
isDragging = False
dragStartX = 0
dragStartY = 0

# 在全局变量部分添加
last_interaction_time = time.time()
IDLE_TIMEOUT = 120  # 120秒无操作触发idle状态
chat_window_instance = None  # 用于跟踪聊天窗口实例

# 添加更新最后交互时间的函数
def update_interaction_time():
    global last_interaction_time
    last_interaction_time = time.time()

def checkMouseProximity():
    global status_num
    mouseX = root.winfo_pointerx()
    mouseY = root.winfo_pointery()
    petX = root.winfo_x() + imgWidth/2
    petY = root.winfo_y()
    
    current_time = time.time()
    
    # 只在前40秒内检查鼠标是否与宠物Y轴重合
    if current_time - last_interaction_time <= 40:
        # 检查鼠标Y轴是否与宠物重合
        # 创建一个高度范围，使检测更容易触发
        height_range = imgHeight/2  # 可以调整这个值来改变检测范围
        if abs(mouseY - (petY + imgHeight/2)) < height_range:  # 鼠标在宠物的垂直范围内
            status_num = 5  # 播放wait动画
            return
    
    # 如果不重合或超过40秒，则使用原来的逻辑
    if status_num != 0:  # 不在下落状态时
        if mouseX > petX:
            status_num = 1  # 面右边
        else:
            status_num = 2  # 面向左边
    
    root.after(100, checkMouseProximity)

def startDrag(event):
    print("开始拖动")
    global isDragging, dragStartX, dragStartY, posX, posY, status_num
    update_interaction_time()
    isDragging = True
    dragStartX = event.x_root - root.winfo_x()
    dragStartY = event.y_root - root.winfo_y()
    
    play_sound("drag")  # 添加拖拽音效
    
    # 记录点击的初始位置
    root._drag_start_x = event.x_root
    root._drag_start_y = event.y_root

def onDrag(event):
    print("正在拖动")
    global posX, posY
    update_interaction_time()
    if isDragging:
        new_x = event.x_root - dragStartX
        new_y = event.y_root - dragStartY
        
        # 限制在屏幕范围内
        new_x = max(0, min(new_x, WIDTH - imgWidth))
        new_y = max(0, min(new_y, HEIGHT - taskbarHeight - imgHeight))
        
        posX, posY = new_x, new_y
        root.geometry(f"{int(imgWidth)}x{int(imgHeight)}+{int(posX)}+{int(posY)}")

def stopDrag(event):
    global isDragging
    update_interaction_time()
    isDragging = False
    
    # 如果移动距离很小，认为是点击不是拖拽
    if hasattr(root, '_drag_start_x') and hasattr(root, '_drag_start_y'):
        if (abs(event.x_root - root._drag_start_x) < 5 and 
            abs(event.y_root - root._drag_start_y) < 5):
            onClick(event)
    else:
        # 将宠物移动到屏幕底部
        posY = HEIGHT - imgHeight - taskbarHeight  # 设置为屏幕底部
        root.geometry(f"{int(imgWidth)}x{int(imgHeight)}+{int(posX)}+{int(posY)}")

# 添加一个全局变量来跟踪是否正在运行移动动画
is_running = False

def onClick(event):
    global status_num, posX, is_running
    
    # 如果正在运行动画，直接返回
    if is_running:
        return
        
    play_sound("click")
    
    # 获取鼠标点击位置和宠物当前位置
    mouse_x = root.winfo_pointerx()
    pet_x = root.winfo_x() + imgWidth / 2
    
    # 点击宠物右侧时：
    if mouse_x > pet_x:
        status_num = 3  # 切换到向右跑的动画状态
        is_running = True  # 设置运行标志
        
        def run_right():
            global posX, status_num, is_running
            if posX + imgWidth < WIDTH:
                posX += 2
                root.geometry(f"{int(imgWidth)}x{int(imgHeight)}+{int(posX)}+{int(posY)}")
                root.after(10, run_right)
            else:
                status_num = 1  # 到达边界后切换回右侧待机状态
                is_running = False  # 清除运行标志
        run_right()
    
    # 点击宠物左侧时：
    else:
        status_num = 4  # 切换到向左跑的动画状态
        is_running = True  # 设置运行标志
        
        def run_left():
            global posX, status_num, is_running
            if posX > 0:
                posX -= 2
                root.geometry(f"{int(imgWidth)}x{int(imgHeight)}+{int(posX)}+{int(posY)}")
                root.after(10, run_left)
            else:
                status_num = 2  # 到达边界后切换回左侧待机状态
                is_running = False  # 清除运行标志
        run_left()
    
    update_interaction_time()

# 添加打开聊天窗口的函数
def open_chat(event):
    global chat_window_instance
    play_sound("chat")
    update_interaction_time()
    
    # 如果已经存在聊天窗口
    if chat_window_instance and chat_window_instance.window.winfo_exists():
        # 恢复最小化的窗口
        if chat_window_instance.window.state() == 'iconic':
            chat_window_instance.window.deiconify()
        
        # 将窗口提升到前台并获取焦点
        chat_window_instance.window.lift()
        chat_window_instance.window.focus_force()
        
        # 重新设置窗口位置到宠物正上方
        pet_x = root.winfo_x()
        pet_y = root.winfo_y()
        chat_width = 400
        chat_height = 500
        
        # 计算正上方位置
        chat_x = pet_x + (imgWidth - chat_width) // 2  # 居中对齐
        chat_y = pet_y - chat_height - 200  # 增加到200像素的向上偏移
        
        # 确保窗口不会超出屏幕边界
        if chat_x < 0:
            chat_x = 0
        elif chat_x + chat_width > WIDTH:
            chat_x = WIDTH - chat_width
        if chat_y < 0:
            chat_y = 0
        
        # 更新窗口位置
        chat_window_instance.window.geometry(f"+{int(chat_x)}+{int(chat_y)}")
        return
    
    # 如果不存在聊天窗口，创建新窗口
    chat_window_instance = ChatWindow(root)
    
    # 设置窗口位置到宠正上方
    pet_x = root.winfo_x()
    pet_y = root.winfo_y()
    chat_width = 400
    chat_height = 500
    
    # 计算正上方位置
    chat_x = pet_x + (imgWidth - chat_width) // 2  # 居中对齐
    chat_y = pet_y - chat_height - 200  # 增加到200像素的向上偏移
    
    # 确保窗口不会超出屏幕边界
    if chat_x < 0:
        chat_x = 0
    elif chat_x + chat_width > WIDTH:
        chat_x = WIDTH - chat_width
    if chat_y < 0:
        chat_y = 0
    
    # 设置聊天窗口位置
    chat_window_instance.window.geometry(f"+{int(chat_x)}+{int(chat_y)}")
    
    # 绑定窗口关闭事件
    chat_window_instance.window.protocol("WM_DELETE_WINDOW", 
        lambda: chat_window_instance.on_closing())

# 添加关闭口的处理函数
def close_chat_window(window):
    global chat_window_instance
    window.window.destroy()
    chat_window_instance = None

def bindEvents():
    # 移除之前的事件绑定
    player.unbind("<Button-1>")
    player.unbind("<B1-Motion>")
    player.unbind("<ButtonRelease-1>")
    
    # 重新绑定事件
    player.bind("<Button-1>", startDrag)
    player.bind("<B1-Motion>", onDrag)
    player.bind("<ButtonRelease-1>", stopDrag)
    
    # 添加右键事件绑定
    player.bind("<Button-3>", open_chat)

# Bind mouse events to the window
bindEvents()

def changeStatus():  # Change the status of the character.
    global status_num
    if not isDragging:
        # 增加移动状态的权重，使宠物更倾向于移动
        choices = [3, 4]  # 只在左右移动之间切换
        status_num = random.choice(choices)
    
    # 增加状态改变的间隔
    root.after(random.randint(8000, 12000), changeStatus)

def falling():  # Falling status. It should in front of other functions.
    global status_num, posX, posY
    # Change status if character is falling
    if root.winfo_y()+imgHeight < HEIGHT-taskbarHeight:
        status_num = 0
        posY += 1
        root.geometry(f"{int(imgWidth)}x{int(imgHeight)}+{int(posX)}+{int(posY)}")
    # On the ground
    elif root.winfo_y()+imgHeight >= HEIGHT-taskbarHeight and status_num == 0:
        status_num = 1
        play_sound("fall")  # 添加落地音效
    root.after(1, falling)

def moving():  # Moving the window based on character's status.
    global status_num, posX
    current_time = time.time()
    mouse_x = root.winfo_pointerx()
    pet_x = root.winfo_x() + imgWidth/2

    # 如果正在下落，不改变动画状态
    if status_num == 0:
        root.after(10, moving)
        return

    # 检查是否超过40秒无操作
    if current_time - last_interaction_time > 40:  # 改为40秒
        status_num = 5  # 切换到wait状态
    else:
        # 正常的移动逻辑
        if mouse_x > pet_x:
            status_num = 1
            if posX + imgWidth < WIDTH:
                posX += 0.5
                root.geometry(f"{int(imgWidth)}x{int(imgHeight)}+{int(posX)}+{int(posY)}")
        else:
            status_num = 2
            if posX > 0:
                posX -= 0.5
                root.geometry(f"{int(imgWidth)}x{int(imgHeight)}+{int(posX)}+{int(posY)}")
    
    root.after(10, moving)

def Anim(num, rate, character):
    if status_num == 0:  # 下落状态
        if num < len(fall) - 1:
            num += 1
        else:
            num = 0
        character.configure(image=fall[num])
        root.after(200, lambda: Anim(num, 200, character))
    else:  # 其他状态
        if num < len(status[status_num])-1:
            num += 1
        else:
            num = 0
        character.configure(image=status[status_num][num])
        
        # 根据不同状态使用不同的动画速度
        if status_num in [1, 2]:  # IdleRight 和 IdleLeft
            next_rate = 250
        elif status_num in [3, 4]:  # RunRight 和 RunLeft
            next_rate = 200
        elif status_num == 5:  # Wait状态
            next_rate = 300  # wait动画可以稍慢一些
        
        root.after(next_rate, lambda: Anim(num, next_rate, character))

if __name__ == '__main__':
    try:
        changeStatus()
        falling()
        moving()
        Anim(0, 200, player)
        checkMouseProximity()
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.mixer.quit()  # 清理pygame混音器
