'''
遊戲主程式。
'''

import pygame
import threading # 多線程 模組
import sys
import os # 用於創建文件夾 處理文件路徑
import time
import pyautogui
import filetype # 檢視文件類型
from PIL import Image # 用於打開/讀取/保存圖片
from random import randint
from random import uniform


'''==========『角色物件』=========='''
class Character(pygame.sprite.Sprite):
    '''『初始化』'''
    def __init__(self, num, zoom, lv, ATK_growing, DEF_growing, HP_growing, ATK, DEF, HP, LUK, SPD, left, top):
        pygame.sprite.Sprite.__init__(self)

        '''角色基本屬性'''
        self.num = num # 角色編號
        self.zoom = zoom # 是否倍化
        # 動作編號
        if self.num == 35:
            self.act = 9
        else:
            self.act = 5

        '''角色等級屬性'''
        self.lv = lv # 等級
        self.exp = 0 # 現有經驗值
        self.lvup_exp = 100 # 升級所需經驗值
        self.give_exp = 50 # 被擊倒給予經驗值
        self.ab_point = 0 # 未使用能力點數

        '''角色成長率'''
        self.ATK_growing = ATK_growing 
        self.DEF_growing = DEF_growing
        self.HP_growing = HP_growing

        '''角色能力屬性'''
        self.ATK = ATK # 攻擊力
        self.DEF = DEF # 防禦力
        self.HP = HP # 體質

        self.LUK = LUK # 運氣：提高爆擊(傷害1.5倍)機率，1 = 1%
        self.SPD = SPD # 移動速度

        self.maxHP = self.HP * 5 # 總血量
        self.nowHP = self.maxHP # 目前剩餘血量

        '''角色移動屬性'''
        self.key_pressed = pygame.key.get_pressed()
        self.frame = 0 # 幀計數

        '''動畫屬性'''
        # 動畫dict：以images[動作索引][方位索引]取對應list。動作方位編號為由下(0)開始，以45度角(1)遞增。
        self.images = {"atk":{"0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": []},
                        "dead":{"0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": []},
                        "stand":{"0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": []},
                        "walk":{"0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": []},
                        }

        self.motion = "stand" # 動作索引
        self.direction = "0" # 方向索引
        self.index = 0 # 幀數索引
        self.image = pygame.image.load("imgs/35_1/35_1_0.png").convert()
        self.rect = self.image.get_rect() # 矩形大小
        self.rect.center = (left, top) # 初始位置
        self.move_x = 0 # 寵物移動量
        self.move_y = 0 # 寵物移動量
        self.original_left = self.rect.left # 出生座標
        self.original_top = self.rect.top # 出生座標

        # 存入所有動畫幀至images
        load_gif(self.num, self.zoom, self.images, self.rect)

        '''開關屬性'''
        self.is_move = False # 寵物是否正在移動
        self.invincible = True # 是否為無敵狀態
        self.invincible_reciprocal = 180 # 無敵倒數計時 1秒為60單位
        self.atk_count = 2 # 寵物攻擊動畫計數 (因動畫過短故播放2次)
    
    
    '''『角色移動動畫』：實作動畫。'''
    def charcter_updata(self):
        if self.motion == "atk":
            if self.num == 35:
                self.image = self.images[self.motion][self.direction] # image = 當前[動作][方位]幀數
                screen.blit(self.image[self.index], (self.rect.left, self.rect.top))
                self.index += 1

                if self.index == len(self.images[self.motion][self.direction]) - 1:
                    self.motion = "stand"

        elif self.motion == "dead":
            if self.num == 35:
                if self.index != len(self.images[self.motion][self.direction]) - 1: # 如果動畫未放到最後一幀
                    self.image = self.images[self.motion][self.direction] # image = 當前[動作][方位]幀數
                    screen.blit(self.image[self.index], (self.rect.left, self.rect.top))
                    self.index += 1
                else:
                    screen.blit(self.image[self.index], (self.rect.left, self.rect.top)) # 動畫等於最後一幀

        else:    
            # 當前幀數索引值大於該動畫list總幀數則歸零
            if self.index > len(self.images[self.motion][self.direction]) - 1:
                self.index = 0
            self.image = self.images[self.motion][self.direction] # image = 當前[動作][方位]幀數
            screen.blit(self.image[self.index], (self.rect.left, self.rect.top))
            self.index += 1
            if self.motion == "walk":
                self.move()
            

    '''『角色矩陣位置刷新』：更新圖片矩陣位置並替換walk動畫方位。'''
    def move(self):
        if self.num == 35: # 玩家
            # 向上走
            if self.direction == "4":
                if self.rect.top > 0:
                    self.rect.top -= self.SPD
            # 向下走
            elif self.direction == "0":
                if self.rect.top < screenSize_y - self.rect.height:
                    self.rect.top += self.SPD
            # 向左走
            elif self.direction == "2":
                if self.rect.left > 0:
                    self.rect.left -= self.SPD
            # 向右走
            elif self.direction == "6":
                if self.rect.left <  screenSize_x - self.rect.width:
                    self.rect.left += self.SPD
        else: # 寵物
                # 向右走
                if self.direction == "6":
                    if self.rect.left + self.SPD < screenSize_x - self.rect.width and self.move_x > 0:
                        self.rect.left += self.SPD
                        self.move_x -= self.SPD
                    else :
                        self.move_x = 0                      

                    if self.move_x < 0:
                        self.move_x = 0
                    
                # 向左走
                elif self.direction == "2":
                    if self.rect.left - self.SPD > 0 and self.move_x < 0:
                        self.rect.left -= self.SPD
                        self.move_x += self.SPD
                    else :
                        self.move_x = 0                      

                    if self.move_x > 0:
                        self.move_x = 0

                # 向下走
                elif self.direction == "0"  :
                    if self.rect.top + self.SPD < screenSize_y - self.rect.height and self.move_y > 0:                  
                        self.rect.top += self.SPD
                        self.move_y -= self.SPD
                    else :
                        self.move_y = 0                        

                    if self.move_y < 0:
                        self.move_y = 0

                # 向上走
                elif self.direction == "4" :
                    if self.rect.top - self.SPD > 0 and self.move_y < 0:
                        self.rect.top -= self.SPD
                        self.move_y += self.SPD
                    else :
                        self.move_y = 0

                    if self.move_y > 0:
                        self.move_y = 0


                if self.move_x == 0 and self.move_y == 0:
                        self.is_move = False
                        self.motion = "stand"



