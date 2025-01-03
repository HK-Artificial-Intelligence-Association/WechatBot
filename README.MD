# WeChatRobot

<details><summary><font color="red" size="12">免责声明【必读】</font></summary>

本工具仅供学习交流使用，不保证本工具对微信账号的安全性。

本工具仅供学习和技术研究使用，不得用于任何商业或非法行为，否则后果自负。

本工具的作者不对本工具的安全性、完整性、可靠性、有效性、正确性或适用性做任何明示或暗示的保证，也不对本工具的使用或滥用造成的任何直接或间接的损失、责任、索赔、要求或诉讼承担任何责任。

本工具的作者保留随时修改、更新、删除或终止本工具的权利，无需事先通知或承担任何义务。

本工具的使用者应遵守相关法律法规，尊重微信的版权和隐私，不得侵犯微信或其他第三方的合法权益，不得从事任何违法或不道德的行为。

本工具的使用者在下载、安装、运行或使用本工具时，即表示已阅读并同意本免责声明。如有异议，请立即停止使用本工具，并删除所有相关文件。

</details>

基于 [WeChatFerry](https://github.com/lich0821/WeChatRobot) 与 [原版WeCharRobot](https://github.com/lich0821/WeChatRobot) 优化与更新后的微信机器人。添加了不少原版机器人不具有的功能。

> ❗ 关于为什么原仓库的 Commit 记录没了，是因为当时写这个项目的姑娘不太会操作 Git 于是便将 `.git` 仓库清了重置了~ 后边在新的记录上缝缝改改一去不返，实在是抱歉。因此，本仓库的 init commit 的内容基本上都来源于原仓库的贡献者（已列于下方 Contributors）。

#### 新增的功能

- 聊天数据统计

![聊天数据统计](./doc/periodstatistic.png)

- 定时聊天总结

![定时聊天总结](./doc/conversationsummary.png)

- 支持用户主动调用对聊天内容的总结

![help](./doc/help.png)

- 基于 SQLite3 的聊天权限管理

## 安装步骤

0. 遇到问题可以看 **原仓库的[文档](https://wechatferry.readthedocs.io/zh/latest/)、[教程](https://mp.weixin.qq.com/s/APdjGyZ2hllXxyG_sNCfXQ)和 [FAQ](https://mp.weixin.qq.com/s/bdPNrbJYoXhezCzHMqLoEw)。**

   - 按照步骤来，版本保持一致，少走弯路。
   - 若需要更详细的安装步骤以及后续的开发，可以阅读[补充资料](https://m0e8x072xo3.feishu.cn/wiki/KsUGwdax3i4gcskfApncXPXgnLh)
1. 安装 Python>=3.9（建议3.10），例如 [3.10.11](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
2. 安装微信 `3.9.10.27` (与 `wcf` 版本v39.2.x 兼容) ，下载地址在[原作者地址](https://github.com/lich0821/WeChatFerry/releases/tag/v39.2.4) 或[WeChatSetup](https://gitee.com/lch0821/WeChatSetup) 。
3. 克隆项目

```sh
git clone -b xjy https://github.com/HK-Artificial-Intelligence-Association/WechatBot.git
```

4. 安装依赖

```sh
# 升级 pip
python -m pip install -U pip
# 安装必要依赖
pip install -r requirements.txt
# ChatGLM 还需要安装一个 kernel
ipython kernel install --name chatglm3 --user
```

5. 配置虚拟环境

```bash
# 创建虚拟环境
conda create -n your_env_name python=3.10
# 启用虚拟环境
conda activate your_env_name
```

6. 运行

我们需要运行两次 `main.py` 第一次是生成配置文件 `config.yaml`, 第二次是真正跑你的机器人。
直接运行程序会自动拉起微信，如果微信未打开，会自动打开微信；如果版本不对，也会有提示；其他报错，请进群交流。

下面代码为第一次运行：第一次运行 `main.py` 会在 WeChatRobot 目录下生成一个 `config.yaml` 文件，参照修改配置进行修改。

同时，第一次运行可能会出现报错弹窗，请根据后文“运行遇到的问题”进行处理。

其中 chatgpt、tigerbot、chatglm 和 xinghuo_web 是四种模型的配置信息，你需要配置它们的参数，不知道的可以加群交流。

```sh
python main.py

# 需要停止按 Ctrl+C
```

启动之后，可以正常接收消息但不会响应群消息。参考下方 [修改配置](#config) 进行配置，以便响应特定群聊。

下面代码为第二次运行：你可以通过命令行参数选择模型，默认是不选择，这样你配置了什么参数就跑什么模型。正因如此你需要配置前面所说四种模型中的至少一种（当然也可以都配置，想跑那个模型就选什么参数）, 然后就可以开始使用你的机器人了。

```sh
python main.py
# 建议首先尝试运行如下代码
python main.py -c 2
# 需要停止按 Ctrl+C
```

如果你配置了多个模型（不需要将其他配置注释或者移除），下面的内容才对你有帮助否则略过，通过 `python main.py -h` 通过参数可以选择要跑的模型。

```sh
# 查看帮助
python main.py -h
#optional arguments:
#  -h, --help            show this help message and exit
#  -c C, --chat_model C  选择要使用的AI模型，默认不选择，可选参数：1. tigerbot 模型 2. chatgpt 模型 3. 讯飞星火模型 4. chatglm 模型
```

```sh
# 例: 我想运行选择chatgpt的机器人
python main.py -c 2

# 需要停止按 Ctrl+C
```

> python main.py -c C 其中参数 C 可选择如下所示
>
>> 2. ChatGPT-4o-mini
>> 3. ChatGPT-4o
>> 4. moonshot
>> 6. deepseek
>>

7. 运行遇到的问题

- 如果出现如下报错 "No Such File or Directory" , 可在报错的目录创建该文件
  ![定时聊天总结](./doc/InitLOGGERERROR.png)
- 其余问题，关注原作者公众号“碲矿”寻找解决方法

8. 停止

不要那么粗暴，温柔点儿；

不要直接关闭窗口，温柔点儿。

输入：`Ctrl+C`。否则，会出现各种奇怪问题。

## 修改配置的相关内容

ℹ️ *修改配置后，需要重新启动，以便让配置生效。*

配置文件 `config.yaml` 是运行程序后自动从模板复制过来的，功能默认关闭。

#### 响应被 @ 消息

为了响应群聊消息，需要添加相应的 `roomId`。

第一次运行的时候，可以在手机上往需要响应的群里发消息，打印的消息中方括号里的就是；多个群用 `,` 分隔。

```yaml
groups:
  enable: [] # 允许响应的群 roomId，大概长这样：2xxxxxxxxx3@chatroom, 多个群用 `,` 分隔
```

#### 配置 AI 模型

为了使用 AI 模型，需要对相应模型并进行配置。

使用 ChatGLM 见注意事项 [README.MD](base/chatglm/README.MD)

```yaml
chatgpt:  # -----chatgpt配置这行不填-----
  key:  # 填写你 ChatGPT 的 key
  api: https://api.openai.com/v1  # 如果你不知道这是干嘛的，就不要改
  proxy:  # 如果你在国内，你可能需要魔法，大概长这样：http://域名或者IP地址:端口号
  prompt: 你是智能聊天机器人，你叫 wcferry  # 根据需要对角色进行设定

chatglm:  # -----chatglm配置这行不填-----
  key: sk-012345678901234567890123456789012345678901234567 # 这个应该不用动
  api: http://localhost:8000/v1  # 根据自己的chatglm地址修改
  proxy:  # 如果你在国内，你可能需要魔法，大概长这样：http://域名或者IP地址:端口号
  prompt: 你是智能聊天机器人，你叫小薇  # 根据需要对角色进行设定
  file_path: C:/Pictures/temp  #设定生成图片和代码使用的文件夹路径

tigerbot:  # -----tigerbot配置这行不填-----
  key:  # key
  model:  # tigerbot-7b-sft

# 抓取方式详见文档：https://www.bilibili.com/read/cv27066577
xinghuo_web:  # -----讯飞星火web模式api配置这行不填-----
  cookie:  # cookie
  fd:  # fd
  GtToken:  # GtToken
  prompt: 你是智能聊天机器人，你叫 wcferry。请用这个角色回答我的问题  # 根据需要对角色进行设定

bard: # -----bard配置这行不填-----
  api_key: # api-key 创建地址：https://ai.google.dev/pricing，创建后复制过来即可
  model_name: gemini-pro # 新模型上线后可以选择模型
  proxy: http://127.0.0.1:7890  # 如果你在国内，你可能需要魔法，大概长这样：http://域名或者IP地址:端口号
  # 提示词尽可能用英文，bard对中文提示词的效果不是很理想，下方提示词为英语老师的示例，请按实际需要修改,默认设置的提示词为谷歌创造的AI大语言模型
  # I want you to act as a spoken English teacher and improver. I will speak to you in English and you will reply to me in English to practice my spoken English. I want you to keep your reply neat, limiting the reply to 100 words. I want you to strictly correct my grammar mistakes, typos, and factual errors. I want you to ask me a question in your reply. Now let's start practicing, you could ask me a question first. Remember, I want you to strictly correct my grammar mistakes, typos, and factual errors.
  prompt: You am a large language model, trained by Google.
```

## 拓展功能配置修改

#### 更改定时总结的时间

通常不需要对该项进行修改。

在 `main.py` 里的  `main` 函数中，通过 `robot.onEveryTime` 传递 `robot.saveAutoSummary` 方法，即可设置定时总结。

```python
# 在每天晚上 7点（19:00）进行一次定时总结，总结的时间范围是 19:00 的前 7 个小时（12:00 - 19:00）
robot.onEveryTime("19:00", robot.saveAutoSummary, time_hours=7)
```

#### 聊天数据统计

在 `main.py` 里的  `main` 函数中，通过 `robot.onEveryTime` 传递 `robot.periodic_statistics` 方法，即可设置定时聊天数据统计。

```
# robot.onEveryTime("20:00", robot.periodic_statistics())
```

#### 权限管理

可以通过 `/getid` 命令得到 wxid 以及 roomid，随后在 `wechat_bot.db` 的数据库的 permission表 中设置权限。

![定时聊天总结](./doc/permission.png)

在roomid列填入wxid或者roomid来设置权限：

- 用户或群组拥有admin权限时，可以使用所有功能；
- 用户或群组拥有chat权限时，用户能在群聊中@bot进行对话；
- 群组拥有autoSummary时，会自动发送定时聊天总结；
- 用户或群组拥有callSummary权限时，能够使用 `@bot /总结1 `进行调用聊天总结;
- 群组拥有periodStat权限时，会自动发送聊天数据统计数据；

## HTTP

如需要使用 HTTP 接口，请参考:

* [wcfrust](https://github.com/lich0821/wcf-client-rust)（基于 Rust），开箱即用：[快速开始](https://github.com/lich0821/wcf-client-rust?tab=readme-ov-file#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)。
* GoHttp（基于 Go），参考 [GoHttp README.MD](https://github.com/lich0821/WeChatFerry/blob/master/clients/gohttp/README.md)
* ~~wcfhttp（基于 Python）~~
  ❗ **wcfhttp 不再维护，有需要可以使用 [WcfRust](https://github.com/lich0821/wcf-client-rust) 或者 [GoHttp](clients/gohttp/README.md)。**

## Copyright

如果你喜欢这个项目，可以关注原作者的微信公众号或赞助原作者：

| ![碲矿](https://s2.loli.net/2023/09/25/fub5VAPSa8srwyM.jpg) | ![赞赏](https://s2.loli.net/2023/09/25/gkh9uWZVOxzNPAX.jpg) |
| :-------------------------------------------------------: | :-------------------------------------------------------: |
|                 后台回复 `WCF` 加群交流                 |                      如果你觉得有用                      |

## Contributors

<a href="https://github.com/lich0821/WeChatRobot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=lich0821/WeChatRobot" />
</a>

<a href="https://github.com/HK-Artificial-Intelligence-Association/WechatBot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HK-Artificial-Intelligence-Association/WechatBot" /></a>
