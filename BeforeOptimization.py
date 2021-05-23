'''
目前已無作用。
為優化前主程式，以多線程(threading)運作。
'''

import pygame
import threading # 多線程 模組
import sys
import os
import pyautogui
import GIFSpliter as GS # 自定義 模組。GIF動態圖片分割器。
import ability_value as ab # 自定義 模組。能力屬性值物件。
import privateItems as pItems # 自定義 模組。私有物件。
from random import randint

#import queue # queue.Queue() 佇列 模組，先入先出，解決多線程共享變數同時使用之安全問題。


'''GIF分割成PNG'''
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
                        GS.main(gif_path) # 將gif依幀切割成png                     
        else:
            print("Error!That isn't a directory!")


'''載入PNG成多幀list並置於佇列中'''
def load_gif(name, num, act, x, y, zoom):   
    global lock
    global screen
    global ability_dic
    
    if not os.path.exists("imgs/"):
        print("imgs路徑錯誤或不存在")
 
    png_pathf = "imgs/{0}_{1}" # 格式化路徑
    pngNames = locals() # 動態變數(dict)
    loadGifList = []
    pngList = os.listdir(png_pathf.format(num, act))
    count = 0
    for png in pngList:
        count += 1
        if os.path.isfile(png_pathf.format(num, act) + "/" + png): # 如果該路徑為檔案
            png_path = png_pathf.format(num, act) + "/" + png
            character = pygame.image.load(png_path)
            if zoom:
                character = pygame.transform.scale2x(character)
            ability_dic.get_dic(name).img = character
            ability_dic.get_dic(name).rect = ability_dic.get_dic(name).img.get_rect()
            pngNames[name] = character
            loadGifList.append(pngNames[name])
            
        else:
            print("erro")
    ability_dic.get_dic(name).frame = count

    animation_refresh(loadGifList, x, y) # 播放gif


'''播放gif的png幀'''
def animation_refresh(loadGifList, x, y):
    # 鎖住
    global lock


    for png in loadGifList:
        # blocking=True, timeout=110
        lock.acquire()
        screen.blit(png, (x, y))
        pygame.display.update()
        lock.release()
        pygame.time.delay(100)


'''角色數值生成'''
def generate_ab(num, act, qty, zoom, lv, ab_point, ATK_growing, DEF_growing, HP_growing, ATK, DEF, SPD, HP, LUK):
    global ability_dic
    global ability_names
    global xy_dict

    xy_demo = "xy_{}"
    for q_ab in range(1,qty + 1):
        name = "pet{}_th{}".format(num, q_ab) # 為每個線程取名
        # 隨機xy值
        if num == 35:
            xy_name = xy_demo.format(num)
            x, y = xy_dict[xy_name]
        else:
            ran_x = randint(1,500)
            ran_y = randint(1,500)
            xy_name = xy_demo.format(num)
            x, y = xy_dict[xy_name]
            x = x - ran_x
            y = y - ran_y
        # 創建能力值物件
        new_ab = ab.Ability(name, num, act, qty, x, y, zoom, lv, ab_point, ATK_growing, DEF_growing, HP_growing, ATK, DEF, SPD, HP, LUK)
        ability_dic.set_dic(name, new_ab)
        # 儲存名稱當ability_dic的key
        ability_names.append(name)


'''寵物多線程生成'''
def generate_pet():
    global ability_dic
    global ability_names

    # 讀取所有角色名稱(key)
    for name in ability_names:
        # 建立多線程 生成角色動畫surface
        this_ab = ability_dic.get_dic(name)
        num = this_ab.num
        act = this_ab.act
        x = this_ab.x
        y = this_ab.y
        zoom = this_ab.zoom

        # 將多線程放入list
        '''
        一旦進去load_gif方法後，原本該dict角色(僅此key下值)名下屬性質變為Thread obj。
        第一輪就可以看到dict的變化，但還取的到。第二輪開始就不行。
        問題未解決，故將原ability_dic創建為私有物件強制禁止修改。
        '''
        pet_character[name] = threading.Thread(target=load_gif, args=(name, num, act, x, y, zoom))
        threads.append(pet_character[name])