'''==========『武器物件』=========='''
class Weapon(pygame.sprite.Sprite):
    def __init__(self, left, top):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("arrow.png").convert_alpha()
        self.rect = self.image.get_rect() # 矩形大小
        self.rect.center = (left, top) # 初始位置
        self.SPD = 20
        self.move_x = 0 # 武器移動量
        self.move_y = 0 # 武器移動量
        self.direction = "0"

        #self.collideRect = pygame.rect.Rect((self.rect.left, self.rect.top), (self.rect.left + 30, self.rect.left - 20))

    def __del__(self):
        print("武器已解構。")

    def move(self):
        # 左
        if self.direction == "2" and self.move_x < 0:
            self.rect.left -= self.SPD
            self.collideRect = pygame.rect.Rect((self.rect.left - self.SPD, self.rect.top), (self.rect.left + 30 - self.SPD, self.rect.left - 20))
            self.move_x += self.SPD
            screen.blit(self.image, (self.rect.left, self.rect.top + 40))
            if self.move_x >= 0:
                self.move_x = 0
        # 右        
        if self.direction == "6" and self.move_x > 0:
            self.rect.left += self.SPD
            self.collideRect = pygame.rect.Rect((self.rect.left + self.SPD, self.rect.top), (self.rect.left + 30 + self.SPD, self.rect.left - 20))
            self.move_x -= self.SPD
            screen.blit(self.image, (self.rect.left, self.rect.top + 40))
            if self.move_x <= 0:
                self.move_x = 0
        # 上
        if self.direction == "4" and self.move_y < 0:
            self.rect.top -= self.SPD
            self.collideRect = pygame.rect.Rect((self.rect.left, self.rect.top - self.SPD), (self.rect.left + 30, self.rect.left - 20  - self.SPD))
            self.move_y += self.SPD
            screen.blit(self.image, (self.rect.left + 20, self.rect.top))
            if self.move_y >= 0:
                self.move_y = 0
        # 下
        if self.direction == "0" and self.move_y > 0:
            self.rect.top += self.SPD
            self.collideRect = pygame.rect.Rect((self.rect.left, self.rect.top + self.SPD), (self.rect.left + 30, self.rect.left - 20  + self.SPD))
            self.move_y -= self.SPD
            screen.blit(self.image, (self.rect.left + 50, self.rect.top))
            if self.move_y <= 0:
                self.move_y = 0

        
        


