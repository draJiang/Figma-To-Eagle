import pytesseract
import os
import time
import requests
import json

from PIL import Image,ImageFont,ImageDraw

# 读取配置文件
with open('config.json') as json_file:
    config = json.load(json_file)

# 默认的文件保存的目录
MAIN_PATH = './imageApi/image/'
# FONT，用于将文字渲染成图片
FONT = config['font']

def strToImg(text,mainPath):
    '''
    文字转图片
    '''
    if(mainPath=='' or mainPath==None):
        mainPath = MAIN_PATH
    W,H = (800,400) 
    # 图片宽、高、背景色
    im = Image.new("RGB", (W,H), (26, 26, 26))
    dr = ImageDraw.Draw(im)
    # 字体、字号
    font = ImageFont.truetype(FONT, 44) 

    w,h = dr.textsize(text,font=font)
    # 文字在背景中的位置、颜色
    dr.text((20, (H-h)/2), text, font=font, fill="#F3F3F3")
    # im.show()
    
    # 图片保存的路径
    path = mainPath+ str(int(time.time()*1000))+'.png'
    im.save(path)

    return {'success':True,'imgLoaclPath':path}

def getOCRCode(path):
    '''
    path：本地路径，str
    code：返回 ocr 文本
    '''
    # open的是图片的路径
    image = Image.open(path)
    code = pytesseract.image_to_string(image, lang='chi_sim')
    print(code)
    return code
    
def downloadImg(imgURL,mainPath):
    '''
    下载图片
    输入 imgURL：图片 URL，str
    返回 imgLocalPath：图片本地文件
    '''

    if(mainPath==''):
        mainPath = MAIN_PATH
    os.makedirs(mainPath, exist_ok=True)
    headers = {
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

    r = requests.get(url=imgURL, headers=headers)
    imgLoaclPath = mainPath + str(int(time.time()*1000))+'.png'
    
    with open(imgLoaclPath, 'wb') as f:
        f.write(r.content)
    
    if(r.status_code!=200):
        success = False
    else:
        success = True

    return {'success':success,'imgLoaclPath':imgLoaclPath}