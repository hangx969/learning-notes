---
title: Python 游戏开发
tags:
  - python/game
  - python/pygame
  - python/tkinter
aliases:
  - Python游戏开发
  - pygame游戏项目
date: 2026-04-16
---

# Python 游戏开发

本笔记包含三个使用 ==pygame== 开发的2D游戏项目:赛车游戏、打飞船游戏和俄罗斯方块游戏。

相关笔记: [[python-GUI-tkinter]]

---

## 赛车2D游戏开发

~~~python
import io,sys
#导入 Python 的两个内置模块
#io：负责"输入输出"（input/output），也就是读写文件、控制台输出等。
#sys：访问与 Python 解释器相关的系统参数，比如输入输出流（stdin、stdout）、命令行参数等。
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#sys.stdout这是 Python 的"标准输出流"，就是你平时用 print() 输出的目标。输出的结果会在控制台显示。
#但 sys.stdout 其实也可以变成一个"字节流"，这就是 sys.stdout.buffer，它处理的是数据的二进制格式，不涉及直接的字符编码。
#io.TextIOWrapper 就是将这个"字节流"转换回"文本流"，而且让它知道要使用 UTF-8 编码，这样就能正确处理中文字符了。

import tkinter as tk
#tkinter 是 Python 标准库中的一个图形用户界面（GUI）库，用于开发桌面应用程序。它提供了丰富的控件（如按钮、文本框、标签等）来构建用户界面。
#tk 是对 tkinter 模块的简写，方便在代码中调用。使用 tk，你可以创建窗口、按钮、文本框等，来设计桌面应用的界面。
from tkinter import messagebox
#messagebox 是 tkinter 库中的一个模块，用于弹出消息框（对话框），用来提示用户信息或错误。你可以用它来显示信息、警告、错误提示等。
import pygame
#pygame 是一个用于开发 2D 游戏和多媒体应用的第三方库，提供了处理图形、声音、事件和其他游戏相关功能的工具。
#你可以用 pygame 来处理图像、音频、用户输入（键盘、鼠标）、碰撞检测等，常用于游戏开发。你可以使用 pygame 来加载图片、播放音效、处理动画等。
import random
#random 是 Python 的标准库模块，提供了生成随机数的功能。它可以生成随机数、随机选择列表中的元素等。
# 它在游戏中常用于生成随机事件，比如随机生成敌人位置、掉落物品、随机数决定的游戏元素。
import os
#os 是 Python 的标准库模块，用于与操作系统进行交互。它提供了文件和目录操作、环境变量管理、进程管理等功能。
#使用 os，你可以创建、删除、移动文件或文件夹，获取操作系统的信息等。