'''『GIF動態圖片分割器』：將每個gif檔案夾下動圖分割成png(內含去背程式碼)。'''
def GIFSpliter(gif_path:str):
    # 判斷gif圖像是否存在
    if not os.path.exists(gif_path):
        print("gif路徑錯誤或不存在")
        return

    # 根據文件名創建輸出目錄
    # 取得不帶目錄與副檔名的檔名 當作輸出目錄名
    gif_filename = os.path.split(gif_path)[1] # 可將路徑切割為[目錄, 檔名.副檔名]
    filename = os.path.splitext(gif_filename)[0] # splittext() 將檔名切割為[檔名, 副檔名]
    path_home = "imgs/"
    output_floder = os.path.join(path_home, filename) # 輸出目錄變數
    if not os.path.exists(output_floder):
        os.makedirs(output_floder) # 創建輸出目錄

    gif_obj = Image.open(gif_path) # 打開gif圖像 為PIL.Image.Image資料型態物件 模式為RGB

    # 循環讀取每一幀圖像
    frame_num = 0
    while True:
        try: # 異常處理
            gif_obj.seek(frame_num) # 將圖片定位到指定幀
        except EOFError: # 若到達文件末尾則跳出
            break 
        gif_obj.seek(frame_num) # 將圖片定位到指定幀         
        # BW_BG_Transparency(gif_obj)
        gif_obj.save(os.path.join(output_floder, "{0}_{1}".format(filename, frame_num) + ".png")) # 將當前幀輸出至輸出目錄
        # 『去背API』(需付費)
        # rmbg = RemoveBg("your_key", "error.log") 
        # rmbg.remove_background_from_img_file(png_path)
        
        image = Image.open(output_floder + "/" + "{0}_{1}".format(filename, frame_num) + ".png")
        image = image.convert("RGBA") # 轉成具alpha(透明度參數)的模式
        newImage = []
        for item in image.getdata():
            if item[:3] == (255, 255, 255):
                newImage.append((255, 255, 255, 0))

            elif item[:3] == (0, 0, 0):
                newImage.append((0, 0, 0, 0))

            elif item[:3] == (20, 20, 20):
                newImage.append((20, 20, 20, 0))

            else:
                newImage.append(item)

        image.putdata(newImage)
        image.save(output_floder + "/" + "{0}_{1}".format(filename, frame_num) + ".png")
        
        frame_num += 1 # 指向下一號

    print("共輸出{0}張圖片".format(frame_num)) # 提示完成


'''『GIF讀檔分割器』：讀入每個gif檔案夾，利用GIFSpliter()將每個gif檔案夾下動圖分割成PNG。'''
def split_gif():
    gif_pathf = "gif/{0}/{1}" # 格式化路徑
    dirList = os.listdir("gif/") # 將指定路徑下所有檔名(包括資料夾)存成list

    for dir in dirList:
        if os.path.isdir(os.path.join("gif/", dir)): # 如果該路徑為資料夾
            for gifDir in dir:
                gifList = os.listdir("gif/" + dir + "/")
                for gif in gifList:
                    if os.path.isfile("gif/" + dir + "/" + gif): # 如果該路徑為檔案
                        gif_path = gif_pathf.format(dir, gif)
                        GIFSpliter(gif_path) # 將gif依幀切割成png                     
        else:
            print("Error!That isn't a directory!")


'''『GIF幀加載器』：將分割後之png加載儲存為list存入物件images屬性。'''
def load_gif(num, zoom, images, rect):   
    act_list = []
    pngList = []

    '''存入八方位動作編碼list'''
    if num == 35:
        # atk
        act = 1
        act_list.append(act)
        for i in range(7):
            act += 13
            act_list.append(act)
        # dead
        act = 3
        act_list.append(act)
        for i in range(7):
            act += 13
            act_list.append(act)
        # stand
        act = 9
        act_list.append(act)
        for i in range(7):
            act += 13
            act_list.append(act)
        # walk
        act = 12
        act_list.append(act)
        for i in range(7):
            act += 13
            act_list.append(act)                
    else:
        # atk
        act = 1
        act_list.append(act)
        for i in range(7):
            act += 7
            act_list.append(act)
        # dead
        act = 2
        act_list.append(act)
        for i in range(7):
            act += 7
            act_list.append(act)
        # stand
        act = 5
        act_list.append(act)
        for i in range(7):
            act += 7
            act_list.append(act)
        # walk
        act = 6
        act_list.append(act)
        for i in range(7):
            act += 7
            act_list.append(act) 

    '''提取動作編碼(act_list)'''
    count = 0
    for i in range(len(act_list)):
        act = act_list[i] # 依序取出動作編碼
        png_pathf = "imgs/" + str(num) + "_" + str(act) # 指定gif幀資料夾路徑
        if not os.path.exists(png_pathf): # 偵錯
            print(str(png_pathf) + "路徑錯誤或不存在")
        
        pngList = os.listdir(png_pathf.format(num, act)) # 取指定資料夾內文件與資料夾名字之list
        for png in pngList:
            if os.path.isfile(png_pathf.format(num, act) + "/" + png): # 如果該路徑為檔案
                png_path = png_pathf.format(num, act) + "/" + png
                if zoom: # 檢查是否需倍化
                    character = pygame.image.load(png_path) # 依序依list檔名路徑讀圖
                    character = pygame.transform.scale2x(character).convert_alpha() # 圖檔倍化
                    character.set_colorkey((15, 0, 2)) # 指定去背RGB
                else:
                    character = pygame.image.load(png_path).convert_alpha() # convert_alpha() 讀入透明度(RGB'A'的第四維)
                    character.set_colorkey((15, 0, 2)) # 指定去背RGB
                    
                    
                '''
                動作8個方向為一組(count <= 8)，分別存入images dict內。
                依『images[動作索引][方向索引]』存取動作list。
                '''
                if i <= 7:
                    images["atk"][str(count)].append(character)
                    image = character
                    rect  = image.get_rect()                                
                elif i <= 15:
                    images["dead"][str(count)].append(character)
                    image = character
                    rect  = image.get_rect()                                
                elif i <= 23:
                    images["stand"][str(count)].append(character)
                    image = character
                    rect  = image.get_rect()                                
                elif i <= 31:
                    images["walk"][str(count)].append(character)
                    image = character
                    rect  = image.get_rect()
            else:
                print("gif幀加載入物件屬性images失敗")

        count += 1
        if count >= 8:
            count = 0


