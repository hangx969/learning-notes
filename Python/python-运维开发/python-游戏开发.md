# 赛车2D游戏开发

~~~python
import io,sys
#导入 Python 的两个内置模块
#io：负责“输入输出”（input/output），也就是读写文件、控制台输出等。
#sys：访问与 Python 解释器相关的系统参数，比如输入输出流（stdin、stdout）、命令行参数等。
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#sys.stdout这是 Python 的“标准输出流”，就是你平时用 print() 输出的目标。输出的结果会在控制台显示。
#但 sys.stdout 其实也可以变成一个“字节流”，这就是 sys.stdout.buffer，它处理的是数据的二进制格式，不涉及直接的字符编码。
#io.TextIOWrapper 就是将这个“字节流”转换回“文本流”，而且让它知道要使用 UTF-8 编码，这样就能正确处理中文字符了。

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
        #self.screen_width // 2：这部分是将屏幕宽度（self.screen_width）除以 2，得到屏幕中心的位置。
        #例如，如果屏幕的宽度是 800 像素，那么 800 // 2 就是 400 像素，即屏幕的水平中心。
        #- 25：由于玩家的汽车是一个固定大小的图像（在代码中，大小为 50x100 像素），
        # 如果我们把它的中心设置在屏幕的中心，那么汽车的左边缘会位于屏幕中心的 25 像素位置（因为宽度是 50 像素，所以从中心向左偏移 25 像素，才能让车的中心位于屏幕的中心）。
        #这样，self.player_x = 400 - 25 就是将玩家汽车的 左边缘 放置在屏幕中心左侧 25 像素的位置，即 375 像素的位置。玩家汽车的右边缘距离在425像素位置
        # 确保玩家汽车的中心是位于屏幕的水平中心。
        self.player_y = self.screen_height - 120 #玩家汽车的垂直位置是距离屏幕底部 120 像素
        self.road_y = 0 #初始化背景滚动位置为0，表示背景尚未开始滚动
        #随着游戏的进行，背景会不断向上滚动，self.road_y 值会逐渐增大，导致背景图片的 Y 坐标变动，从而模拟出背景向上的滚动效果。

        self.enemies = [] #  初始化敌人车辆列表为空，表示尚未生成敌人车辆，将在游戏开始时生成敌人车辆
        self.spawn_multiple_enemies() #调用函数生成多个敌人车辆

        # 加载背景音乐 
        self.load_background_music() #  调用函数加载背景音乐

        # 加载碰撞音效
        self.load_collision_sound() #  调用函数加载碰撞音效

    def load_background_music(self):
        """加载背景音乐"""
        if os.path.exists(self.background_music): #  检查背景音乐文件是否存在
            try:
                pygame.mixer.music.load(self.background_music) #  尝试加载背景音乐文件
                pygame.mixer.music.play(-1)  # 循环播放背景音乐 ，-1表示无限循环
            except pygame.error as e: #  捕获加载音乐时的错误
                print("背景音乐加载失败:", e) #  捕获pygame错误并打印错误信息
        else:
            print("背景音乐文件未找到:", self.background_music) #  如果背景音乐文件不存在，打印文件未找到的信息

    def load_collision_sound(self):
        """加载碰撞音效"""
        if os.path.exists(self.collision_sound): #  检查碰撞音效文件是否存在
            try:
                self.collision_sound_effect = pygame.mixer.Sound(self.collision_sound) #  尝试加载碰撞音效
            except pygame.error as e: #  捕获加载音效时的错误
                print("碰撞音效加载失败:", e) #  捕获pygame错误并打印错误信息
                self.collision_sound_effect = None #  如果加载失败，将碰撞音效设为None
        else:
            print("碰撞音效文件未找到:", self.collision_sound) #  如果碰撞音效文件不存在，打印文件未找到的信息
            self.collision_sound_effect = None #  将碰撞音效设为None

    def play_collision_sound(self):
        """播放碰撞音效"""
        if self.collision_sound_effect: #  检查碰撞音效是否已加载
            self.collision_sound_effect.play() #  播放碰撞音效

    def spawn_multiple_enemies(self, count=5):
        """生成多个敌人汽车位置"""
        self.enemies = [] #  初始化敌人列表
        for _ in range(count): 
            self.spawn_enemy()
        #循环count次，每次调用spawn_enemy方法生成一个敌人汽车

    def spawn_enemy(self):
        """随机生成一个敌人汽车位置和速度"""
        enemy_x = random.randint(200, self.screen_width - 250) 
        #随机生成敌人汽车的水平位置（X坐标）
        #random.randint(200, self.screen_width - 250)：表示敌人车辆的左上角 X 坐标在 200 到 屏幕宽度减250 的范围内随机选择一个整数
        #这样做是为了控制敌人车辆不会生成在屏幕太边缘的地方，避免它们“飞出”赛道边界或影响玩家的视野和游戏性。
        enemy_y = random.randint(-600, -100)
        #随机生成敌人汽车的垂直位置（Y坐标），范围在-600到-100像素之间，表示敌人车辆最初生成的位置在屏幕之外的上方，距离屏幕顶部还有一定距离。
        # 这样做的目的是让敌人“从屏幕外往下开”，营造出敌人从远处驶来的效果。
        enemy_speed = self.enemy_base_speed + random.random() * 2  # 生成敌人汽车的速度，基础速度加上一个0到2之间的随机数
        self.enemies.append([enemy_x, enemy_y, enemy_speed]) #  将敌人的初始位置和速度添加到敌人列表中

    def run_game(self):
    #这段代码是你游戏的主循环函数 —— run_game()，它控制了整个游戏运行的流程，包括玩家操作、敌人移动、碰撞检测、背景滚动、绘图渲染等。
        #游戏启动和事件处理
        self.running = True #  设置游戏运行状态为True,意味着游戏主循环应该开始运行。
        while self.running: # 游戏主循环开始。当 self.running 是 True 时，这个循环会持续执行，实现游戏持续进行。
            for event in pygame.event.get(): #  遍历所有 Pygame 收集到的事件（比如键盘按下、鼠标点击、关闭窗口等）。
                if event.type == pygame.QUIT: #  如果事件类型是QUIT事件
                    self.running = False #  设置 self.running = False，跳出主循环。
                    pygame.quit() # 调用 pygame.quit() 关闭 Pygame。
                    sys.exit() # 使用 sys.exit() 完全退出程序。

            # 玩家逻辑，玩家左右和加速减速控制
            keys = pygame.key.get_pressed() #  获取当前按键状态，返回一个布尔值数组，表示每个键是否被按下
            if keys[pygame.K_LEFT] and self.player_x > 200: # 如果按了左方向键，并且玩家车的位置在赛道左边界内（大于200像素），就向左移动8个像素。
                self.player_x -= 8 # 玩家向左向左移动8个像素
            if keys[pygame.K_RIGHT] and self.player_x < self.screen_width - 250: #  如果按了右键，并且玩家位置小于屏幕宽度减去250像素防止超出屏幕右侧）
                self.player_x += 8 #  玩家向右移动8个像素
            if keys[pygame.K_UP]: # 如果按了向上键
                self.player_speed += 0.1   #  玩家加速，速度增加0.1
            if keys[pygame.K_DOWN] and self.player_speed > 1: # 如果按了向下键，并且玩家速度大于1
                self.player_speed -= 0.1  #减少玩家速度，每次减少0.1

            # 背景滚动控制代码

            #游戏背景为什么要“滚动”？
            #在赛车游戏中，汽车其实是静止在屏幕上不动的（例如玩家的车总是停在底部中间）。为了制造一种“车在往前开”的错觉，我们通过让背景（道路图片）向下移动，来模拟这种运动。
            # 就像你坐在地铁上看窗外，感觉是地面在动，实际上是你在动。游戏里用同样的原理：背景动 → 视觉上就是你在移动。

            self.road_y += self.player_speed / 2   #self.road_y=  self.road_y+self.player_speed / 2
            #self.road_y 是背景图（或者说赛道图片）绘制时在屏幕上的垂直位置（Y坐标）。
            #每一帧中，我们根据 self.player_speed 增加 road_y。self.player_speed / 2 表示玩家速度越快，背景滚动也越快，增强真实感。
            #如果 player_speed = 10，则每一帧背景就会下移 5 像素。
            #效果就是：背景不断向“下”滚动，模拟你在往前开。

            if self.road_y >= self.screen_height: #如果 road_y 超过了屏幕高度（例如屏幕高是 600，road_y ≥ 600），就表示背景图片已经完全滚动出了屏幕。
                self.road_y = 0 #这一步就是让背景重置回顶部，从头开始滚动。所以你可以想象背景是一张无限循环的赛道图片，它从上往下滚，当滚完一轮，就重新开始。

                #假设我们屏幕高为 600，背景图片也是 600 像素高：

                # 帧数  | road_y 的值 | 背景显示位置
                # 第1帧 | 0 |          背景从顶部开始
                # 第2帧 | 5 |          背景下移5像素
                # 第3帧 | 10 |         背景下移10像素（累计）
                # ... | ... |          ...
                # 第120帧 | 600 |      背景刚好滚完一整张
                # 第121帧 | 重置为 0 |  背景从顶部重新开始 → 形成“循环滚动”效果
            

            # 移动敌人车辆
            self.move_enemies() #  调用方法移动敌人车辆

            # 计算赛程距离和动态加速
            self.distance += self.player_speed / 10 #  根据玩家速度更新赛程距离
            if int(self.distance) % 100 == 0:  # 敌人每移动100像素距离稍微加速
                self.enemy_base_speed += 0.1  # 敌人基础速度增加0.1

            # 检查碰撞
            if self.is_collision(): #  如果发生碰撞
                self.play_collision_sound() #  播放碰撞声音
                pygame.mixer.music.stop()  # 停止背景音乐
                self.game_over() #  游戏结束

            # 绘制背景
            self.draw_background() #  调用方法绘制背景
            # 显示玩家车、敌人车、当前赛程距离，然后刷新画面，控制帧率。
            self.screen.blit(self.player_car, (self.player_x, self.player_y)) #把玩家的赛车图片（self.player_car）绘制（blit）到屏幕上，位置是 (self.player_x, self.player_y)。
            for enemy_x, enemy_y, _ in self.enemies: 
                self.screen.blit(self.enemy_car, (enemy_x, enemy_y)) # 遍历所有敌人车辆的位置信息,把它们一辆一辆画到屏幕上。
            # 显示赛程距离
            font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 28) 
            #pygame.font.Font() 用来加载一个字体文件。
            #创建一个字体对象，用的是系统的微软雅黑（msyh.ttc），字号为 28。
            distance_text = font.render(f"赛程: {int(self.distance)} 米", True, (255, 255, 255))
            self.screen.blit(distance_text, (10, 10)) #  在屏幕的左上角(10, 10)位置显示距离，白色字体
            pygame.display.flip() #把刚刚画好的整个画面一次性显示出来。这一帧的背景、车、文字，全部更新显示。
            self.clock.tick(30) #控制帧率，意思是：让这个循环最多每秒执行 30 次。如果你去掉这行，游戏会运行得非常快（太多帧），看起来不流畅，而且 CPU 占用很高。限制刷新频率，让游戏节奏稳定下来。

    def draw_background(self):
        #这是一个类方法，用来更新游戏背景（赛道+草地+分隔线），实现赛道的视觉效果。
        self.screen.fill((0, 128, 0)) 
        #self.screen.fill 是用纯色填充整个游戏窗口。颜色 (0, 128, 0) 是深绿色，代表赛道周围的草地或树林环境。
        #颜色对照表：https://www.w3schools.com/colors/colors_picker.asp
        pygame.draw.rect(self.screen, (50, 50, 50), (200, 0, self.screen_width - 400, self.screen_height)) 
        #  使用pygame的draw.rect方法绘制一个矩形，代表赛道
        # 参数1：屏幕对象，用于指定赛道在绿色屏幕上绘制，self.screen 表示整个游戏窗口。
        # 参数2：颜色值(50, 50, 50)，表示矩形赛道是灰色的，
        # 参数3：矩形的位置和大小，(200, 0, self.screen_width - 400, self.screen_height) 
        # 200：矩形左上角的 x 坐标（矩形从屏幕左侧向右偏移 200 像素）。
        # 0：矩形左上角的 y 坐标（矩形从屏幕顶部开始）。
        # self.screen_width - 400：矩形的宽度（屏幕宽度减去 400 像素，留出两侧的边界）。
        # self.screen_height：矩形的高度（屏幕的高度）。
        #结果：赛道位置在屏幕正中间，距离左右各有 200 像素的间隙，整体作用是画出道路背景，为游戏的赛道提供视觉区域。
        for i in range(0, self.screen_height, 60): 
            #  使用for循环在道路上绘制白色的分隔线
            # range(0, self.screen_height, 60)生成从0到屏幕高度，步长为60的序列
            # 每隔60像素绘制一条分割线
            # i是每条线的基础y坐标
            pygame.draw.line(self.screen, (255, 255, 255),
                             (self.screen_width // 2 - 5, i + self.road_y), 
                             (self.screen_width // 2 + 5, i + 40 + self.road_y), 5)
            # 使用pygame的draw.line方法绘制一条线
            # self.screen：表示游戏窗口的表面，所有的绘制都会显示在这个屏幕上。
            # (255, 255, 255)：表示线的颜色，这里是白色。
            # 线起点坐标：(self.screen_width // 2 - 5, i + self.road_y)
            # x = self.screen_width // 2 - 5 → 屏幕中心偏左 5 像素。
            # y = i + self.road_y → 这是线的起始垂直坐标。self.road_y 是滚动偏移量，让线条不断往上移动，产生赛道滚动的视觉效果。
            
            #线的终点坐标：(self.screen_width // 2 + 5, i + 40 + self.road_y)
            #x = self.screen_width // 2 + 5 → 屏幕中心偏右 5 像素。
            #y = i + 40 + self.road_y → 线的终点垂直坐标。线长为 40 像素。
            # 线宽：5 像素。

    def move_enemies(self):
        """控制敌人车辆在屏幕上移动并清理屏幕外的敌人"""
        for enemy in self.enemies: #  遍历所有敌人车辆
            enemy[1] += enemy[2]  
        #self.enemies 是一个列表，里面的每一项是一个敌人，比如 [enemy_x, enemy_y, enemy_speed]。
        # enemy[1] 是敌人的垂直坐标（y 轴）。
        # enemy[2] 是敌人的速度。
        # 所以 enemy[1] += enemy[2] 就是：每一帧都根据速度往下移动敌人车辆。
        # 这就像车在你面前一辆辆从上往下冲一样。
        # 敌人速度越快，移动也越快。

        self.enemies = [enemy for enemy in self.enemies if enemy[1] < self.screen_height] 
        #这行代码是一个列表推导式。遍历 self.enemies 这个敌人列表，只保留那些 enemy[1]（也就是敌人y坐标）小于屏幕高度的敌人（也就是y 坐标还没超出屏幕底部的），重新生成一个新的列表。
        #反过来说，所有 y 坐标大于或等于屏幕高度的敌人就被丢弃了，因为他们已经滑出屏幕底部，看不到了。
        if len(self.enemies) < 5: 
        # 检查当前屏幕上还剩几个敌，如果数量小于 5，说明有敌人已经“滚”出去屏幕外了，就调用：self.spawn_enemy() 来生成一个新的敌人，放到屏幕上端外（通常 y 是负值）并开始滑下来。
            self.spawn_enemy() 

    def is_collision(self):
        """检查玩家和敌人之间的碰撞"""
        # 你正在做一个赛车游戏，现在你要判断：
        # “玩家的车有没有撞上敌人的车？”
        # 每辆车都是一个矩形区域，所以你用了最常见的碰撞检测方式：AABB 碰撞检测（Axis-Aligned Bounding Box）
        # 翻译一下就是：
        # 检查两个“长方形”是否有重叠区域。

        for enemy_x, enemy_y, _ in self.enemies: #  遍历所有敌人，把所有敌人都拿出来，拿到它的坐标 (enemy_x, enemy_y)。
            # 玩家与敌人的碰撞检测条件，检查玩家和敌人的矩形是不是有交集。
            if (self.player_x < enemy_x + 50 and   # 玩家的左边界在敌人的右边界 的左边
                self.player_x + 50 > enemy_x and   # 玩家的右边界在敌人的左边界的右边
                self.player_y < enemy_y + 100 and  # 玩家的上边界在敌人的下边界 的上边
                self.player_y + 100 > enemy_y):   # 玩家的下边界在敌人的上边界 的下边
                return True #  如果发生碰撞，返回True
                
        return False #  如果没有发生碰撞，返回False

    def game_over(self):
        """处理游戏结束逻辑"""
        choice = messagebox.askyesno("游戏结束", f"你已行驶 {int(self.distance)} 米！\n是否重新开始游戏？") #  弹出消息框，询问玩家是否重新开始游戏
        if choice:  # 选择是 
            self.reset_game() #  调用reset_game方法重置游戏状态
            self.run_game()  # 重新开始游戏
        else:  # 选择否
            pygame.quit() #  退出Pygame库
            sys.exit() #  退出系统

    def reset_game(self):
        """重置游戏状态"""
        self.player_speed = 5 #  将玩家速度重置为5
        self.enemy_base_speed = 3 #  将敌人基础速度重置为3
        self.distance = 0 #  初始化距离为0
        self.road_y = 0 #  初始化道路的Y坐标为0
        self.player_x = self.screen_width // 2 - 25 #  初始化玩家的X坐标为屏幕宽度的一半减去25
        self.enemies.clear() #  清空敌人列表
        self.spawn_multiple_enemies() #  生成多个敌人

# 使用 tkinter 创建主界面
class RacingApp:
    #这个类是用来创建主界面窗口的（不是游戏本身，而是菜单界面）：
    def __init__(self, root):
        self.root = root #  初始化根窗口
        self.root.title("竞速赛车游戏") #  设置窗口标题
        self.root.geometry("900x700") #  设置窗口大小
        
         # 设置字体大小
        button_font = ("Microsoft YaHei", 18)  # 字体为Microsoft YaHei，大小为 18

        # 启动游戏按钮
        self.start_button = tk.Button(self.root, text="开始游戏", command=self.start_game,font=button_font) #  创建一个按钮，用于开始游戏，按钮文本为“开始游戏”，点击时调用start_game方法
        self.start_button.pack(pady=20) #  将按钮添加到窗口中，垂直间距是20像素
        
        # 退出按钮
        self.exit_button = tk.Button(self.root, text="退出", command=self.root.quit,font=button_font)
        self.exit_button.pack(pady=10) #  将按钮添加到窗口中，并设置按钮在垂直方向上的外边距为 10 像素

    def start_game(self):
        self.root.withdraw() # 隐藏当前的 Tk 窗口，以便显示游戏窗口
        game = RacingGame() #  创建一个 RacingGame 对象
        game.run_game() #  调用 RacingGame 对象的 run_game 方法，开始运行游戏
        self.root.deiconify()  #游戏结束后，重新显示 Tk 窗口

# 创建主窗口并启动应用
if __name__ == "__main__":
    root = tk.Tk() 
    #创建一个 Tkinter 的主窗口（也就是你的图形界面窗口）。root 是窗口对象，之后你要往这个窗口里加按钮、标签等控件。相当于打开了一个白纸，你接下来可以在上面画各种控件。
    app = RacingApp(root) 
    # 创建一个 RacingApp 类的实例，把你刚才创建的窗口 root 传进去。
    #这个 RacingApp 类里做了这些事：
    # 给窗口加标题、设置大小
    # 创建了“开始游戏”和“退出”的两个按钮
    # 给按钮设置功能，比如点击开始游戏后会打开 Pygame 窗口
    root.mainloop() 
    #Tkinter 的事件主循环，它会让窗口保持“始终运行在前端”，等待用户操作（比如点击按钮）。如果你不写 mainloop()，窗口会闪一下就关掉。
    #它会不停检测事件（比如鼠标点击、键盘输入），然后调用对应的函数（比如 start_game()）。
~~~

# 打飞船2D游戏开发

~~~python
import sys,io 
#导入 Python 的两个内置模块
#io：负责“输入输出”（input/output），也就是读写文件、控制台输出等。
#sys：访问与 Python 解释器相关的系统参数，比如输入输出流（stdin、stdout）、命令行参数等。
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#sys.stdout这是 Python 的“标准输出流”，就是你平时用 print() 输出的目标。输出的结果会在控制台显示。
#但 sys.stdout 其实也可以变成一个“字节流”，这就是 sys.stdout.buffer，它处理的是数据的二进制格式，不涉及直接的字符编码。
#io.TextIOWrapper 就是将这个“字节流”转换回“文本流”，而且让它知道要使用 UTF-8 编码，这样就能正确处理中文字符了。

import pygame 
#pygame 是一个用于开发 2D 游戏和多媒体应用的第三方库，提供了处理图形、声音、事件和其他游戏相关功能的工具。
#你可以用 pygame 来处理图像、音频、用户输入（键盘、鼠标）、碰撞检测等，常用于游戏开发。你可以使用 pygame 来加载图片、播放音效、处理动画等。
import random 
#random 是 Python 的标准库模块，提供了生成随机数的功能。它可以生成随机数、随机选择列表中的元素等。
# 它在游戏中常用于生成随机事件，比如随机生成敌人位置、掉落物品、随机数决定的游戏元素。

# 初始化 Pygame
pygame.init()
#初始化 pygame 库，为游戏设置一些环境。pygame 是一个用于开发2D游戏的库，包括图像、声音、事件、游戏循环等功能。

width, height = 800, 600 
#这行代码定义了游戏窗口的大小，width 表示宽度，height 表示高度。在这个例子中，窗口的尺寸是 800 像素（宽）× 600 像素（高）。

screen = pygame.display.set_mode((width, height)) 
#这行代码通过 pygame.display.set_mode() 创建一个游戏窗口，参数是一个元组 (width, height)，也就是窗口的尺寸。
#返回值 screen 是一个 Surface 对象，代表游戏的主画布，之后所有的图像绘制都会显示在这个画布上。

pygame.display.set_caption("射击美国飞船") 
#这行代码设置了游戏窗口的标题栏文本，也就是你在窗口顶部看到的名字。在这里标题是 "射击美国飞船"，可以随意更换为你喜欢的名字，比如 "太空大战" 或 "超级战机" 等。

# 颜色定义
black = (0, 0, 0) #  定义黑色
white = (255, 255, 255) #  定义白色
red = (255, 0, 0) #  定义红色
blue = (0, 0, 255) #  定义蓝色
#颜色对照表：https://www.w3schools.com/colors/colors_picker.asp

# 加载中文字体
try:
    # 确保您有适当的字体文件（例如：SimHei.ttf），并指定其路径
    font_path = "C:\Windows\Fonts\STXIHEI.TTF"  # 请替换为你的字体文件路径，微软雅黑
    font = pygame.font.Font(font_path, 20)  # 设置字体和大小
except FileNotFoundError:
    font = pygame.font.SysFont(None, 20)  # 如果字体文件未找到，则使用默认字体

# 玩家类
class Player(pygame.sprite.Sprite):
    #定义一个**“玩家角色”类**，也就是你在游戏中操控的飞船。 它继承自 pygame.sprite.Sprite父类，具有这个类的所有方法
    # 代表它是一个“精灵”——游戏中可移动的物体，比如人物、子弹、敌人等。
    def __init__(self):
        #定义一个构造函数，是“造一个玩家角色”的过程，相当于你把这个角色生出来，接下来要给它画身体、放位置、设置生命等。
        super().__init__()
        #super()表示可以继承父类pygame.sprite.Sprite下的方法，才可以创建玩家角色这些属性

        #画出玩家的样子
        self.image = pygame.Surface((30, 50), pygame.SRCALPHA) 
        pygame.draw.polygon(self.image, blue, [(15, 0), (30, 50), (0, 50)]) 
        # 创建一个大小为 30像素（宽度）×50像素（高度） 的半透明画布（Surface）。
        # 在这张画布上画了一个蓝色的三角形（看起来像一架飞船），顶点坐标是：
        # 顶部中间点 (15, 0)，在30*50的画布里，类似于三角形顶点在画布中间
        # 底部右边 (30, 50)
        # 底部左边 (0, 50)

        #设置玩家初始位置
        self.rect = self.image.get_rect(center=(width // 2, height - 50)) 
        #self.rect是用来管理玩家位置和大小的“框框”（矩形区域）。矩形框放到屏幕中心，离底部50像素

        #设置状态变量
        self.lives = 3 # 默认玩家有3条生命
        self.hit_count = 0 #玩家被击中的次数，游戏未开始，还没被击中
        self.is_game_over = False # 初始化游戏状态，表示游戏未结束
        self.weapon = RegularGun()  # 玩家的初始武器是普通枪（RegularGun）
        self.fire_message = "按下空格键射击"  # 开火提示
        self.switch_message = "按下 W 切换武器"  # 切换武器提示

    def update(self):
        #update(self)：更新玩家位置，根据按键控制左、右移动。
        keys = pygame.key.get_pressed() #  获取当前按键状态
        if keys[pygame.K_LEFT] and self.rect.left > 0: 
        #  如果按下左键且角色未超出左边界
        #self.rect 是玩家角色的矩形区域，left 属性表示该矩形的左边界坐标。
        # 这个条件判断玩家角色的左边界是否超过了屏幕的最左端（即坐标 0）。
        # 如果 self.rect.left > 0，说明玩家角色的左边界没有超出屏幕的最左侧。
            self.rect.x -= 5 #玩家的水平坐标 self.rect.x 会减少 5，即向左移动 5 个像素。
        if keys[pygame.K_RIGHT] and self.rect.right < width: #  如果按下右键且角色未超出右边界
            #self.rect 是玩家角色的矩形区域，right 属性表示该矩形的右边界坐标。
            # 这个条件判断玩家角色的右边界是否超过了屏幕的最右端。
            # width 是屏幕的宽度（即屏幕的右边界），如果 self.rect.right < width，
            # 则表示玩家角色的右边界没有超出屏幕的最右端。
            self.rect.x += 5 #  玩家的水平坐标 self.rect.x 会增加 5，即向右移动 5 个像素。

    def switch_weapon(self):
        #switch_weapon(self)：切换武器，依次切换普通枪、散弹枪、火箭筒。
        if isinstance(self.weapon, RegularGun): 
            #isinstance(self.weapon, RegularGun) 是 Python 中的一种类型检查方法，意思是检查 self.weapon 是否是 RegularGun 类的一个实例或其子类的实例。
            #检查当前武器是否为普通枪
            self.weapon = Shotgun() #  切换为散弹枪
            self.switch_message = "切换为散弹枪" #  设置切换武器时的提示信息
        elif isinstance(self.weapon, Shotgun): #  如果当前武器是散弹枪
            self.weapon = RocketLauncher() #  切换武器为火箭筒
            self.switch_message = "切换为火箭筒" #  设置切换武器时的提示信息
        else: #  如果当前武器既不是散弹枪也不是火箭筒
            self.weapon = RegularGun() #  切换武器为普通枪
            self.switch_message = "切换为普通枪" #  设置切换武器时的提示信息

    def fire(self):
        #这个函数是玩家按下“空格键”开火时调用的函数。整体目的：
        # 创建一发子弹（或者多发，如果是散弹枪）
        # 把这些子弹交给 Pygame 的精灵组管理
        # 这样子弹就可以动了、能显示出来、能检测碰撞

        #第一步：让武器发射子弹
        bullets = self.weapon.fire(self.rect.centerx, self.rect.top) 
        #self.weapon：当前玩家用的是什么武器（可能是普通枪、散弹枪、火箭筒）
        #.fire(...)：调用武器的 fire() 方法，让它“造出”子弹
        #self.rect.centerx：玩家飞船的水平中点（子弹从飞船中央射出）
        #self.rect.top：玩家飞船的顶部位置（子弹从顶端往上飞）
        #bullets 是这个 fire() 方法返回的子弹，可能是一个子弹，也可能是一堆子弹（列表）

        #第二步：判断子弹是一发还是多发？
        if isinstance(bullets, list): 
            #检查 bullets 是不是个“列表”
            #也就是说，如果你拿的是散弹枪，就会一次发出好几颗子弹，组成一个列表。
            # 如果是“多发子弹”怎么办？
            for bullet in bullets: #  遍历子弹列表
                all_sprites.add(bullet) 
                bullets_group.add(bullet)
                #每一发子弹都：
                # 加入 all_sprites：这是个总的精灵组，游戏里所有“会动的对象”都在这儿管理。
                # 加入 bullets_group：这是专门放“子弹”的组，用于检查碰撞、控制子弹速度等。
        elif bullets is not None: #  如果开火返回的是单个子弹对象
            all_sprites.add(bullets) #  将子弹添加到所有精灵组
            bullets_group.add(bullets) #  将子弹添加到子弹组
        #总结：fire(self) 让玩家根据当前武器发射子弹，无论是单发还是多发，都自动加入游戏中进行管理和显示。

    def respawn(self):
        #respawn(self) 方法是“玩家复活”时会调用的函数
        self.rect.center = (width // 2, height - 50) #  将玩家位置重置到屏幕底部中央
        # 这行代码的意思是：
        # 把玩家的位置重新放回屏幕下方中央。
        # width // 2：表示屏幕的水平方向中心点。
        # height - 50：表示距离屏幕底部还有 50 像素的位置。
        self.hit_count += 1 #  增加被击中次数
        if self.hit_count >= 3: #  如果被击中次数达到3次
            self.is_game_over = True #意味着游戏结束了，True意味着游戏的主循环可以检查这个状态，并显示“游戏结束”画面。

    def reset_game(self):
        #这段函数是重新开始游戏时要调用的，重置所有玩家状态和游戏数据，让游戏像刚启动一样
        self.hit_count = 0 #  重置被击中次数
        self.lives = 3 #  重置生命值
        self.is_game_over = False #  设置游戏未结束
        self.rect.center = (width // 2, height - 50) #  将玩家位置重置到屏幕底部中央，距离底部50个像素
        bullets_group.empty() #游戏中子弹是用“精灵组 bullets_group”来管理的。empty() 的意思是把里面所有子弹删掉。防止上一局留下的子弹还在飞。
        enemies_group.empty() # 把屏幕上所有敌人都清空。不然你重新开始的时候，敌人还停留在原地。
        all_sprites.add(self) #把玩家重新放入游戏画面中，all_sprites 是“所有要绘制的游戏对象”的集合。玩家也必须在这个组里，Pygame 才会帮你绘制在屏幕上，如果忘了加，玩家角色会“消失不见”。

# 武器基类
class Weapon:
    #这行代码定义了一个叫 Weapon 的类（即武器基类）。
    #基类（或父类）意味着可以被其他类继承，其他具体的武器（如普通枪、火箭筒等）将从这个类继承。
    def fire(self, x, y):
        #这是 Weapon 类中的一个方法，名称为 fire，表示发射武器的行为。
        # fire 方法有两个参数：x 和 y，通常这两个参数代表发射点的坐标。
        #出 NotImplementedError 异常：
        raise NotImplementedError("This method should be overridden in subclasses.")
    #NotImplementedError 是 Python 内置的异常，通常用于抽象基类中未实现的方法。
    # 这行代码的作用是：
    # 当你尝试调用 fire 方法时，如果它没有被子类实现（即没有提供具体的发射行为），Python 会抛出一个 NotImplementedError 异常。
    # 这个异常的作用是提醒开发者：“你必须在子类中重写（实现）这个 fire 方法”。
    
    #为什么要这样设计？
    #抽象基类：Weapon 类其实是一个抽象类，用来定义所有武器共有的行为，但并不直接提供完整的实现。
    #你会看到具体的武器类（如 RegularGun、RocketLauncher 等）继承自 Weapon 类，并提供各自的 fire 实现。例如，RegularGun 可能发射单个子弹，而 Shotgun 可能发射多个子弹。


# 普通枪类
class RegularGun(Weapon):
    #定义了一个名为 RegularGun 的新类，表示一种具体的武器（普通枪）。
    #RegularGun 类继承自 Weapon 类，这意味着它继承了 Weapon 类的所有属性和方法，
    # 并且必须实现 Weapon 类中的抽象方法（在这里是 fire 方法）。
    def fire(self, x, y):
        #这是 RegularGun 类中的一个方法，名称为 fire，表示普通枪的发射行为。
        # 参数 x 和 y 表示枪发射时子弹的起始坐标。
        return Bullet(x, y) #  返回一个子弹对象，x和y表示子弹的位置

# 子弹类
class Bullet(pygame.sprite.Sprite):
    #这行代码定义了一个名为 Bullet 的类，表示游戏中的子弹。
    #Bullet 继承自 pygame.sprite.Sprite 类，pygame.sprite.Sprite 是 Pygame 提供的一个基本类，用于管理游戏中的“精灵”（sprite）。
    # 精灵是游戏中所有动态对象的抽象，比如玩家角色、敌人、子弹等。
    #通过继承，Bullet 类可以拥有 Sprite 类的功能，例如更新位置、碰撞检测等。
    def __init__(self, x, y):
        #__init__ 是类的构造方法，在创建 Bullet 对象时会自动调用。
        #x 和 y 是传递给构造方法的参数，表示子弹发射时的 位置
        super().__init__() 
        #super() 是 Python 中的一个内置函数，用于调用父类的方法。在这里，它调用了 pygame.sprite.Sprite 的构造方法（__init__）。
        #通过调用父类的构造方法，Bullet 类继承了 Sprite 类的属性和方法，如图像管理、矩形位置管理等。
        #这一步是确保 Bullet 类的对象能够正确初始化，并且具备 Sprite 类的所有基本功能。

        #创建子弹的图像（Surface）
        self.image = pygame.Surface((5, 10)) 
        # pygame.Surface((5, 10)) 创建了一个 5x10 像素 的矩形 图像，这是子弹的显示图像。
        #Surface 是 Pygame 用来创建图像的类，它接受一个包含宽度和高度的元组作为参数。在这里，子弹的图像是一个 5 像素宽、10 像素高的矩形。
        self.image.fill(red) # 将刚刚创建的 5x10 像素的矩形填充为红色

        #创建矩形 rect（位置和大小）
        self.rect = self.image.get_rect(center=(x, y)) 
        #self.image.get_rect(center=(x, y)) 返回一个 矩形（rect），用于表示图像的位置和大小。
        #这个矩形的 位置 和 大小 可以通过 Rect 对象进行管理。
        #center=(x, y) 将矩形的 中心点 设置为 (x, y)，即子弹的发射点。这样，子弹的中心就会出现在传入的 (x, y) 坐标位置。
        #这一步确保了子弹在屏幕上的显示位置是正确的，基于传入的 x 和 y 坐标。

    def update(self):
        #update 是 Bullet 类的一个方法，通常用于更新子弹的位置和状态
        self.rect.y -= 10 #将子弹的矩形区域 rect 的 y 坐标减少 10 像素，表示子弹在屏幕上向上移动。
        if self.rect.bottom < 0: #  如果子弹的底部位置小于0，表示子弹已经超出屏幕顶端范围
            self.kill() #  调用kill方法将子弹移除


# 散弹枪类
class Shotgun(Weapon):
    #定义了一个名为 Shotgun 的类，表示游戏中的散弹枪。继承自 Weapon 类
    def fire(self, x, y):
        #fire 是 Shotgun 类的一个方法， 用于模拟散弹枪发射多个子弹的行为。
        #该方法接收两个参数：x 和 y，表示子弹的发射位置
        bullets = [] #  定义一个空列表，用于存储散弹枪发射的所有子弹，散弹枪一次发射多个子弹，因此我们需要一个列表来存放这些子弹。

        # 发射三个子弹
        for offset in [-10, 0, 10]:
            #for offset in [-10, 0, 10]：这是一个 for 循环，它遍历一个包含三个元素的列表 [-10, 0, 10]。每个元素代表一个子弹的水平偏移量。
            # offset = -10 表示左侧偏移；
            # offset = 0 表示发射在中心；
            # offset = 10 表示右侧偏移。
            #这模拟了散弹枪的特点：一次发射多个子弹，并且子弹的位置会有一定的分散，形成一个扇形的发射范围。 
            
            bullet = Bullet(x + offset, y) #对于每个 offset 值，创建一个新的 Bullet 对象。
            #子弹的发射位置是 (x + offset, y)，也就是根据偏移量 offset 来决定子弹的水平位置，y 位置保持不变。
            #例如：
            # 当 offset = -10 时，子弹的水平位置为 x - 10，模拟向左发射；
            # 当 offset = 0 时，子弹的水平位置为 x，表示从中心发射；
            # 当 offset = 10 时，子弹的水平位置为 x + 10，表示向右发射。

            bullets.append(bullet) #将创建的 Bullet 对象添加到 bullets 列表中。这样，bullets 列表最终会包含三个子弹对象。
        return bullets  # 返回子弹列表

# 火箭筒类
class RocketLauncher(Weapon):
    #RocketLauncher 是一个类，表示火箭发射器，继承自基类 Weapon。
    def fire(self, x, y):
        #为 RocketLauncher 类定义了一个 fire 方法，用于实现武器的开火逻辑。
        #self：指代当前的 RocketLauncher 实例。
        #x：火箭发射的初始水平位置。
        #y：火箭发射的初始垂直位置。
        return Rocket(x, y) 
        # 返回Rocket对象，表示一枚发射的火箭。

# 火箭类
class Rocket(pygame.sprite.Sprite): # 创建一个叫 Rocket 的类，继承自 pygame 的 Sprite 类
    def __init__(self, x, y):
        super().__init__()
        #super().__init__()：调用父类 pygame.sprite.Sprite 的初始化方法，这样才能让火箭对象被添加进 Pygame 的精灵组里，并被正确管理。
        self.image = pygame.Surface((10, 20)) #pygame.Surface 是一个图像对象，这里创建了一个 10 像素宽*20 像素高的矩形。它就像一个贴纸，是显示在屏幕上的。
        self.image.fill(blue) #火箭的外观，10 像素宽*20 像素高的矩形是蓝色的
        self.rect = self.image.get_rect(center=(x, y)) #把火箭贴纸摆到屏幕上的位置。get_rect() 是 Surface 自带的方法，它返回一个矩形区域对象（Rect），用于控制图像的位置、大小、碰撞等。
        #center=(x, y) 表示：把这个火箭的“中心”对准屏幕上的 (x, y)，这通常是我们点击或者发射时的位置。

    
    #火箭飞行动作：
    def update(self):
        self.rect.y -= 15 #self.rect.y -= 15 #火箭每帧往上移动 15 像素（屏幕坐标系中，y 轴向下增长，减小 y 即是向上移动）。
        if self.rect.bottom < 0: #检查火箭是否完全飞出了屏幕上方（bottom 表示底边的 y 坐标，小于 0 就说明完全飞出了上边界）。
            self.kill() #将当前精灵从所有精灵组中移除。一旦移除，这个火箭就不会再被渲染、更新，也不会参与碰撞检测等操作。


# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"C:\代码\python公开课\ameri.png")  # 加载敌人图像
        self.image = pygame.transform.scale(self.image, (100, 30))  # 调整图片大小
        self.rect = self.image.get_rect(center=(random.randint(0, width), random.randint(-100, -40))) 
        #random.randint(0, width): 生成一个从 0 到 width 的随机整数，表示矩形的水平中心位置 (x 坐标)，随机分布在屏幕宽度范围内。
        #random.randint(-100, -40): 生成一个从 -100 到 -40 的随机整数，表示矩形的垂直中心位置 (y 坐标)
        #出现在屏幕上方范围（屏幕看不到的区域），通常是为了实现物体从上方“掉落”的效果。
    def update(self):
        self.rect.y += 5 #  每次更新时，将矩形区域的y坐标增加5，即向下移动
        if self.rect.top > height: #  如果矩形区域的顶部大于屏幕高度，即完全移出屏幕下方，则从屏幕移除该对象
            self.kill()

# 创建精灵组
player = Player() #创建一个 Player 类的对象，代表玩家控制的角色（例如普通枪、散弹枪、火箭筒等）。
bullets_group = pygame.sprite.Group() #创建一个专门用于存放“子弹”精灵的组。所有由玩家或敌人发射出来的子弹对象（如 Rocket、Laser）会被加进这个组。
enemies_group = pygame.sprite.Group() # 创建一个用于存放敌人精灵的组。每次生成一个敌人，就加入这个组。在主循环中可以统一更新它们、绘制它们，甚至批量检测与子弹的碰撞。
all_sprites = pygame.sprite.Group() # 创建一个“万能组”，用于存放 所有出现在屏幕上的精灵。通常这个组会包含：player、敌人、子弹、爆炸动画 等。这样我们就可以一行代码：all_sprites.update() 来更新所有对象。
all_sprites.add(player) #将玩家加入到“万能组”中。这样玩家也会被统一更新和绘制。

# 游戏状态
running = True #  游戏是否正在运行
paused = False #  游戏是否暂停
score = 0 #  玩家得分

#游戏主循环初始化：
clock = pygame.time.Clock() #创建一个 Clock 对象，后面用它来控制循环的执行速度（帧率）。
while running: #这是整个游戏运行的核心循环，只要 running=True，这段代码就会不停执行，相当于游戏每一帧的逻辑和渲染。
    for event in pygame.event.get(): #遍历 Pygame 当前帧产生的所有事件（按键、鼠标、退出等等）
        if event.type == pygame.QUIT: #如果点击窗口关闭按钮，设置running为False，退出游戏循环
            running = False 
        elif event.type == pygame.KEYDOWN: #  如果事件类型是键盘按下事件
            if event.key == pygame.K_SPACE and not paused: #  如果按下的键是空格键且游戏未暂停
                player.fire()  # 玩家发射当前武器
                player.fire_message = "发射成功！"  # 并且提示发射成功
            elif event.key == pygame.K_p:  #按下 P 键切换游戏暂停状态。
                paused = not paused 
            elif event.key == pygame.K_r:  # 复活
                if player.hit_count >= 3: #如果玩家被击中次数达到3次，按 R 键可以重置游戏，恢复状态和提示。
                    player.reset_game() #  重置游戏
                    player.fire_message = "按下空格键射击"  # 重置提示
                    player.switch_message = "按下 W 切换武器"  #玩家按下 W 键时切换当前武器。
            elif event.key == pygame.K_w:  #玩家按下 W 键时切换当前武器。
                player.switch_weapon() #  调用玩家的切换武器方法
    
    #更新游戏状态（如果没暂停、也没结束）：
    if not paused and not player.is_game_over: #  如果游戏未暂停且玩家未游戏结束
        all_sprites.update() #  更新所有精灵的状态

        # 随机生成敌人
        if random.randint(1, 20) == 1: #  生成一个1到20之间的随机数，如果等于1则生成敌人
            enemy = Enemy() #  创建一个新的敌人对象
            all_sprites.add(enemy) #  将敌人添加到所有精灵组
            enemies_group.add(enemy) #  将敌人添加到敌人组

        #检测游戏中的子弹是否击中了敌人，如果发生碰撞，会移除子弹和敌人，并增加玩家得分
        for bullet in bullets_group: #  遍历子弹组中的每一颗子弹
            hits = pygame.sprite.spritecollide(bullet, enemies_group, True) 
            #pygame.sprite.spritecollide() 用于检测 bullet（子弹）是否与 enemies_group（敌人组）中的任何敌人碰撞。
            for hit in hits: #如果 hits 不为空，说明有敌人与子弹发生了碰撞。
                bullet.kill() #  当子弹击中敌人后，将其从 bullets_group 中移除，表示这颗子弹已经失效。
                score += 1 #  增加得分

        #这段代码的功能是检测玩家是否与任何敌人发生了碰撞，
        # 如果发生碰撞，就调用 player.respawn() 方法让玩家重新开始（重生）。
        if pygame.sprite.spritecollideany(player, enemies_group): #  检测玩家是否与任何敌人碰撞
            player.respawn() #  玩家重生

        #屏幕绘制
        screen.fill(black) #每一帧开始之前，用黑色背景“清空”屏幕，防止图像重叠残留。
        all_sprites.draw(screen) #把所有精灵（玩家、敌人、子弹等）绘制到屏幕上。all_sprites 是一个精灵组，它管理着游戏中所有需要渲染和更新的对象。

        # 显示得分和生命
        score_text = font.render(f'得分: {score}', True, white)  
        lives_text = font.render(f'生命: {player.lives}', True, white)  
        hit_count_text = font.render(f'击中次数: {player.hit_count}', True, white) 
        weapon_text = font.render(f'当前武器: {type(player.weapon).__name__}', True, white) 
        fire_text = font.render(player.fire_message, True, white)   #提示按空格键射击
        switch_text = font.render(player.switch_message, True, white)   #提示武器切换
        screen.blit(score_text, (10, 10)) 
        screen.blit(lives_text, (10, 40)) 
        screen.blit(hit_count_text, (10, 70)) 
        screen.blit(weapon_text, (10, 100)) 
        screen.blit(fire_text, (10, 130))  
        screen.blit(switch_text, (10, 160))  

        #font.render(...)	把一段字符串（比如“得分: 100”）变成可以画在屏幕上的“文字图像”
        #screen.blit(...)	把刚刚渲染出来的“文字图像”放在屏幕上，指定位置贴上去

    elif player.is_game_over:
        screen.fill(black) #  如果游戏结束，填充屏幕为黑色
        game_over_text = font.render('游戏结束!按R键重新开始', True, white) 
        #  使用字体对象font渲染游戏结束提示文本，文本颜色为白色
        screen.blit(game_over_text, (width // 2 - 200, height // 2)) 
        #  在屏幕中央绘制游戏结束提示文本，位置为(width // 2 - 200, height // 2)

    elif paused:
        screen.fill(black)
        pause_text = font.render('游戏暂停，按 P 继续', True, white) #  使用字体对象font渲染游戏暂停提示文本，文本颜色为白色
        screen.blit(pause_text, (width // 2 - 200, height // 2)) #  在屏幕中央绘制游戏暂停提示文本，位置为(width // 2 - 200, height // 2)
    
    #刷新屏幕和控制帧率
    pygame.display.flip() 
    #你前面画的所有内容（精灵、文字）其实都是画在一张“隐藏画布”里。这个 flip() 的作用就是：
    #“把隐藏的画布翻到屏幕前面”，就像你在画画，画完之后，把画纸翻过来给别人看。所以我们每一帧结束前，一定要调用它，才能让玩家看到画面更新。

    clock.tick(50) #控制游戏运行速度，避免游戏太快。它会让这一帧最多只能跑 1/50 秒，也就是每秒最多 50 帧。如果不加这个，你的游戏就会跑得飞快，甚至CPU占满、画面撕裂，非常不稳定。

#退出游戏
pygame.quit() #告诉 pygame：“我不玩了，帮我把所有窗口、声音、资源都释放掉”。
sys.exit() #告诉 整个 Python 程序：“我真的要退出了，彻底关闭”。
~~~

~~~sh
pyinstaller --onefile --windowed .\game.py 
~~~

# 俄罗斯方块游戏开发

~~~python
import pygame #  导入pygame库，用于游戏开发
import random #  导入random库，用于生成随机数

# 游戏窗口的宽度和高度
SCREEN_WIDTH = 300  # 游戏屏幕宽度（单位：像素）
SCREEN_HEIGHT = 600  # 游戏屏幕高度（单位：像素）
BLOCK_SIZE = 30  # 每个方块的大小（单位：像素）

# 定义颜色，使用 RGB 颜色模式
BLACK = (0, 0, 0)  # 黑色，用于背景色
WHITE = (255, 255, 255)  # 白色，用于方块的颜色
CYAN = (0, 255, 255)  # 青色，用于当前方块的颜色

#用二维数组定义五种俄罗斯方块的形状。
#什么是一维数组？
#一维数组（列表）：就像一排格子：[1, 2, 3]


#什么是二维数组？
#二维数组是列表的列表，就是“多行多列”的格子表格：
"""
[
 [1, 2, 3],
 [4, 5, 6]
]

外面是一个列表 [...]，里面每一行又是一个小列表。
每一行就是一个一维数组，多个一维数组排成“二维”的样子。
"""

SHAPES = [
    [[1, 1, 1, 1]],   # 一字形（I形）⬜⬜⬜⬜
    [[1, 1, 1], [0, 1, 0]],  # T形
#    ⬜⬜⬜
#      ⬜
    [[1, 1], [1, 1]],  # 方块（O形）
#    ⬜⬜
#    ⬜⬜
    [[0, 1, 1], [1, 1, 0]],   # Z形
#        ⬜⬜
#     ⬜⬜
    [[1, 1, 0], [0, 1, 1]]    # 反Z形（S形）
#    ⬜⬜
#       ⬜⬜
]

class Tetris:
    def __init__(self):
        pygame.init()  # 初始化pygame库，必须在使用任何 Pygame 功能前调用一次。
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 设置游戏窗口大小，并创建一个显示屏幕。
        pygame.display.set_caption("俄罗斯方块")  # 设置游戏窗口标题
        self.clock = pygame.time.Clock()  # 创建一个时钟对象 self.clock，用于控制游戏的帧率。比如可以通过 self.clock.tick(60) 控制每秒最多更新 60 次。
        self.running = True  #控制主循环是否继续运行。
        self.board = [[0 for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
        
        #这是一行嵌套列表推导式，用来创建一个**“二维网格”**（20行 × 10列），用 0 表示空格，组成俄罗斯方块的棋盘。
        """
        SCREEN_WIDTH = 300,SCREEN_HEIGHT = 600,BLOCK_SIZE = 30

        那么：
        横向格子数 = 300 // 30 = 10（每行10格）
        纵向格子数 = 600 // 30 = 20（共20行）

        第一步：先看内层
        [0 for _ in range(SCREEN_WIDTH // BLOCK_SIZE)]
        等价于：
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        生成一个包含 10 个 0 的列表
        表示棋盘中的一行，10 个空格位

        第二步：再看外层
        [[...内层... ] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]

         等价于：
        [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 第1行
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 第2行
        ...
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 第20行
        ]

        重复调用 内层列表 20 次 ⇒ 得到一个二维列表（20行 × 10列）
        每一行都是一个独立的 [0, 0, ..., 0]
        组成了棋盘初始状态，全是 0，表示“空”。

        为什么要这样写？
        俄罗斯方块的棋盘就是一个二维矩阵。
        每个方格要么是空的（0），要么有方块（1）。
        所以就需要一个二维列表 board[row][col] 来表示这个结构。

        """
        
        #初始化当前方块和下一个方块
        self.current_piece = self.new_piece()  #self.new_piece() 会从 SHAPES（预定义好的所有方块形状列表）中随机选一个返回
        self.next_piece = self.new_piece()  #self.current_piece 是当前下落的方块，而 self.next_piece 是等下一个出现的。

        #方块初始位置
        self.piece_x = SCREEN_WIDTH // BLOCK_SIZE // 2 - len(self.current_piece[0]) // 2  #让方块一开始出现在屏幕横向的正中央。
        """
        分解这句话：
        ① SCREEN_WIDTH // BLOCK_SIZE
        这是“整个屏幕一行可以容纳多少个格子”。
        比如：屏幕宽度 300 像素，每个格子 30 像素，则有 300 // 30 = 10 格子。
        → 所以整行有 10 个“格子”可以放方块。

        ② SCREEN_WIDTH // BLOCK_SIZE // 2
        这是中间格子的位置编号，也就是从左数到中间的位置。
        上面例子：10 个格子的一半是 5，第 5 格是中间位置。

        ③ len(self.current_piece[0])
         当前方块是个二维数组，如：
         SHAPES = [
         [[1, 1, 1, 1]],  
         [[1, 1, 1], [0, 1, 0]], 
         [[1, 1], [1, 1]],  
         [[0, 1, 1], [1, 1, 0]], 
         [[1, 1, 0], [0, 1, 1]]  
         ]

        self.current_piece[0] 是第一行 [1, 1, 1, 1]]。
        len(...) 得到的是“有几列”，也就是方块的宽度。
        上面这个例子，方块宽 4 格。

        ④ len(self.current_piece[0]) // 2
        方块的一半宽度（向左偏多少）。 

        所以整句的意思是：
       从屏幕中间位置出发，向左偏移“半个方块宽”，从而让方块整体正好居中。


        举个例子：

        假设：
        屏幕宽度 300 像素
        每个格子宽度 30 像素
        当前方块宽度是 4 格（比如 I 形：[[1, 1, 1, 1]]）

        那么：
        SCREEN_WIDTH // BLOCK_SIZE         = 10
        SCREEN_WIDTH // BLOCK_SIZE // 2   = 5 （中间是第5格）
        len(self.current_piece[0])        = 4
        len(...) // 2                     = 2

        最终：piece_x = 5 - 2 = 3

        → 这样这个 4 格宽的方块从第 3 列开始放：第 3、4、5、6 列刚好占满在正中间！
        """
        self.piece_y = 0  
        # 当前方块的垂直坐标位置（从顶部开始，在棋盘顶部）

        #下落速度控制变量
        self.fall_speed = 500  #意味着每 500 毫秒尝试让方块下降一次。
        self.last_fall_time = pygame.time.get_ticks() #把当前的“游戏运行时间”记录下来，存在变量 self.last_fall_time 里。记住现在这个时刻，作为上一次下落的时间点
        
        #游戏得分
        self.score = 0  # 游戏的初始分数

    def new_piece(self):
        # 随机生成一个俄罗斯方块形状
        return random.choice(SHAPES)

    def draw_board(self):
        #绘制俄罗斯方块游戏的界面，主要包括棋盘、当前下落的方块以及分数显示
        self.screen.fill(BLACK)  #这行代码用黑色填充整个屏幕背景，表示游戏的背景颜色为黑色。
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.board[y][x]:  # 如果当前位置有方块
                    pygame.draw.rect(self.screen, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))  # 画一个白色的方块

        """
        代码详细解释：
        for y in range(len(self.board)):
        # 遍历每一行的编号，假设有 20 行，这里 y 就从 0 到 19。
        # y 是行号，也可以理解为“高度”或“纵向”。
        
        for x in range(len(self.board[y])):
        
        # 在每一行里，再去遍历每一列的编号。
        # 比如每行有 10 列，那 x 就是 0 到 9。
        # x 是列号，也就是“水平方向”。

        if self.board[y][x]:      
        #  如果这个格子是 1（非零），说明这里有方块。那就绘制方块
        pygame.draw.rect(self.screen, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        #这一行才是真正画方块的部分。pygame.draw.rect 是在屏幕上画一个矩形（就是方块）。

        参数：
        self.screen：在哪个屏幕上画。
        WHITE：方块的颜色是白色。
        举例说明：
        如果我们画的是第2行（y=2），第3列（x=3）的一个方块：
        横向坐标 = x * BLOCK_SIZE = 3 * 30 = 90 像素
        纵向坐标 = y * BLOCK_SIZE = 2 * 30 = 60 像素
        所以这个方块会显示在 屏幕左上角往右偏移 90 像素，下偏移 60 像素的位置，占据一个 30x30 像素的正方形区域。
     
        """

        # 绘制当前正在下落的方块
        for y in range(len(self.current_piece)): #  遍历当前正在下落的方块（self.current_piece）的每一行
            for x in range(len(self.current_piece[y])):
                if self.current_piece[y][x]:  # 如果当前方块位置有方块
                    pygame.draw.rect(self.screen, CYAN, ((self.piece_x + x) * BLOCK_SIZE, (self.piece_y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))  
                    # 画一个青色的方块


        # 显示分数
        font = pygame.font.Font(None, 36)  # 创建一个字体对象，字体大小为36
        score_text = font.render(f'Score: {self.score}', True, WHITE)  # 渲染文本（分数）
        self.screen.blit(score_text, (10, 10))  # 在屏幕上绘制分数文本

        pygame.display.flip()  # 更新显示，刷新屏幕

    def run(self):
        # 游戏主循环
        while self.running:
            self.handle_events()  # 处理用户输入
            self.update()  # 更新游戏状态
            self.draw_board()  # 绘制游戏界面
            pygame.display.flip()  # 更新显示
            self.clock.tick(30)  # 每秒30帧

    def handle_events(self):
        # 处理用户输入的所有事件，检测键盘输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False  # 用户点击关闭窗口，退出游戏
            elif event.type == pygame.KEYDOWN:  # 如果按下了键盘键
                if event.key == pygame.K_LEFT:  # 按左键向左移动一个格
                    self.piece_x -= 1
                    if self.collision():  # 检查碰撞
                        self.piece_x += 1  # 如果碰撞，撤销移动
                elif event.key == pygame.K_RIGHT:  # 右键移动
                    self.piece_x += 1
                    if self.collision():  # 检查碰撞
                        self.piece_x -= 1  # 如果碰撞，撤销移动
                elif event.key == pygame.K_DOWN:  # 下键加速下落
                    self.piece_y += 1
                    if self.collision():  # 检查碰撞
                        self.piece_y -= 1  # 如果碰撞，撤销移动
                elif event.key == pygame.K_UP:  # 上键旋转方块
                    self.current_piece = self.rotate(self.current_piece)  # 顺时针旋转方块
                    if self.collision():  # 检查碰撞
                        self.current_piece = self.rotate(self.current_piece, -1)  # 如果碰撞，逆时针旋转回去

    def rotate(self, piece, direction=1):
        #这是一个方法，叫做 rotate，用来旋转方块。
        """
        piece 是你当前的方块（一个二维列表，例如 O 形、T 形等）
        direction 是旋转方向，默认为 1（顺时针）：
        1 表示顺时针旋转
        -1 表示逆时针旋转
        """

        if direction == 1:
            # 顺时针旋转：将方块转置并反转每行
            return [list(row) for row in zip(*piece[::-1])]
            """
            这一行做了两个动作：

            第一步：piece[::-1]
            把原来的二维数组上下翻转
            这是准备做转置的一部分

            第二步：zip(*...)
            zip(*列表) 会把行变成列（也就是矩阵“转置”）

            第三步：[list(row) for row in zip(...)]
            把 zip 生成的每一行再变成 list，变成一个新的二维数组

            举个例子：
            原始方块（2x2）：
            [
            [1, 0],
            [1, 1]
            ]

            上下翻转后（piece[::-1])：
            [
            [1, 1],
            [1, 0]
            ]

            转置后：
            [
            [1, 1],
            [1, 0]
            ]
            ==> 变成
            [
            [1, 1],
            [1, 0]
            ]
           其实这个例子转出来长得差不多，但对于 T 形、L 形等效果就很明显。
            """
        else:
            # 逆时针旋转：转置后不反转
            return [list(row) for row in zip(*piece)][::-1]
            """
            这句和上面差不多，只不过：

            顺序变成：
            先转置
            然后再左右翻转（整个二维数组上下反转）

            假设原来是：
            [
            [1, 0],
            [1, 1]
            ]

             zip 转置 ➜
            [
            [1, 1],
            [0, 1]
            ]

            再整体上下翻转 ➜
            [
            [0, 1],
            [1, 1]
            ]
            """

    def update(self):
        #定义update函数，更新方块的状态，特别是负责让方块不断向下移动，并在适当时候生成新方块。

        #获取当前时间
        self.fall_time = pygame.time.get_ticks()  
        #pygame.time.get_ticks() 获取自 Pygame 初始化以来的毫秒数（当前时间）,
        #用 self.fall_time 存储这个时间戳，表示方块下落的当前时间。
        
        #控制方块下落速度：
        if self.fall_time - self.last_fall_time > self.fall_speed: 
            """
            这行代码用于控制方块下落的速度。
            self.last_fall_time 是方块上次下落的时间。
            self.fall_speed 是设定的下落速度（单位：毫秒），比如每 500 毫秒方块下落一次。
            通过比较 self.fall_time - self.last_fall_time 和 self.fall_speed，判断是否已经超过了设定的下落时间。
            """
            self.piece_y += 1  #如果时间到了，就让方块向下移动一格。每次下落一步，self.piece_y 会增加 1。
            #碰撞检测：
            if self.collision():  # 如果发生碰撞
                """
                self.collision() 是一个方法，用来检查方块是否和其他已经存在的方块、墙壁等发生了碰撞。
                如果检测到碰撞（比如方块已经堆积到最底部或碰到其他方块），就会执行接下来的操作。
                """
                self.piece_y -= 1  # 撤销下落
                self.lock_piece()  #当前方块锁定到棋盘上，这样它就成为了棋盘的一部分，不能再移动了。
                self.clear_lines()  #用来清除已填满的行，即消除那些已经被填满的整行，让上方的方块掉下来。
                self.current_piece = self.next_piece  #把下一个方块设置为当前方块。
                self.next_piece = self.new_piece()  #生成一个新的下一个方块（即随机生成一个新的方块）
                self.piece_x = SCREEN_WIDTH // BLOCK_SIZE // 2 - len(self.current_piece[0]) // 2
                #self.piece_x：把方块的横坐标重置到屏幕的中间，SCREEN_WIDTH // BLOCK_SIZE // 2 会将其设置为屏幕宽度的中间。
                self.piece_y = 0  # 重置方块Y坐标
                #self.piece_y = 0：把方块的纵坐标设置为 0，即从屏幕的顶部开始下落。
                if self.collision():  # 如果方块再碰撞，running设置成false，表示游戏结束
                    self.running = False
            self.last_fall_time = self.fall_time  
            #最后更新 self.last_fall_time 为当前时间（self.fall_time），这样下一次下落的判断就会有正确的时间间隔。

    def collision(self):
        """检查当前方块是否与棋盘上的其他方块发生碰撞"""
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[y])):
                if self.current_piece[y][x]:  # 如果当前位置有方块
                    board_x = self.piece_x + x  # 计算方块X坐标
                    board_y = self.piece_y + y  # 计算方块Y坐标
                    # 检查是否超出棋盘边界或者与已有方块发生碰撞
                    if board_x < 0 or board_x >= SCREEN_WIDTH // BLOCK_SIZE or board_y >= SCREEN_HEIGHT // BLOCK_SIZE or self.board[board_y][board_x]:
                        return True  # 如果发生碰撞，返回True
        return False  # 如果没有碰撞，返回False

    def lock_piece(self):
        """将当前方块锁定到棋盘上"""
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[y])):
                if self.current_piece[y][x]:
                    self.board[self.piece_y + y][self.piece_x + x] = 1  # 将方块添加到棋盘

    def clear_lines(self):
        """清除已填满的行并更新分数"""
        for y in range(len(self.board) - 1, -1, -1):
            if all(self.board[y]):
                self.score += 100  # 每清除一行加100分
                del self.board[y]  # 删除该行
                self.board.insert(0, [0 for _ in range(SCREEN_WIDTH // BLOCK_SIZE)])  # 在顶部插入一个空行


# 创建并运行游戏
game = Tetris()
game.run()
pygame.quit()
~~~

