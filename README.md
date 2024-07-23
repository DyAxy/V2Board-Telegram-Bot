# V2Board Telegram Bot via Python

一个简单的项目，让 V2Board Telegram Bot 支持更丰富的功能。  
使用反馈、功能定制可加群：[https://t.me/dyaogroup](https://t.me/dyaogroup)

Python 版本需求 >= 3.9

## 现有功能
- 基于MySQL，支持以SSH方式登录
- 自动删除群聊中命令信息
- 支持Bot内绑定、解绑
- 支持获取用户信息、订阅、邀请

## 现有指令
|   指令   |   参数    |         描述         |
| :------: | :-------: | :------------------: |
|   ping   |    无     |     获取聊天的ID     |
|   bind   |   订阅    | 绑定该订阅到Telegram |
|  unbind  |    无     | 解绑该TG的Telegram  |
|  mysub   |    无     | 获取该账号的订阅链接 |
|  myinfo  |    无     | 获取该账号的订阅信息 |
| myinvite |    无     | 获取该账号的邀请信息 |

## 常规使用
```
# apt install git 如果你没有git的话
git clone https://github.com/DyAxy/V2Board_Telegram_Bot.git
# 进程常驻可参考 screen 或 nohup 或 systemctl
# 你需要安装好 pip3 的包管理
cd V2Board_Telegram_Bot
pip3 install -r requirements.txt
cp config.yml.example config.yml
nano config.yml
# 根据注释中的内容修改配置
python3 bot.py
```

## 申请 Telegram Bot Token

1. 私聊 [https://t.me/BotFather](https://https://t.me/BotFather)
2. 输入 `/newbot`，并为你的bot起一个**响亮**的名字
3. 接着为你的bot设置一个username，但是一定要以bot结尾，例如：`v2board_bot`
4. 最后你就能得到bot的token了，看起来应该像这样：`123456789:gaefadklwdqojdoiqwjdiwqdo`