'''『寵物動畫』'''
def creat_motion(character_name):
    for name in character_name:
        creator = character_dic[name]
        if creator.motion != "dead":
            switch = randint(1,20) # 是否移動之開關
            if creator.motion != "atk":
                if creator.is_move == False:
                    if switch == 1: # 移動動畫
                        creator.motion = "walk"
                    else: # 待機動畫
                        creator.motion = "stand"

            # 待機動畫
            if creator.motion == "stand":
                if creator.index > len(creator.images[creator.motion][creator.direction]) - 1:
                    creator.index = 0
                creator.image = creator.images[creator.motion][creator.direction] # image = 當前[動作][方位]幀數
                screen.blit(creator.image[creator.index], (creator.rect.left, creator.rect.top))
                creator.index += 1

            # 走路動畫
            elif creator.motion == "walk":
                if creator.is_move == True:
                    if creator.move_x > 0:
                        creator.direction = "6"
                    elif creator.move_x < 0:
                        creator.direction = "2"
                    elif creator.move_y > 0:
                        creator.direction = "0"
                    elif creator.move_y < 0:
                        creator.direction = "4"
                    elif creator.move_x == 0 and creator.move_y == 0:
                        creator.motion ="stand"

                    if creator.index > len(creator.images[creator.motion][creator.direction]) - 1:
                        creator.index = 0
                    creator.image = creator.images[creator.motion][creator.direction] # image = 當前[動作][方位]幀數
                    screen.blit(creator.image[creator.index], (creator.rect.left, creator.rect.top))
                    creator.index += 1
                    creator.move()
                elif creator.is_move == False:
                    creator.is_move = True
                    x = randint(-100, 100) # 隨機移動量
                    y = randint(-100 ,100)
                    creator.move_x += x # 目標地left
                    creator.move_y += y
                    
                    if creator.move_x > 0:
                        creator.direction = "6"
                    elif creator.move_x < 0:
                        creator.direction = "2"
                    elif creator.move_y > 0:
                        creator.direction = "0"
                    elif creator.move_y < 0:
                        creator.direction = "4"
                    else: 
                        creator.motion = "stand"
                    # 當前幀數索引值大於該動畫list總幀數則歸零
                    if creator.index > len(creator.images[creator.motion][creator.direction]) - 1:
                        creator.index = 0
                    creator.image = creator.images[creator.motion][creator.direction] # image = 當前[動作][方位]幀數
                    screen.blit(creator.image[creator.index], (creator.rect.left, creator.rect.top))
                    creator.index += 1
                    creator.move()

            # 攻擊動畫
            elif creator.motion == "atk":
                if creator.atk_count != 0:
                    if creator.index > len(creator.images[creator.motion][creator.direction]) - 1: # 如果為最後一幀
                        creator.index = 0
                        creator.atk_count -= 1 # 播放次數-1
                    creator.image = creator.images[creator.motion][creator.direction] # image = 當前[動作][方位]幀數
                    screen.blit(creator.image[creator.index], (creator.rect.left, creator.rect.top))
                    creator.index += 1
                else:
                    creator.atk_count = 2 # 播放次數回復成2次
                    creator.motion = "stand" # 攻擊完回復待機狀態
                    creator.is_move = False # 強制待機 重新判定是否移動
                    creator.move_x = 0 # 原移動量清0
                    creator.move_y = 0 # 原移動量清0
                    screen.blit(creator.image[creator.index], (creator.rect.left, creator.rect.top))
        
        # 死亡動畫
        elif creator.motion == "dead":
            if creator.index != len(creator.images[creator.motion][creator.direction]) - 1: # 如果動畫未放到最後一幀
                creator.image = creator.images[creator.motion][creator.direction] # image = 當前[動作][方位]幀數
                screen.blit(creator.image[creator.index], (creator.rect.left, creator.rect.top))
                creator.index += 1
            else:
                screen.blit(creator.image[creator.index], (creator.rect.left, creator.rect.top)) # 動畫等於最後一幀


