# Onmyoji_Python

大风刮倒梧桐树，自有旁人论长短

## 前言

[使用文档](https://github.com/AquamarineCyan/Onmyoji_Python/wiki)

## 主要功能
1. 组队御魂副本
2. 组队永生之海副本
3. 业原火副本
4. 御灵副本
5. 个人突破
6. 寮突破
7. 道馆突破
8. 普通召唤
9. 百鬼夜行
10. 限时活动

## 下载  

~~**无论哪种都需要管理员权限**~~

1. 前往 [releases](https://github.com/AquamarineCyan/Onmyoji_Python/releases) 下载解压打包完成的应用程序，点开即用
2. 需要一定的基础，更新较勤，可能存在bug  
   - 使用`git`命令下载源码  
     `git close https://github.com/AquamarineCyan/Onmyoji_Python.git`  
     后续只需`git pull`
   - 安装依赖 
     - venv 方式 
       `pip install -r requestments.txt`
     - poetry 方式
       `poetry init`
   - 自行打包，打包配置已存在`main.spec`    
     `pyinstaller main.spec`
   - 或者不打包，直接运行（理论上能够生成UI）  
     `python main.py`

## Tips

**请自行合理使用，所产生的一切后果自负**


使用过程中（`环境检测`后），~~请不要移动游戏窗口，会导致点击位置错误~~  
移动游戏窗口后，点击`更新窗口信息`即可
