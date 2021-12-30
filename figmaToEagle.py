# -*- coding:utf-8 -*-
import requests
import json
import os
import time
from datetime import datetime
import difflib

import imageApi


def search_eagle(figma_key):
    '''
    在 Eagle 中搜索文件
    '''
    for index in range(len(EAGLE_DATA)):
        # 根据 Eagle 文件的 URL 进行匹配
        if(EAGLE_DATA[index]['url'].find(figma_key)>0):
            return {'success':True,'msg':'找到文件','data':EAGLE_DATA[index]}

    return {'success':False,'msg':'没有找到文件','data':{}}

# 读取配置文件
with open('config.json') as json_file:
    config = json.load(json_file)

# Figma 接口凭证
FIGMA_TOKEN = config['figma']['figma_token']
# CFun Center 团队 id
TEAM_ID = config['figma']['team_id']
# 封面保存到本地的路径
MAIN_PATH = config['main_path']
# Eagle 目录 ID,metadata.json
FOLDERS = config['eagle']['folders_id']
# FOLDERS 目录中文件数量
EAGLE_DATA_COUNT = config['eagle']['eagle_data_count']
EAGLE_DATA = []


# 获取 Eagle 的数据【确保 Eagle 开启并链接到对应资源库】
# 根据创建时间正序获取
requestOptions_1 = {'folders':FOLDERS,'orderBy':'CREATEDATE','limit':str(round(EAGLE_DATA_COUNT/2)+10)}
eagle_req_1 = requests.get(url='http://localhost:41595/api/item/list',params=requestOptions_1)
eagle_req_json_1 = json.loads(eagle_req_1.text)
eagle_data_1 = eagle_req_json_1['data']
# 根据创建时间倒序获取
requestOptions_2 = {'folders':FOLDERS,'orderBy':'-CREATEDATE','limit':str(round(EAGLE_DATA_COUNT/2))}
eagle_req_2 = requests.get(url='http://localhost:41595/api/item/list',params=requestOptions_2)
eagle_req_json_2 = json.loads(eagle_req_2.text)
eagle_data_2 = eagle_req_json_2['data']
# 组合上述 2 批数据
EAGLE_DATA = eagle_data_1+eagle_data_2

# 根据 Team ID 获取 Figma 项目 ID
url = 'https://api.figma.com/v1/teams/'+TEAM_ID+'/projects'
headers = {
    'x-figma-token': FIGMA_TOKEN
}
req = requests.get(url=url, headers=headers)
projectInfo = json.loads(req.text)
projects = projectInfo['projects']

# 遍历项目，获取项目下的文件
for item in projects:
    
    url = 'https://api.figma.com/v1/projects/'+item['id']+'/files'
    headers = {
        'x-figma-token': FIGMA_TOKEN
    }
    req = requests.get(url=url, headers=headers)
    filesInfo = json.loads(req.text)
    files = filesInfo['files']

    print(item['name']+' - files count:'+str(len(files)))

    to_eagle_data = []  # 存储需要导入 Eagle 的数据
    
    # 构造传给 Eagle 的数据
    for index in range(len(files)):
        # 判断是否已包含此文件（根据文件 key）
        search_req = search_eagle(files[index]['key'])
        # 如果 Eagle 内已包含
        if(search_req['success']):
            # 判断文件信息是否需要更新(名称相似度)
            if(difflib.SequenceMatcher(None, files[index]['name'], search_req['data']['name']).ratio()<0.7):
                # 需要更新 /api/item/update，但 Eagle API 暂不支持更新文件名称，所以更新到 Eagle 的注释信息中，便于 Eagle 内搜索
                requestOptions = {'id':search_req['data']['id'],'annotation':search_req['data']['annotation']+' '+files[index]['name']}
                eagle_req = requests.post(url='http://localhost:41595/api/item/update',json=requestOptions)
                continue
            else:
                # 不需要更新（跳过此文件）
                continue
        # 如果 Eagle 内未包含，则将数据加入 Eagle
        # 下载 Figma 封面数据
        download_img_req = imageApi.downloadImg(files[index]['thumbnail_url'],MAIN_PATH) # 图片路径
        if(download_img_req['success']):
            pass
        else:
            # Figma 封面下载失败，使用文件名称渲染封面图片
            download_img_req = imageApi.strToImg(files[index]['name'],MAIN_PATH)

        # 如果封面处理成功
        if(download_img_req['success']):

            # 文件名称
            name = files[index]['name']
            # 文件链接
            website = 'https://www.figma.com/file/'+files[index]['key']
            # 标签
            tags = [item['name']] # 项目名称
            last_modified = datetime.strptime(files[index]['last_modified'], '%Y-%m-%dT%H:%M:%S%fZ')
            tags.append(str(last_modified.year)+'年') # 最近修改的年份
            tags.append(str(last_modified.month)+'月') # 最近修改的月份
            # 图片注释
            annotation = ''
            # 最近更新视觉

            to_eagle_data.append({'path':download_img_req['imgLoaclPath'],'name':name,'website':website,'tags':tags,'annotation':annotation})
            
            time.sleep(0.4)
        else:
            # 封面处理失败，无法导入 Eagle
            print('图片下载失败：'+files[index]['name']+' '+'https://www.figma.com/file/'+files[index]['key'])

    if(len(to_eagle_data)>0):
        # 导入 Eagle（本地需要先启动 Eagle）
        requestOptions = {'items':to_eagle_data,'folderId':FOLDERS}
        eagle_req = requests.post(url='http://localhost:41595/api/item/addFromPaths',json=requestOptions)

        # 等待导入
        time.sleep(2)
    