'''『寵物物件生成』'''
def creat(num, zoom, qty, lv, ATK_growing, DEF_growing, HP_growing, ATK, DEF, SPD, HP, LUK):

    xy_demo = "xy_" + str(num)
    name = "creator{0}_{1}"
    for i in range(1, qty + 1):
        # 隨機座標誤差值值
        ran_x = randint(-250,250)
        ran_y = randint(-250,250)
        x, y = xy_dict[xy_demo]
        left = x + ran_x
        top = y + ran_y
        if top < 0:
            top = ran_y
        if top > screenSize_y:
            top = screenSize_y
        if left > screenSize_x:
            left = screenSize_x
        if left < 0:
            left = ran_x

        # 創建寵物物件
        # num, zoom, lv, ATK_growing, DEF_growing, HP_growing, ATK, DEF, HP, LUK, SPD, left, top
        character = Character(num, zoom, lv, ATK_growing, DEF_growing, HP_growing, ATK, DEF, HP, LUK, SPD, left, top)
        character_dic[name.format(num, i)] = character # 儲存物件進dict
        character_name.append(name.format(num, i)) # 儲存名稱當character_dic的key

if __name__ == "__main__":
    '''分割並載入gif資源'''
    if not os.path.exists("imgs/"): # 若已分割gif資源(路徑/資料夾)不存在 則執行分割
        split_gif()

    '''初始化介面'''
    pygame.init() # 初始化導入 pygame 模組
    screenSize_x, screenSize_y = pyautogui.size()
    screen = pygame.display.set_mode(pyautogui.size()) # 設定尺寸並顯示視窗 pyautogui.size()取得當前螢幕解析度
    pygame.display.set_caption("StoneAge") # 設置視窗標題
    screen.fill((0, 0, 0)) # 填滿顏色(rgb)
    bg_img = pygame.image.load("bg/bg.png") # 背景

    character_dic = locals() # 儲存寵物物件
    character_name = list() # 儲存寵物物件索引值
    weapon_list = list() # 儲存武器物件


    '''BGM'''
    pygame.mixer.init() # 初始化
    pygame.mixer.music.set_endevent(pygame.constants.USEREVENT) # 設置音樂結束事件
    normal_music = "bgm/normal.mp3"
    battle_music = "bgm/battle.mp3"
    sad_music = "bgm/sad.mp3"
    final_battle_music = "bgm/final_battle.mp3"

    music = normal_music
    pygame.mixer.music.load(music)
    pygame.mixer.music.play()

    '''音效'''
    # 玩家受傷
    player_hurt = pygame.mixer.Sound("bgm/player_hurt.mp3")
    player_hurt.set_volume(1) # 音量調整(0.1~1)
    # 玩家受爆擊
    player_hurt_more = pygame.mixer.Sound("bgm/player_hurt_more.mp3")
    player_hurt.set_volume(1) # 音量調整(0.1~1)

    '''玩家創建'''
    # num, zoom, lv, ATK_growing, DEF_growing, HP_growing, ATK, DEF, HP, LUK, SPD, left, top
    player = Character(35, False, 1, 0, 0, 0, 15, 5, 10, 0, 10, 800, 500)
    weapon_group = pygame.sprite.Group() # 武器群組
    

    '''寵物初始座標'''
    xy_dict = {"xy_244" : (1800, 200), # 烏力烏力
            "xy_247" : (1300, 500), # 布依
            "xy_265" : (700, 200), # 石龜
            "xy_250" : (300, 500), # 加美
            "xy_312" : (700, 700), # 加格
            "xy_670" : (1700, 600), # 塔斯夫
            "xy_325" : (1200, 700), # 斯天多斯
            "xy_302" : (700, 700), # 貝魯卡
            "xy_672" : (500 , 800)} # 班尼迪克

    '''寵物創建'''
    # num, zoom, qty, lv, ATK_growing, DEF_growing, HP_growing, ATK, DEF, SPD, HP, LUK
    creat(244, False, 5, 1, 1, 2, 2, 10, 5, 3, 10, 10) # 烏力烏力  
    creat(247, False, 3, 1, 1, 2, 3, 10, 5, 3, 11, 20) # 布依
    creat(265, False, 3, 1, 1, 3, 2, 10, 7, 1, 10, 10) # 石龜
    creat(250, False, 3, 1, 2, 2, 2, 13, 5, 15, 10, 20) # 加美
    creat(312, False, 3, 1, 3, 2, 2, 13, 6, 5, 10, 40) # 加格
    creat(670, False, 4, 1, 3, 2, 2, 13, 6, 12, 11, 20) # 塔斯夫
    creat(325, False, 2, 1, 3, 3, 3, 12, 8, 3, 12, 40) # 斯天多斯
    creat(302, False, 2, 1, 5, 2, 3, 16, 6, 8, 11, 50) # 貝魯卡
    creat(672, True, 1, 1, 6, 4, 3, 18, 7, 8, 12, 60) # 班尼迪克


