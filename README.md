# Figma-To-Eagle
使用 Eagle 管理 Figma 文件

## 现存问题和优化机会

Figma 目前只支持通过项目维度对设计文件进行分类；[Eagle](https://cn.eagle.cool/) 支持强大的设计素材管理功能。

![图片来自 Eagle 官网](https://jiangzilong-image.oss-cn-beijing.aliyuncs.com/uPic/Company/20211229182808.jpg)

图片来自 Eagle 官网

我们可以通过将 Figma 文件导入 Eagle 再利用 Eagle 的标签、注释等功能为设计添加更多属性，可带来以下好处

1. 更好的设计文件检索体验(特别是团队文件较多时)

2. 实现**设计沉淀**、积攒自己的设计库

   例如可以对不同文件打上「活动弹窗」、「数据分析」等标签，让设计打破项目的壁垒，新人参与项目或做新设计时可找到同类型参考、避免重复造轮子。

## 解决方案

利用 [Figma API](https://www.figma.com/developers/api) 获取文件信息，再利用 [Eagle API](https://www.yuque.com/augus-gsjgn/eagle-api) 将文件信息导入 Eagle，之后就可以正常在 Eagle 中添加文件标签管理文件了。

获取 Figma 文件的封面信息需要先下载到本地再导入 Eagle，偶现下载失败时使用 `PIL` 模块将文件名转图片再导入 Eagle（Eagle 导入必须传一个本地的图片路径）

## 使用方法

Python：3.9.9

Python 库：requests、PIL

1. 打开 Eagle 客户端，链接到对应的资源库

2. 配置 `config.json`

   ```json
   {
     "eagle": {
       "eagle_data_count": 683,
       "folders_id": "KXH06W3PRHTDK"
     },
     "figma": {
       "team_id": "0000000000000",
       "figma_token": "183183-cb23c011-1a1c-4c3f-1acb-2a2cee1833cf"
     },
     "main_path": "/Users/cc/Documents/JiangZiLong/minpg/image/figmaCover/"
     ,"font":"/Users/cc/Library/Fonts/OPPOSans-R.ttf"
   }
   ```

   - eagle_data_count：Eagle 目标文件夹的文件数，若不指定文件夹则值设置为 `""`

     ![https://jiangzilong-image.oss-cn-beijing.aliyuncs.com/uPic/mYa7Sq20211229232003.jpg](https://jiangzilong-image.oss-cn-beijing.aliyuncs.com/uPic/mYa7Sq20211229232003.jpg)

   - folders_id：上述文件夹的 ID

     从资源库下 `metadata.json` 中获取

     ```json
     // metadata.json
     {
       "folders": [
         {
           // ……
           "children": [
             {
               "id": "KXH06W3PRHTDK",
               "name": "【目标目录】",
               "description": "",
               "children": [],
               "modificationTime": 1640145345541,
     ```

   - team_id：Figma 的团队 ID

     在 Figma 首页选中目标团队后从 URL 中获取

     ![https://jiangzilong-image.oss-cn-beijing.aliyuncs.com/uPic/Company/20211229182204.png](https://jiangzilong-image.oss-cn-beijing.aliyuncs.com/uPic/Company/20211229182204.png)

   - figma_token：Figma > 右上角头像 > 设置 > 创建 Token

     ![https://jiangzilong-image.oss-cn-beijing.aliyuncs.com/uPic/Company/20211229182415.png](https://jiangzilong-image.oss-cn-beijing.aliyuncs.com/uPic/Company/20211229182415.png)

   - main_path：本地路径，从 Figma 中下载的文件封面将保存在这里

   - font：本地字体文件路径，当 Figma 封面下载失败时，将使用此字体合成封面图片再导入 Eagle
