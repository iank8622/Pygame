'''
目前已無作用。
為優化前主程式導入之class。
'''

# GIF動態圖片分割器

import os # 用於創建文件夾 處理文件路徑
import sys
from PIL import Image # 用於打開/讀取/保存圖片


def main(gif_path:str):
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
            print("End")
            break 
        gif_obj.seek(frame_num) # 將圖片定位到指定幀         
        # BW_BG_Transparency(gif_obj)
        gif_obj.save(os.path.join(output_floder, "{0}_{1}".format(filename, frame_num) + ".png")) # 將當前幀輸出至輸出目錄
        frame_num += 1 # 指向下一號

    print("共輸出{0}張圖片".format(frame_num)) # 提示完成


'''
def BW_BG_Transparency(gif_obj):
    #image = Image.open(gif_obj) # 打開圖像 為PIL.Image.Image資料型態物件 模式為RGB
    image = gif_obj.convert("RGBA") # 轉換模式為RGBA 為了後續將背景透明化    
    newImage = []
    for item in image.getdata(): # 取得gif_obj當前幀中像素物件
        #item = Image.open(item)
        #item = item.convert("RGBA") # 轉換模式為RGBA 為了後續將背景透明化
        if item[:3] == (255, 255, 255): # 如果RGB為白色便將其設定為透明
            newImage.append((255, 255, 255 ,0))
        elif item[:3] == (0, 0, 0): # 如果RGB為黑色便將其設定為透明
            newImage.append((0, 0, 0 ,0))
        else:
            newImage.append(item)
    gif_obj.putdata(newImage) # 將去背後的資料放回來
'''

'''
def BW_BG_Transparency(gif_obj):
    png_obj = Image.open(png_path) # 打開png圖像 為PIL.Image.Image資料型態物件 模式為RGB
    png_obj = png_obj.convert("RGBA") # 轉換模式為RGBA 為了後續將背景透明化    
    newImage = []
    for item in png_obj.getdata(): # 取得gif_obj中像素物件
        if item[:3] == (255, 255, 255): # 如果RGB為白色便將其設定為透明
            newImage.append((255, 255, 255 ,0))
        elif item[:3] == (0, 0, 0): # 如果RGB為黑色便將其設定為透明
            newImage.append((0, 0, 0 ,0))
        else:
            newImage.append(item)
    png_obj.putdata(newImage) # 將去背後的資料放回來
'''

'''
if __name__ == "__main__":
    # 從命令行參數讀取gif路徑
    if len(sys.argv) == 2:
        gif_path = sys.argv[1]
        main(gif_path)
    else:
        print("請於命令行輸入gif圖像路徑")
'''
