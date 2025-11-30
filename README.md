# OnmyojiDesktopAssistant

![Python](https://img.shields.io/badge/python-3.11+-blue)

[![GitHub release (with filter)](https://img.shields.io/github/v/release/AquamarineCyan/OnmyojiDesktopAssistant)](https://github.com/AquamarineCyan/OnmyojiDesktopAssistant/releases/latest)

## 简介

本项目仅支持阴阳师桌面版使用，~~使用过程中会占用鼠标，桌面版需前置（可使用游戏自带的置顶功能）~~ V2版本提供了后台交互的功能，开启后仅当前一次使用生效。

## 帮助文档

[帮助文档](https://docs.qq.com/doc/DZUxDdm9ya2NpR2FY)

## 主要功能

1. 御魂副本
   - 十层/悲鸣/神罚
   - 组队/单人
   - 组队司机/打手
2. 组队永生之海副本
    - 适配司机/打手
3. 业原火副本
4. 御灵副本
5. 个人突破
    - 卡级/退级
    - 3胜刷新
6. 寮突破
    - 锁定阵容，从上至下进攻
7. 道馆突破
    - 等待系统进入/手动挑战/正在进行中
    - 仅支持挂机阵容
8. 普通召唤
    - 十连灰票
9. 百鬼夜行
    - 清票
10. 限时活动
    - 体力爬塔300次/周年庆999次
11. 日轮副本
    - 组队/单人
    - 组队司机/打手
12. 单人探索
    - 准备自动轮换
13. 契灵
    - 探查
    - 结契
14. 觉醒副本
15. 六道之门速刷
    - 目前仅适配：椒图，4柔风，不打星之子的阵容，需要手动勾选“不再提醒”
16. 斗技自动上阵
    - 挂机阵容，自动上阵
17. 英杰试炼
    - 鬼兵演武
    - 兵藏秘境

---

- [x] 全局悬赏封印
- [x] 记忆上次所选功能
- [x] 识别多种战斗主题
- [x] 支持后台交互 :sparkles:
- [x] 有效词条分析
- [x] 游戏窗口管理


## 使用方法

### 桌面版

 - 旧版桌面版
   - [NGA下载地址](https://nga.178.com/read.php?tid=29661629)
 - 新版桌面模拟器，通过官方MuMu专版下载，支持新区账号登录
   - [阴阳师桌面模拟器](https://yys.163.com/zmb/)
 - 新版与旧版仅窗口名称区别，其余功能一致。


###  应用程序运行

- 前往 [releases](https://github.com/AquamarineCyan/OnmyojiDesktopAssistant/releases/latest)
- 下载最新压缩包 `OnmyojiDesktopAssistant-2.x.x.zip`
- 解压后双击 `OnmyojiDesktopAssistant.exe` 即可运行。
> [!NOTE]
> 需要解压到英文路径下

### 源码编译运行

<details><summary> 不推荐 </summary>

1. 使用 `git` 命令下载源码  
    ```bash
    git clone https://github.com/AquamarineCyan/OnmyojiDesktopAssistant.git --depth=1 --single-branch
    ```

2. 安装依赖 
    - venv 方式  
    `pip install -r requestments.txt`
    - poetry 方式  
    `poetry install`

3. 添加文字识别依赖库
    从 [releases](https://github.com/AquamarineCyan/OnmyojiDesktopAssistant/releases/latest) 下载 `OnmyojiDesktopAssistant-2.x.x.zip`， 解压后找到`ocr`文件夹放在项目根目录下

4. 运行
    - 终端运行 `python main.py`
    - 使用VSCode调试，调试模式选择`Project`

5. 打包
    - 需要poetry环境，打包配置已存在 `main.spec`  
    - 终端运行 `pyinstaller main.spec` 或者双击 `build.bat`

</details>

## 程序目录

```
   |- data # 用户数据
      |- myresource # 自定义素材，用法见(#注意事项)
      |- screenshot # 截图
      |- config.yaml # 配置文件
      |- update_info.json # 更新记录
   |- lib # 运行库
   |- log # 日志
   |- ocr # 文字识别库
   |- resource # 素材文件
```

## 主界面

![效果图](效果图.png)

## 日服

1. 下载下方 `Assets` 的 `resource_ja.zip`
2. 解压后，复制到软件根目录，与自带的 `resource` 文件夹同级
3. 软件设置 - `游戏服务器`  改为 `日服` ，重启
4. 无报错信息即可使用
5. 目前仅适配 `单人御魂副本` ，资源及测试由 [@huahua1125](https://github.com/huahua1125) 提供

## 注意事项

**请自行合理使用，所产生的一切后果自负**

1. 基于图像识别和文字识别，支持多种战斗主题，建议游戏窗口不要过小，推荐强制缩放。

2. 推荐在功能界面开始任务。例如组队御魂类副本，在组队房间内开始任务。

3. 移动游戏窗口后，会自动更新窗口。

   多开游戏窗口，需要手动点击`游戏检测`，会检测位于较上层的游戏窗口。

   针对常见`1920*1080`分辨率下的非100%缩放，可修改游戏路径下的`Launch.exe`属性，避免每次强制缩放
   ```bash
   属性 - 兼容性 - 更改高DPI设置 - 替代高DPI缩放行为为`应用程序`
   ```

4. 如果需要自定义识别的素材，可参考 `resource` 下的分类方法，在 `/data/myresource` 给出相同路径的素材即可。

    例如需要使用自定义的 `/resource/huodong/title.png` 文件，则新建 `/data/myresource/huodong/title.png` 即可。程序将优先使用用户给定的自定义素材。

## 感谢

[raoyutian/PaddleOCRSharp](https://gitee.com/raoyutian/PaddleOCRSharp) 基于paddle的本地离线OCR v3识别库

## 更新记录

[CHANGELOG.MD](CHANGELOG.MD)