class RacingGame:
#定义一个类，用来设置游戏基本属性和参数的，类似于是游戏全部功能的集合

    def __init__(self):
    #定义一个init构造函数，在面向对象编程中，__init__ 是类的构造函数，负责在创建类的实例时对对象进行初始化操作
    #这个方法会在你创建类实例时自动调用，目的是为新创建的对象设置一些初始值，通常用于设置对象的属性和初始化一些必要的资源。

        pygame.init()
        #初始化 pygame 库，为游戏设置一些环境。pygame 是一个用于开发2D游戏的库，包括图像、声音、事件、游戏循环等功能。
        pygame.mixer.init()
        #初始化 pygame库下的音频模块（mixer），用于处理游戏中的音效和背景音乐。

        #设置游戏窗口的大小，宽度 800 像素，高度 600 像素。
        self.screen_width, self.screen_height = 800, 600
        #通过pygame库创建游戏窗口，大小为 800x600 像素。
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        #设置窗口的标题为 "竞速赛车游戏"。
        pygame.display.set_caption("竞速赛车游戏")
        #创建一个时钟对象，用于控制游戏的帧率。通过控制帧率，可以让游戏运行得更加流畅。时钟也帮助控制游戏循环的速度。
        self.clock = pygame.time.Clock()
        #游戏中的每一帧都是一幅静止的图像。当这些帧以足够快的速度连续播放时，人眼就会产生画面在连续运动的错觉
        #帧率越高，意味着在单位时间内显示的画面数量越多，画面的连贯性就越好，给人的视觉感受就越流畅。

        #对游戏属性进行初始化
        self.player_speed = 5 #  设置玩家汽车的移动速度，5像素/帧
        self.enemy_base_speed = 3  #  设置敌人汽车的初始速度

        #设置游戏的运行状态为 False，表示游戏没有开始。
        self.running = False
        #初始距离为0
        self.distance = 0

        # 指定图片路径
        self.player_car_image = "D:/player_car.png"  # 玩家汽车图片
        self.enemy_car_image = "D:/enemy_car.png"    # 机器自带的赛车图片
        self.background_music = "D:/background_music.ogg"  # 背景音乐
        self.collision_sound = "D:/collision_sound.wav"    # 碰撞音效

        # 加载图像
        self.player_car = pygame.image.load(self.player_car_image) #  加载玩家车辆图像
        self.player_car = pygame.transform.scale(self.player_car, (50, 100)) #将玩家车辆图像缩放到50x100像素
        self.enemy_car = pygame.image.load(self.enemy_car_image) #加载敌人车辆图像
        self.enemy_car = pygame.transform.scale(self.enemy_car, (50, 100)) #将敌人车辆图像缩放到50x100像素

        # 设置玩家初始位置
        self.player_x = self.screen_width // 2 - 25  #设置玩家车辆的水平位置位于屏幕中心
        self.player_y = self.screen_height - 120 #玩家汽车的垂直位置是距离屏幕底部 120 像素
        self.road_y = 0 #初始化背景滚动位置为0，表示背景尚未开始滚动

        self.enemies = [] #  初始化敌人车辆列表为空
        self.spawn_multiple_enemies() #调用函数生成多个敌人车辆

        # 加载背景音乐
        self.load_background_music()

        # 加载碰撞音效
        self.load_collision_sound()

    def load_background_music(self):
        """加载背景音乐"""
        if os.path.exists(self.background_music):
            try:
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.play(-1)  # 循环播放背景音乐，-1表示无限循环
            except pygame.error as e:
                print("背景音乐加载失败:", e)
        else:
            print("背景音乐文件未找到:", self.background_music)

    def load_collision_sound(self):
        """加载碰撞音效"""
        if os.path.exists(self.collision_sound):
            try:
                self.collision_sound_effect = pygame.mixer.Sound(self.collision_sound)
            except pygame.error as e:
                print("碰撞音效加载失败:", e)
                self.collision_sound_effect = None
        else:
            print("碰撞音效文件未找到:", self.collision_sound)
            self.collision_sound_effect = None

    def play_collision_sound(self):
        """播放碰撞音效"""
        if self.collision_sound_effect:
            self.collision_sound_effect.play()

    def spawn_multiple_enemies(self, count=5):
        """生成多个敌人汽车位置"""
        self.enemies = []
        for _ in range(count):
            self.spawn_enemy()

    def spawn_enemy(self):
        """随机生成一个敌人汽车位置和速度"""
        enemy_x = random.randint(200, self.screen_width - 250)
        enemy_y = random.randint(-600, -100)
        enemy_speed = self.enemy_base_speed + random.random() * 2
        self.enemies.append([enemy_x, enemy_y, enemy_speed])

    def run_game(self):
        """游戏主循环"""
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

            # 玩家逻辑，玩家左右和加速减速控制
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.player_x > 200:
                self.player_x -= 8
            if keys[pygame.K_RIGHT] and self.player_x < self.screen_width - 250:
                self.player_x += 8
            if keys[pygame.K_UP]:
                self.player_speed += 0.1
            if keys[pygame.K_DOWN] and self.player_speed > 1:
                self.player_speed -= 0.1

            # 背景滚动控制
            self.road_y += self.player_speed / 2
            if self.road_y >= self.screen_height:
                self.road_y = 0

            # 移动敌人车辆
            self.move_enemies()

            # 计算赛程距离和动态加速
            self.distance += self.player_speed / 10
            if int(self.distance) % 100 == 0:
                self.enemy_base_speed += 0.1

            # 检查碰撞
            if self.is_collision():
                self.play_collision_sound()
                pygame.mixer.music.stop()
                self.game_over()

            # 绘制背景
            self.draw_background()
            # 显示玩家车、敌人车、当前赛程距离
            self.screen.blit(self.player_car, (self.player_x, self.player_y))
            for enemy_x, enemy_y, _ in self.enemies:
                self.screen.blit(self.enemy_car, (enemy_x, enemy_y))
            # 显示赛程距离
            font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 28)
            distance_text = font.render(f"赛程: {int(self.distance)} 米", True, (255, 255, 255))
            self.screen.blit(distance_text, (10, 10))
            pygame.display.flip()
            self.clock.tick(30)

    def draw_background(self):
        """绘制赛道背景"""
        self.screen.fill((0, 128, 0))
        pygame.draw.rect(self.screen, (50, 50, 50), (200, 0, self.screen_width - 400, self.screen_height))
        for i in range(0, self.screen_height, 60):
            pygame.draw.line(self.screen, (255, 255, 255),
                             (self.screen_width // 2 - 5, i + self.road_y),
                             (self.screen_width // 2 + 5, i + 40 + self.road_y), 5)

    def move_enemies(self):
        """控制敌人车辆在屏幕上移动并清理屏幕外的敌人"""
        for enemy in self.enemies:
            enemy[1] += enemy[2]
        self.enemies = [enemy for enemy in self.enemies if enemy[1] < self.screen_height]
        if len(self.enemies) < 5:
            self.spawn_enemy()

    def is_collision(self):
        """检查玩家和敌人之间的碰撞(AABB碰撞检测)"""
        for enemy_x, enemy_y, _ in self.enemies:
            if (self.player_x < enemy_x + 50 and
                self.player_x + 50 > enemy_x and
                self.player_y < enemy_y + 100 and
                self.player_y + 100 > enemy_y):
                return True
        return False

    def game_over(self):
        """处理游戏结束逻辑"""
        choice = messagebox.askyesno("游戏结束", f"你已行驶 {int(self.distance)} 米！\n是否重新开始游戏？")
        if choice:
            self.reset_game()
            self.run_game()
        else:
            pygame.quit()
            sys.exit()

    def reset_game(self):
        """重置游戏状态"""
        self.player_speed = 5
        self.enemy_base_speed = 3
        self.distance = 0
        self.road_y = 0
        self.player_x = self.screen_width // 2 - 25
        self.enemies.clear()
        self.spawn_multiple_enemies()

# 使用 tkinter 创建主界面
class RacingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("竞速赛车游戏")
        self.root.geometry("900x700")

        button_font = ("Microsoft YaHei", 18)

        # 启动游戏按钮
        self.start_button = tk.Button(self.root, text="开始游戏", command=self.start_game,font=button_font)
        self.start_button.pack(pady=20)

        # 退出按钮
        self.exit_button = tk.Button(self.root, text="退出", command=self.root.quit,font=button_font)
        self.exit_button.pack(pady=10)

    def start_game(self):
        self.root.withdraw()
        game = RacingGame()
        game.run_game()
        self.root.deiconify()

# 创建主窗口并启动应用
if __name__ == "__main__":
    root = tk.Tk()
    app = RacingApp(root)
    root.mainloop()
~~~

---

## 打飞船2D游戏开发

> [!info] 游戏功能
> - 玩家控制飞船左右移动,按空格键射击
> - 按 ==W== 键切换武器(普通枪、散弹枪、火箭筒)
> - 按 ==P== 键暂停/继续游戏
> - 按 ==R== 键在游戏结束后重新开始
> - 碰撞敌人3次后游戏结束

~~~python
import sys,io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pygame
import random

# 初始化 Pygame
pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("射击美国飞船")

# 颜色定义
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)

# 加载中文字体
try:
    font_path = "C:\Windows\Fonts\STXIHEI.TTF"
    font = pygame.font.Font(font_path, 20)
except FileNotFoundError:
    font = pygame.font.SysFont(None, 20)

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, blue, [(15, 0), (30, 50), (0, 50)])
        self.rect = self.image.get_rect(center=(width // 2, height - 50))
        self.lives = 3
        self.hit_count = 0
        self.is_game_over = False
        self.weapon = RegularGun()
        self.fire_message = "按下空格键射击"
        self.switch_message = "按下 W 切换武器"

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.x += 5

    def switch_weapon(self):
        if isinstance(self.weapon, RegularGun):
            self.weapon = Shotgun()
            self.switch_message = "切换为散弹枪"
        elif isinstance(self.weapon, Shotgun):
            self.weapon = RocketLauncher()
            self.switch_message = "切换为火箭筒"
        else:
            self.weapon = RegularGun()
            self.switch_message = "切换为普通枪"

    def fire(self):
        bullets = self.weapon.fire(self.rect.centerx, self.rect.top)
        if isinstance(bullets, list):
            for bullet in bullets:
                all_sprites.add(bullet)
                bullets_group.add(bullet)
        elif bullets is not None:
            all_sprites.add(bullets)
            bullets_group.add(bullets)

    def respawn(self):
        self.rect.center = (width // 2, height - 50)
        self.hit_count += 1
        if self.hit_count >= 3:
            self.is_game_over = True

    def reset_game(self):
        self.hit_count = 0
        self.lives = 3
        self.is_game_over = False
        self.rect.center = (width // 2, height - 50)
        bullets_group.empty()
        enemies_group.empty()
        all_sprites.add(self)

# 武器基类
class Weapon:
    def fire(self, x, y):
        raise NotImplementedError("This method should be overridden in subclasses.")

# 普通枪类
class RegularGun(Weapon):
    def fire(self, x, y):
        return Bullet(x, y)

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(red)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()

# 散弹枪类
class Shotgun(Weapon):
    def fire(self, x, y):
        bullets = []
        for offset in [-10, 0, 10]:
            bullet = Bullet(x + offset, y)
            bullets.append(bullet)
        return bullets

# 火箭筒类
class RocketLauncher(Weapon):
    def fire(self, x, y):
        return Rocket(x, y)

# 火箭类
class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(blue)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 15
        if self.rect.bottom < 0:
            self.kill()

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"C:\代码\python公开课\ameri.png")  # 加载敌人图像
        self.image = pygame.transform.scale(self.image, (100, 30))
        self.rect = self.image.get_rect(center=(random.randint(0, width), random.randint(-100, -40)))
    def update(self):
        self.rect.y += 5
        if self.rect.top > height:
            self.kill()

# 创建精灵组
player = Player()
bullets_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# 游戏状态
running = True
paused = False
score = 0

# 游戏主循环
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not paused:
                player.fire()
                player.fire_message = "发射成功！"
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_r:
                if player.hit_count >= 3:
                    player.reset_game()
                    player.fire_message = "按下空格键射击"
                    player.switch_message = "按下 W 切换武器"
            elif event.key == pygame.K_w:
                player.switch_weapon()

    if not paused and not player.is_game_over:
        all_sprites.update()

        # 随机生成敌人
        if random.randint(1, 20) == 1:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies_group.add(enemy)

        # 碰撞检测：子弹击中敌人
        for bullet in bullets_group:
            hits = pygame.sprite.spritecollide(bullet, enemies_group, True)
            for hit in hits:
                bullet.kill()
                score += 1

        # 碰撞检测：玩家碰到敌人
        if pygame.sprite.spritecollideany(player, enemies_group):
            player.respawn()

        # 屏幕绘制
        screen.fill(black)
        all_sprites.draw(screen)

        # 显示得分和生命
        score_text = font.render(f'得分: {score}', True, white)
        lives_text = font.render(f'生命: {player.lives}', True, white)
        hit_count_text = font.render(f'击中次数: {player.hit_count}', True, white)
        weapon_text = font.render(f'当前武器: {type(player.weapon).__name__}', True, white)
        fire_text = font.render(player.fire_message, True, white)
        switch_text = font.render(player.switch_message, True, white)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(hit_count_text, (10, 70))
        screen.blit(weapon_text, (10, 100))
        screen.blit(fire_text, (10, 130))
        screen.blit(switch_text, (10, 160))

    elif player.is_game_over:
        screen.fill(black)
        game_over_text = font.render('游戏结束!按R键重新开始', True, white)
        screen.blit(game_over_text, (width // 2 - 200, height // 2))

    elif paused:
        screen.fill(black)
        pause_text = font.render('游戏暂停，按 P 继续', True, white)
        screen.blit(pause_text, (width // 2 - 200, height // 2))

    pygame.display.flip()
    clock.tick(50)

pygame.quit()
sys.exit()
~~~

~~~sh
pyinstaller --onefile --windowed .\game.py
~~~

---

## 俄罗斯方块游戏开发

> [!info] 游戏操作
> - ==左右方向键==: 移动方块
> - ==上方向键==: 旋转方块
> - ==下方向键==: 加速下落
> - 消除满行得 ==100分==

~~~python
import pygame
import random

# 游戏窗口的宽度和高度
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)

# 用二维数组定义五种俄罗斯方块的形状
SHAPES = [
    [[1, 1, 1, 1]],   # 一字形（I形）
    [[1, 1, 1], [0, 1, 0]],  # T形
    [[1, 1], [1, 1]],  # 方块（O形）
    [[0, 1, 1], [1, 1, 0]],   # Z形
    [[1, 1, 0], [0, 1, 1]]    # 反Z形（S形）
]

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.running = True
        self.board = [[0 for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]

        # 初始化当前方块和下一个方块
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()

        # 方块初始位置(居中)
        self.piece_x = SCREEN_WIDTH // BLOCK_SIZE // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0

        # 下落速度控制变量
        self.fall_speed = 500  # 每500毫秒下落一次
        self.last_fall_time = pygame.time.get_ticks()

        # 游戏得分
        self.score = 0

    def new_piece(self):
        """随机生成一个俄罗斯方块形状"""
        return random.choice(SHAPES)

    def draw_board(self):
        """绘制游戏界面"""
        self.screen.fill(BLACK)
        # 绘制已固定的方块
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.board[y][x]:
                    pygame.draw.rect(self.screen, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # 绘制当前正在下落的方块
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[y])):
                if self.current_piece[y][x]:
                    pygame.draw.rect(self.screen, CYAN, ((self.piece_x + x) * BLOCK_SIZE, (self.piece_y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # 显示分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def run(self):
        """游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(30)

    def handle_events(self):
        """处理用户输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.piece_x -= 1
                    if self.collision():
                        self.piece_x += 1
                elif event.key == pygame.K_RIGHT:
                    self.piece_x += 1
                    if self.collision():
                        self.piece_x -= 1
                elif event.key == pygame.K_DOWN:
                    self.piece_y += 1
                    if self.collision():
                        self.piece_y -= 1
                elif event.key == pygame.K_UP:
                    self.current_piece = self.rotate(self.current_piece)
                    if self.collision():
                        self.current_piece = self.rotate(self.current_piece, -1)

    def rotate(self, piece, direction=1):
        """旋转方块"""
        if direction == 1:
            # 顺时针旋转：将方块转置并反转每行
            return [list(row) for row in zip(*piece[::-1])]
        else:
            # 逆时针旋转：转置后上下翻转
            return [list(row) for row in zip(*piece)][::-1]

    def update(self):
        """更新方块下落状态"""
        self.fall_time = pygame.time.get_ticks()
        if self.fall_time - self.last_fall_time > self.fall_speed:
            self.piece_y += 1
            if self.collision():
                self.piece_y -= 1
                self.lock_piece()
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()
                self.piece_x = SCREEN_WIDTH // BLOCK_SIZE // 2 - len(self.current_piece[0]) // 2
                self.piece_y = 0
                if self.collision():
                    self.running = False
            self.last_fall_time = self.fall_time

    def collision(self):
        """检查碰撞"""
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[y])):
                if self.current_piece[y][x]:
                    board_x = self.piece_x + x
                    board_y = self.piece_y + y
                    if board_x < 0 or board_x >= SCREEN_WIDTH // BLOCK_SIZE or board_y >= SCREEN_HEIGHT // BLOCK_SIZE or self.board[board_y][board_x]:
                        return True
        return False

    def lock_piece(self):
        """将当前方块锁定到棋盘上"""
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[y])):
                if self.current_piece[y][x]:
                    self.board[self.piece_y + y][self.piece_x + x] = 1

    def clear_lines(self):
        """清除已填满的行并更新分数"""
        for y in range(len(self.board) - 1, -1, -1):
            if all(self.board[y]):
                self.score += 100
                del self.board[y]
                self.board.insert(0, [0 for _ in range(SCREEN_WIDTH // BLOCK_SIZE)])

# 创建并运行游戏
game = Tetris()
game.run()
pygame.quit()
~~~