clock = pygame.time.Clock() # 計時物件
while True:
    clock.tick(60) # 每秒執行次數
    screen.blit(bg_img,(0,0))
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if player.motion != "dead": # 如果玩家為未死亡狀態
            '''走路監測'''
            if  event.type == pygame.KEYDOWN:
                # 向上走
                if event.key == pygame.K_UP:
                    player.direction = "4"
                    player.motion = "walk"
                # 向下走    
                elif event.key == pygame.K_DOWN:
                    player.direction = "0"
                    player.motion = "walk"
                # 向左走    
                elif event.key == pygame.K_LEFT:
                    player.direction = "2"
                    player.motion = "walk"
                # 向右走
                elif event.key == pygame.K_RIGHT:
                    player.direction = "6"
                    player.motion = "walk"

                '''攻擊監測'''
                if event.key == pygame.K_SPACE:
                    weapon = Weapon(player.rect.left, player.rect.top) # 建立武器物件
                    # 向左攻擊
                    if player.direction == "2":
                        weapon.move_x = -500
                    # 向右攻擊
                    elif player.direction == "6":
                        weapon.move_x = 500
                    # 向上攻擊
                    elif player.direction == "4":
                        weapon.move_y = -500
                    # 向下攻擊
                    elif player.direction == "0":
                        weapon.move_y = 500

                    '''轉換圖片(武器)角度：負數為順時針。'''
                    # 上
                    if player.direction == "4":
                        weapon.image = pygame.transform.rotate(weapon.image, -90)
                    # 右
                    elif player.direction == "6":
                        weapon.image = pygame.transform.rotate(weapon.image, -180)
                    # 下
                    elif player.direction == "0":
                        weapon.image = pygame.transform.rotate(weapon.image, -270)

                    weapon.direction = player.direction
                    player.motion = "atk"
                    player.index = 0
                    weapon_list.append(weapon)
                    weapon_group.add(weapon)

            '''待機監測'''
            if event.type == pygame.KEYUP and player.motion == "walk":
                player.motion = "stand"

            '''音樂播完再次執行'''
            if event.type == pygame.constants.USEREVENT:
                pygame.mixer.music.play()


    '''        
    key_p = pygame.key.get_pressed() # 取得按鍵當前狀態
    if key_p[pygame.K_UP] or key_p[pygame.K_DOWN] or key_p[pygame.K_LEFT] or key_p[pygame.K_RIGHT]:
        player.charcter_updata()
    '''

    '''玩家復活與無敵判定'''
    if player.motion == "dead":
        if player.invincible_reciprocal > 0: # 如果有無敵秒數則進入檢測
            player.invincible_reciprocal -= 1 # 扣減1單位 60單位為1秒
        if player.invincible_reciprocal <= 300: # 如果秒數耗盡
            music = normal_music
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music) # 更換為平時音樂
            pygame.mixer.music.play()      
            player.motion = "stand" # 復活
            player.nowHP = player.maxHP

            # 作為死亡懲罰 exp清0 全場寵物生命值回滿
            player.exp = 0
            for name in character_name:
                creator = character_dic[name]
                if creator.motion != "dead":
                    creator.nowHP = creator.maxHP
            print("復活！無敵開啟5秒。")
    else:
        if player.invincible_reciprocal > 0: # 如果有無敵秒數則進入檢測
            player.invincible_reciprocal -= 1 # 扣減1單位 60單位為1秒
        if player.invincible_reciprocal <= 0: # 如果秒數耗盡
            player.invincible_reciprocal = -1 # 秒數值設定在-1才不會進入迴圈
            player.invincible = False # 關閉無敵


    '''寵物復活與無敵判定'''
    for name in character_name:
        creator = character_dic[name]
        if creator.motion == "dead":
            if creator.invincible_reciprocal > 0: # 如果有無敵秒數則進入檢測
                creator.invincible_reciprocal -= 1 # 扣減1單位 60單位為1秒
            
            if creator.invincible_reciprocal <= 0: # 如果秒數耗盡則重生
                creator.invincible_reciprocal = 0
                creator.invincible = False # 無敵關閉
                creator.motion = "stand" # 復活
                creator.is_move = False # 重新判定是否移動
                creator.move_x = 0 # 原移動量清0
                creator.move_y = 0 # 原移動量清0

                '''升等與提升能力值後重生'''
                tmp_lv = creator.lv
                if creator.num == 244:
                    creator.lv = player.lv
                elif creator.num == 274:
                    creator.lv = player.lv + 1
                elif creator.num == 265:
                    creator.lv = player.lv + 2
                elif creator.num == 250:
                    creator.lv = player.lv + 3
                elif creator.num == 312:
                    creator.lv = player.lv + 4
                elif creator.num == 670:
                    creator.lv = player.lv + 5
                elif creator.num == 325:
                    creator.lv = player.lv + 6
                elif creator.num == 302:
                    creator.lv = player.lv + 7
                elif creator.num == 672:
                    creator.lv = player.lv + 10

                # 依成長率提升能力
                creator.ATK = creator.ATK + creator.ATK_growing * (creator.lv - tmp_lv)
                creator.DEF = creator.DEF + creator.DEF_growing * (creator.lv - tmp_lv)
                creator.HP = creator.HP + creator.HP_growing * (creator.lv - tmp_lv)
                creator.maxHP = creator.HP * 5
                creator.nowHP = creator.maxHP

                # 於出生地重生
                creator.rect.left = creator.original_left
                creator.rect.top = creator.original_top

        else:
            if creator.invincible_reciprocal > 0: # 如果有無敵秒數則進入檢測
                creator.invincible_reciprocal -= 1 # 扣減1單位 60單位為1秒
            
            if creator.invincible_reciprocal <= 0: # 如果秒數耗盡
                creator.invincible_reciprocal = -1 # 秒數值設定在-1才不會進入迴圈
                creator.invincible = False # 關閉無敵


    '''寵物攻擊玩家碰撞檢測'''
    # 精靈與群組檢測：pygame.sprite.spritecollide(被檢測精靈, 檢測是否與該群組碰撞, 是否從群組刪除被碰撞精靈(布林)，collided = (碰撞檢測範圍, 如未另外設定預設其矩形區域)))
    # 精靈檢測：pygame.sprite.collide_rect(first, second)
    if player.invincible == False: # 如非無敵則進入碰撞檢測
        for name in character_name:
            creator = character_dic[name]
            if pygame.sprite.collide_rect(player, creator): # 如果玩家與此寵物名的物件觸發碰撞
                if creator.motion != "dead":
                    if music != final_battle_music:    
                        if creator.zoom: # 如果為巨大化寵物
                            music = final_battle_music
                            pygame.mixer.music.stop() # 關閉音樂
                            pygame.mixer.music.load(music) # 更換為戰鬥音樂
                            pygame.mixer.music.play()
                    if music != battle_music and music != final_battle_music:
                        if creator.zoom == False:
                            music = battle_music
                            pygame.mixer.music.stop() # 關閉音樂
                            pygame.mixer.music.load(music) # 更換為決戰音樂
                            pygame.mixer.music.play()
                    criticalStrike = randint(1, 100) # 爆擊判定變數
                    CranATK = uniform(-creator.ATK * 1.2, creator.ATK * 1.2) # 寵物攻擊亂數
                    PranDEF = uniform(-player.DEF * 1.2, player.DEF * 1.2) # 玩家防禦亂數
                    creator.motion = "atk" # 開啟寵物攻擊動畫
                    creator.index = 0 # 動畫索引歸0 以完整播放動畫
                    
                    '''寵物攻擊方向判定'''
                    x = player.rect.left - creator.rect.left + 20 # 正值在右 負值在左 常數為矯正值
                    y = player.rect.top - creator.rect.top + 40 # 正值在下 負值在上 常數為矯正值
                    
                    # abs()取傳參絕對值 比較xy絕對值大小 判定要執行上下或左右攻擊動畫
                    if abs(x) <= abs(y):
                        # 右
                        if x >= 0:
                            creator.direction = "6"
                        # 左
                        else:
                            creator.direction = "2"
                    elif abs(x) > abs(y):
                        # 下
                        if y >= 0:
                            creator.direction = "0"
                        # 上
                        else:
                            creator.direction = "4"

                    '''傷害判定'''
                    if criticalStrike <= character_dic[name].LUK: # 爆擊成立 傷害 * 1.5
                        damage = ((creator.ATK + CranATK) - (player.DEF + PranDEF)) * 1.5 # 將此寵物名攻擊屬性取出扣減玩家生命值
                        player_hurt_more.play() # 玩家受爆擊音效
                    else: 
                        damage = ((creator.ATK + CranATK) - (player.DEF + PranDEF))
                        player_hurt.play() # 玩家受傷擊音效
                    if damage <= 0: # 如果傷害為負數則傷害為0
                        damage = 0    
                    player.nowHP -= damage # 將傷害扣減玩家生命值
                    if player.nowHP <= 0: # 生命值低於0則死亡
                        music = sad_music
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(music) # 更換為悲傷音樂    
                        pygame.mixer.music.play()
                        player.motion = "dead"
                        player.index = 0 # 將動畫幀數歸0 完整播放死亡動畫
                        player.invincible = True
                        player.invincible_reciprocal = 600 # 無敵10秒
                        print("受到 " + str(damage) + " 傷害")
                        print("剩餘血量: " + str(player.nowHP))
                        print("等待復活中...(5秒)")
                    else:
                        player.invincible = True
                        player.invincible_reciprocal = 60 # 無敵1秒
                        print("受到 " + str(damage) + " 傷害")
                        print("剩餘血量: " + str(player.nowHP))
                        print("無敵開啟1秒 ")


    '''玩家攻擊寵物碰撞檢測'''
    for name in character_name:
        creator = character_dic[name]
        if creator.invincible == False: # 如非無敵則進入碰撞檢測
            # 精靈與群組檢測：spritecollide(被檢測精靈, 檢測是否與該群組碰撞, 是否從群組刪除被碰撞精靈(布林),collided = (碰撞檢測範圍, 如未另外設定預設其矩形區域)))
            if pygame.sprite.spritecollide(creator, weapon_group, True): # 如果此寵物名與武器物件觸發碰撞 pygame.sprite.collide_circle
                criticalStrike = randint(1, 100) # 爆擊判定變數
                CranATK = uniform(-player.ATK * 1.2, player.ATK * 1.2) # 玩家攻擊亂數
                PranDEF = uniform(-creator.DEF * 1.2, creator.DEF * 1.2) # 寵物防禦亂數
                
                '''傷害判定'''
                if criticalStrike <= player.LUK: # 爆擊成立 傷害 * 1.5
                    damage = ((player.ATK + CranATK) - (creator.DEF + PranDEF)) * 1.5 # 將玩家攻擊屬性取出扣減寵物生命值
                else: 
                    damage = ((player.ATK + CranATK) - (creator.DEF + PranDEF))
                
                if damage <= 0: # 如果傷害為負數則傷害為0
                    damage = 0
                creator.nowHP -= damage
                if creator.nowHP <= 0: # 生命值低於0則死亡
                    creator.motion = "dead"
                    creator.index = 0 # 將動畫幀數歸0 完整播放死亡動畫
                    creator.invincible = True
                    creator.invincible_reciprocal = 300 # 無敵5秒
                    print("寵物已死亡 於10秒後重生")
                else:
                    creator.invincible = True
                    creator.invincible_reciprocal = 30 # 無敵0.5秒


    '''繪製血條'''
    # 繪製玩家滿血血條
    pygame.draw.rect(screen, (200, 200, 200), ((player.rect.left - 35, player.rect.top - 20), (100, 5)))
    # 繪製玩家剩餘血條
    pygame.draw.rect(screen, (255, 0, 0), ((player.rect.left - 35, player.rect.top - 20), (100 - ((player.maxHP - player.nowHP + 0.1) / player.maxHP) * 100, 5)) )
    
    for name in character_name:
        creator = character_dic[name]
        if creator.zoom:
            # 繪製寵物滿血血條
            pygame.draw.rect(screen, (200, 200, 200), ((creator.rect.left + 35, creator.rect.top - 20), (100, 5)))
            # 繪製寵物剩餘血條
            pygame.draw.rect(screen, (255, 0, 0), ((creator.rect.left + 35, creator.rect.top - 20), (100 - ((creator.maxHP - creator.nowHP + 0.1) / creator.maxHP) * 100, 5)) )
        else:
            if creator.num == 670: # 塔斯夫特別校正
                # 繪製寵物滿血血條
                pygame.draw.rect(screen, (200, 200, 200), ((creator.rect.left + 45, creator.rect.top - 20), (50, 5)))
                # 繪製寵物剩餘血條
                pygame.draw.rect(screen, (255, 0, 0), ((creator.rect.left + 45, creator.rect.top - 20), (50 - ((creator.maxHP - creator.nowHP + 0.1) / creator.maxHP) * 50, 5)) )
            else:
                # 繪製寵物滿血血條
                pygame.draw.rect(screen, (200, 200, 200), ((creator.rect.left + 10, creator.rect.top - 20), (50, 5)))
                # 繪製寵物剩餘血條
                pygame.draw.rect(screen, (255, 0, 0), ((creator.rect.left + 10, creator.rect.top - 20), (50 - ((creator.maxHP - creator.nowHP + 0.1) / creator.maxHP) * 50, 5)) )




    '''動畫更新'''
    player.charcter_updata() # 更新玩家動畫
    for weapon in weapon_list: # 更新武器動畫
        weapon.move()
        if weapon.move_x == 0 and weapon.move_y == 0:
            weapon_list.remove(weapon) # 解構已超出射程武器
    creat_motion(character_name) # 更新寵物動畫
    pygame.display.update() # 刷新畫布
    # 延遲：因調用clock.tick_busy_loop()會使clock.tick()必須拉高至一定fps(否則會嚴重lag)
    # 由於動畫速度過快 故加此延遲放慢動畫速度
    pygame.time.delay(20)
pygame.quit() # 退出遊戲