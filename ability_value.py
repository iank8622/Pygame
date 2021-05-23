'''
目前已無作用。
為優化前主程式導入之物件class。
'''

import pygame

class Ability(pygame.sprite.Sprite):
    def __init__(self, name, num, act, qty, x, y, zoom, lv, ab_point, ATK_growing, DEF_growing, HP_growing, ATK, DEF, SPD, HP, LUK):
        pygame.sprite.Sprite.__init__(self)

        self.name = name
        self.num = num
        self.act = act    
        self.qty = qty
        #self.x = x   
        #self.y = y
        self.zoom = zoom
        self.lv = lv
        self.zoom = zoom
        self.exp = 0
        self.lvup_exp = 100
        self.give_exp = 50
        self.ab_point = ab_point

        self.ATK_growing = ATK_growing
        self.DEF_growing = DEF_growing
        self.HP_growing = HP_growing

        self.ATK = ATK
        self.DEF = DEF
        self.SPD = SPD
        self.HP = HP
        self.LUK = LUK
        self.maxHP = self.HP * 5
        self.nowHP = self.maxHP

        self.movex = 0 # 沿 X 方向移動
        self.movey = 0 # 沿 Y 方向移動
        self.frame = 0 # 幀計數

        self.images = [pygame.image.load("imgs/35_1/35_1_0.png")]
        
        self.image = self.images[0]
        self.rect  = self.image.get_rect()        


    ''' 控制玩家移動 ''' 
    def control(self, x, y): 
        self.movex += x
        self.movey += y


    ''' 更新玩家位置 '''
    def update(self):  
        self.rect.x = self.rect.x + self.movex
        self.rect.y = self.rect.y + self.movey
        self.x = self.rect.x
        self.y = self.rect.y

        # 向左移動 
        if self.movex < 0: 
            self.act = 38
        # 向右移動 
        if self.movex > 0:
            self.act = 80
        #向上移動 
        if self.movey > 0:
            self.act = 64
        #向下移動 
        if self.movey < 0:
            self.act = 12
        #待機
        if self.movex == 0 and self.movey == 0:
            self.act = self.act - 3