'''玩家移動控制'''
def control(self, x, y):    
    pass


if __name__ == "__main__":
    '''初始化介面'''
    pygame.init() # 初始化導入 pygame 模組
    #screen = pygame.display.set_mode(pyautogui.size()) # 設定尺寸並顯示視窗 pyautogui.size()取得當前螢幕解析度
    screen = pygame.display.set_mode([int(2868 * 1.5), int(1456 * 1.5)]) # 設定尺寸並顯示視窗 pyautogui.size()取得當前螢幕解析度
    pygame.display.set_caption("StoneAge") # 設置視窗標題
    screen.fill((0, 0, 0)) # 填滿顏色(rgb)
    lock = threading.Lock() # 鎖變數，才不會共享數據互相干擾。
    
    '''背景'''
    bg_img = pygame.image.load("bg/bg.png")
    screen.blit(bg_img, (0, 0))
    
    '''BGM'''
    pygame.mixer.init() # 初始化
    
    normal_music = pygame.mixer.Sound("bgm/normal.mp3")
    normal_music.set_volume(0.7) # 音量大小(0~1)
    normal_music.play()


    is_move = False

    '''角色初始能力創建'''
    ability_dic = pItems.Dic() # 角色能力值資料 為私有物件
    ability_names = []  # 角色名稱(key)列表 

    '''初始座標'''

    xy_dict = {"xy_35" : (800, 500), # 玩家
            "xy_340" : (1000 , 300), # 巴朵蘭恩
            "xy_241" : (1500, 600)} # 烏力

    # 為每個角色創建能力值
    # num, act, qty, zoom, lv, ab_point, ATK_growing, DEF_growing, HP_growing, ATK, DEF, SPD, HP, LUK
    generate_ab(35, 9, 1, False, 1, 20, 1, 1, 1, 5, 5, 20, 5, 0) #玩家

    generate_ab(340, 5, 1, True, 90, 0, 7, 5, 3, 20, 10, 30, 8, 60) # 巴朵蘭恩
    generate_ab(241, 5, 20, False, 1, 0, 3, 3, 4, 9, 5, 10, 7, 10) # 烏力

    '''分割並載入gif資源'''
    if not os.path.exists("imgs/"): # 若已分割gif資源(路徑/資料夾)不存在 則執行分割
        split_gif()

    while True: # 無限迴圈確保視窗一直顯示
        lock.acquire()
        for event in pygame.event.get(): # 遍歷所有事件
            if event.type == pygame.QUIT: # 如果單擊關閉視窗，則退出
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN: # 鼠標點下反應
                print('鼠標點擊',event.pos)
                mx, my = event.pos
                pygame.display.update()
                is_move = True
            elif event.type == pygame.MOUSEBUTTONUP: # 鼠標彈起反應
                print('鼠標彈起')
                is_move = False
            elif event.type == pygame.MOUSEMOTION: # 鼠標移动反應
                if is_move:
                    pygame.display.update()
            if event.type ==pygame.KEYDOWN: # 鍵盤按下反應
                print('鍵盤按下')
                print(chr(event.key))
            elif event.type == pygame.KEYUP: # 鍵盤彈起反應
                print('鍵盤彈起')
                print(chr(event.key))
        lock.release()

        '''GIF線程(人物 + 寵物)''' # 需放於迴圈內以在每次迴圈new線程，才不會出現同一線程禁重複start() bug。
        # threading.Thread()是一個類。target表示要調用的函數名，args表示調用函數的參數。
        pet_character = locals()
        threads = []

        generate_pet()


        # 將多線程依次開啟
        for t in threads:          
            t.setDaemon(True) # 將線程聲明為守護線程，必須在start() 方法調用之前設置，如果不設置為守護線程程序會被無限掛起。子線程啟動後，父線程也繼續執行下去，
            t.start() # 開始線程活動，每個線程僅能啟動一次。start() 會調用run()。            
        t.join() # join()方法，用於等待線程終止。join（）的作用是，在子線程完成運行之前，這個子線程的父線程將一直等待(完成後正常關閉子線程)。

        #pygame.display.flip() # 更新全部顯示

    pygame.quit() # 退出pygame
