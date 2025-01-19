# -*- coding: utf-8 -*-
# UTF-8 编码

import logging# 导入日志库，用于记录日志信息
import re# 导入正则表达式库，用于文本匹配和处理
import time# 导入时间库，用于处理时间相关的功能
import xml.etree.ElementTree as ET # 用于处理XML格式数据，如微信消息中的数据
from queue import Empty # 从队列库导入Empty异常，用于处理队列空异常
from multiprocessing import Queue
import threading
from sympy import content # 导入线程库，用于创建并运行线程
import json
import os
from datetime import datetime



# 导入项目内部的其他模块和功能
from base.func_zhipu import ZhiPu# 智谱功能，可能是定制化的功能模块
from wcferry import Wcf, WxMsg # type: ignore # wcferry库提供的基础类和消息类，用于微信通讯
from base.func_bard import BardAssistant# Bard助手，可能是另一种AI对话助手
from base.func_chatglm import ChatGLM # ChatGLM对话模型，可能是基于GPT类似的语言模型
from base.func_chatgpt import ChatGPT # ChatGPT对话模型
from base.func_chatgptt import ChatGPTt
from base.func_moonshot import Moonshot
from base.func_deepseek import DeepSeek
from base.func_Qwen import Qwen
from base.func_chengyu import cy # 成语处理功能
from base.func_news import News# 新闻功能模块
from base.func_tigerbot import TigerBot # 虎型机器人功能模块
from base.func_xinghuo_web import XinghuoWeb # 星火Web功能，可能提供网络相关服务
from configuration import Config # 配置管理模块
from constants import ChatType # 常量定义模块，定义了聊天类型
from job_mgmt import Job # 作业管理基类，`Robot`类继承自此
from db import store_message, insert_roomid, store_summary # 导入 db.py 中的 store_message 函数,add_unique_roomids_to_roomid_table 函数
from db import fetch_messages_from_last_some_hour, fetch_summary_from_db, collect_stats_in_room
from db import fetch_permission_from_db, fetch_roomid_list, get_auto_summary_settings
from utils.yaml_utils import update_yaml
from tools import *
__version__ = "39.0.10.1" # 版本号


class Robot(Job):#robot类继承自job类
    """个性化自己的机器人，注释
    """

    def __init__(self, config: Config, wcf: Wcf, chat_type: int) -> None:
        # 类的构造函数，初始化机器人，构造方法在类实例化时会自动调用
        super().__init__()
        self.wcf = wcf # 微信通讯功能实例
        self.config = config # 配置信息
        self.LOG = logging.getLogger("Robot") # 日志记录器
        self.wxid = self.wcf.get_self_wxid()# 获取自己的微信ID
        self.allContacts = self.getAllContacts()# 获取所有联系人
        self.active = True # 状态标识，True为活跃，False为关闭
        self.model_type = None  # 初始化 model_type
        self.calltime = 5 # 初始化调用次数
        self.newsQueue = Queue() # 初始化新闻队列
        self.stopEvent = threading.Event()
        self.permissions = fetch_permission_from_db()
        self.model_value = chat_type # 当前模型编号

    # 根据聊天类型初始化对应的聊天模型
        if ChatType.is_in_chat_types(chat_type):
         # 聊天类型检查，如果指定类型在支持的类型列表中
            if chat_type == ChatType.TIGER_BOT.value and TigerBot.value_check(self.config.TIGERBOT):
                self.chat = TigerBot(self.config.TIGERBOT)
            elif chat_type == ChatType.CHATGPT.value and ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
                self.model_type = 'ChatGPT-gpt-3.5-turbo'
            elif chat_type == ChatType.CHATGPTt.value and ChatGPTt.value_check(self.config.CHATGPTt):
                self.chat = ChatGPTt(self.config.CHATGPTt)
                self.model_type = 'ChatGPT-gpt-4o-2024-05-13'
            elif chat_type == ChatType.MOONSHOT.value and Moonshot.value_check(self.config.MOONSHOT):
                self.chat = Moonshot(self.config.MOONSHOT)
                self.model_type = 'Moonshot-moonshot-v1-32k'
            elif chat_type == ChatType.QWEN.value and Qwen.value_check(self.config.QWEN):
                self.chat = Qwen(self.config.QWEN)
                self.model_type = 'Qwen-qwen-plus'
            elif chat_type == ChatType.XINGHUO_WEB.value and XinghuoWeb.value_check(self.config.XINGHUO_WEB):
                self.chat = XinghuoWeb(self.config.XINGHUO_WEB)
            elif chat_type == ChatType.CHATGLM.value and ChatGLM.value_check(self.config.CHATGLM):
                self.chat = ChatGLM(self.config.CHATGLM)
            elif chat_type == ChatType.BardAssistant.value and BardAssistant.value_check(self.config.BardAssistant):
                self.chat = BardAssistant(self.config.BardAssistant)
            elif chat_type == ChatType.ZhiPu.value and ZhiPu.value_check(self.config.ZHIPU):
                self.chat = ZhiPu(self.config.ZHIPU)
            elif chat_type == ChatType.DeepSeek.value and DeepSeek.value_check(self.config.DEEPSEEK):
                self.chat = DeepSeek(self.config.DEEPSEEK)
                self.model_type = 'DeepSeek-deepseek-chat'
            else:
                self.LOG.warning("未配置模型")
                self.chat = None # 如果没有合适的配置，将聊天模型设置为None
                self.model_value = 0 # 配置模型失败，切换至未设置的默认值
        else:
            # 如果聊天类型不在支持的列表中，也尝试进行初始化
            # 类似的逻辑处理...
            if TigerBot.value_check(self.config.TIGERBOT):
                self.chat = TigerBot(self.config.TIGERBOT)
                self.model_value = ChatType.TIGER_BOT.value
            elif ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
                self.model_value = ChatType.CHATGPT.value
            elif ChatGPTt.value_check(self.config.CHATGPTt):
                self.chat = ChatGPTt(self.config.CHATGPTt)
                self.model_value = ChatType.CHATGPTt.value
            elif Moonshot.value_check(self.config.MOONSHOT):
                self.chat = Moonshot(self.config.MOONSHOT)
                self.model_value = ChatType.MOONSHOT.value
            elif Qwen.value_check(self.config.QWEN):
                self.chat = Qwen(self.config.QWEN)
                self.model_value = ChatType.QWEN.value
            elif XinghuoWeb.value_check(self.config.XINGHUO_WEB):
                self.chat = XinghuoWeb(self.config.XINGHUO_WEB)
                self.model_value = ChatType.XINGHUO_WEB.value
            elif ChatGLM.value_check(self.config.CHATGLM):
                self.chat = ChatGLM(self.config.CHATGLM)
                self.model_value = ChatType.CHATGLM.value
            elif BardAssistant.value_check(self.config.BardAssistant):
                self.chat = BardAssistant(self.config.BardAssistant)
                self.model_value = ChatType.BardAssistant.value
            elif ZhiPu.value_check(self.config.ZhiPu):
                self.chat = ZhiPu(self.config.ZhiPu)
                self.model_value = ChatType.ZhiPu.value
            elif DeepSeek.value_check(self.config.DEEPSEEK):
                self.chat = DeepSeek(self.config.DEEPSEEK)
                self.model_value = ChatType.DeepSeek.value
            else:
                self.LOG.warning("未配置模型")
                self.chat = None
                self.model_value = 0

        self.LOG.info(f"已选择: {self.chat}")
        #self.current_msg = None
        self.setScheduleSummary()# 设置总结发送时间表

    @staticmethod
    #标记一个静态方法
    def value_check(args: dict) -> bool:
        if args:
            return all(value is not None for key, value in args.items() if key != 'proxy')
        return False

    def toAt(self, msg: WxMsg) -> bool:
        """处理被 @ 消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        return self.toChitchat(msg)

    def toChengyu(self, msg: WxMsg) -> bool:
        """
        处理成语查询/接龙消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        status = False
        texts = re.findall(r"^([#|?|？])(.*)$", msg.content)
        # [('#', '天天向上')]
        if texts:
            flag = texts[0][0]
            text = texts[0][1]
            if flag == "#":  # 接龙
                if cy.isChengyu(text):
                    rsp = cy.getNext(text)
                    if rsp:
                        self.sendTextMsg(rsp, msg.roomid)
                        status = True
            elif flag in ["?", "？"]:  # 查词
                if cy.isChengyu(text):
                    rsp = cy.getMeaning(text)
                    if rsp:
                        self.sendTextMsg(rsp, msg.roomid)
                        status = True

        return status

    def toChitchat(self, msg: WxMsg) -> bool:
        """闲聊，接入 ChatGPT
        """
        if not self.chat:  # 没接 ChatGPT，固定回复
            rsp = "你@我干嘛？"
        else:  # 接了 ChatGPT，智能回复 # 如果不是开启或关闭机器人的命令，而是普通的消息，则进行智能回复
             # 使用正则表达式将消息内容中的@提及和空格替换为空，只保留消息内容
            q = re.sub(r"@.*?[\u2005|\s]", "", msg.content).replace(" ", "")
            # 调用 ChatGPT 模型的 get_answer 方法，传入用户的问题和消息的发送者 ID 或群组 ID（根据消息类型确定）
            rsp = self.chat.get_answer(q, (msg.roomid if msg.from_group() else msg.sender))

        if rsp:
            if msg.from_group():
                self.sendTextMsg(rsp, msg.roomid, msg.sender)
            else:
                self.sendTextMsg(rsp, msg.sender)

            return True
        else:
            self.LOG.error(f"无法从 ChatGPT 获得答案")
            return False
        
    def processMsg(self, msg: WxMsg) -> None:
        """当接收到消息的时候，会调用本方法。"""
        # 构建消息数据字典
        #print(msg)
        

        msg_dict = {
             'id': str(msg.id),
             'type': msg.type,
             'sender': msg.sender,
             'roomid': msg.roomid,
             'content': msg.content,
             'thumb': getattr(msg, 'thumb', ''),
             'extra': getattr(msg, 'extra', ''),
             'sign': getattr(msg, 'sign', ''),
             'ts': str(getattr(msg, 'ts', '')),
             'xml': getattr(msg, 'xml', ''),
             'is_self': int(msg.from_self()),  # 使用方法获取值
             'is_group': int(msg.from_group())  # 使用方法获取值
        }

        print(msg_dict)

        """存储消息到message表"""
        store_message(msg_dict)

        # 判断消息类型是否为10000
        if msg_dict['type'] == 10000 and msg_dict['is_group'] == 1 and "邀请你" in msg_dict['content']:
            # 如果是群组消息，调用insert_roomid函数，传入roomid
            insert_roomid(msg_dict['roomid'])
            # 在插入roomid之后调用update_yaml来更新配置文件
            update_yaml()
            # 重新载入机器人的config
            self.config.reload()

            self.sendTextMsg(
                f"我是兔狲机器人，小狲狲，你好鸭。当前我使用的模型是：{self.model_type}\n"
                "目前我有的功能如下：\n"
                "1. @我，我可以回答你的问题哦\n"
                "2. /总结 - 获取聊天总结，我可以帮你总结2小时的聊天内容哦\n"
                "3. /聊天统计 - 获取聊天数据统计，我可以向你展示最近24小时的发言排行榜哦\n"
                "4. /help - 获取帮助信息\n"
                "5. 后续功能还在开发中，敬请期待！\n",
                msg_dict["roomid"]
            )

        # 新的判断条件，消息类型为1，is_group为1，并且content中包含'/func'
        if msg_dict['type'] == 1 and msg_dict['is_group'] == 1 and '/help' in msg_dict['content'] and msg.is_at(self.wxid):
            self.sendTextMsg(
                f"我是兔狲机器人，小狲狲，你好鸭。当前我使用的模型是：{self.model_type}\n"
                "你可以使用以下命令：\n"
                "1. /help - 获取帮助信息\n"
                "2. /总结1 - 获取2小时内分话题式聊天总结\n"
                "3. /总结2 - 获取2小时内不话题式聊天总结\n"
                "4. /聊天统计 - 获取聊天数据统计\n"
                "5. /文章总结 url - 获取文章的摘要\n"
                "6. /getid - 获取当前群聊或用户的roomid与wxid\n"
                "7. 后续功能还在开发中，敬请期待！\n",
                msg_dict["roomid"]
            )

        elif is_card_article(msg.content):
            if self.hasPermission(msg.roomid, "articleSummary") or self.hasPermission(msg.sender, "articleSummary"):
                print("开始执行卡片文章总结")
                self.handle_card_article_summary_request(msg)
        elif (msg.is_at(self.wxid) and msg_dict['is_group'] == 1) or msg_dict['is_group'] != 1:
            content = msg.content.strip()
            # print(content)
            # 检查是否是控制命令或是否包含“总结”关键字

            if content == "/sun":
                if self.hasPermission(msg.roomid, "admin") or self.hasPermission(msg.sender, "admin"): # 验证管理权限
                    self.handle_open(msg)
            elif content == "/nus":
                if self.hasPermission(msg.roomid, "admin") or self.hasPermission(msg.sender, "admin"):
                    self.handle_close(msg)
            elif "/总结" in content and msg_dict['type'] != 49:
                if self.hasPermission(msg.roomid, "callSummary"):
                    self.handle_summary_request(msg)
            elif "/change" in content:
                if self.hasPermission(msg.roomid, "admin") or self.hasPermission(msg.sender, "admin"):
                    self.handle_change_request(msg)
            elif "/文章总结" in content:
                if self.hasPermission(msg.roomid, "articleSummary") or self.hasPermission(msg.sender, "articleSummary"):
                    self.handle_url_article_summary_request(msg)
            elif "/getid" in content:
                self.handle_get_id_request(msg)
            elif "/聊天统计" in content:
                self.handle_statistics_request(msg)
            elif "/群聊激活" in content:
                if self.hasPermission(msg.sender, "admin"):
                    self.handle_activation_request(msg)
            elif self.active:
                # 如果机器人处于活跃状态，则处理其他消息
                self.handle_other_messages(msg)

    def handle_change_request(self, msg):
        content = msg.content
        print("消息内容:", content)  # 打印消息内容以调试

            # 尝试获取消息最后的数字
        match = re.search(r'\d+$', content) # 正则表达式 \d+$ 来匹配字符串末尾的连续数字。\d+ 表示一个或多个数字，$ 表示字符串的末尾
        if match:
            chat_type = int(match.group())
            print("提取的数字是:", chat_type)
            self.change_model(chat_type)
        else:
            chat_type = None
            print("没有找到匹配的数字")

    def change_model(self, chat_type: int):
        previous_value = chat_type
        self.model_value = chat_type
        if chat_type and ChatType.is_in_chat_types(chat_type):
            if chat_type == ChatType.CHATGPT.value and ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
                self.model_type = 'ChatGPT-gpt-4o-mini'
            elif chat_type == ChatType.CHATGPTt.value and ChatGPTt.value_check(self.config.CHATGPTt):
                self.chat = ChatGPTt(self.config.CHATGPTt)
                self.model_type = 'ChatGPT-gpt-4o-32k'
            elif chat_type == ChatType.MOONSHOT.value and Moonshot.value_check(self.config.MOONSHOT):
                self.chat = Moonshot(self.config.MOONSHOT)
                self.model_type = 'Moonshot-moonshot-v1-32k'
            elif chat_type == ChatType.QWEN.value and Qwen.value_check(self.config.QWEN):
                self.chat = Qwen(self.config.QWEN)
                self.model_type = 'Qwen-qwen-plus'
            elif chat_type == ChatType.DeepSeek.value and DeepSeek.value_check(self.config.DEEPSEEK):
                self.chat = DeepSeek(self.config.DEEPSEEK)
                self.model_type = 'DeepSeek-deepseek-chat'
            else:
                self.LOG.warning("未配置模型")
                self.chat = None  # 如果没有合适的配置，将聊天模型设置为None
                self.model_type = None
                self.model_value = previous_value
        else:
            # 如果聊天类型不在支持的列表中，也尝试进行初始化
            if ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
                self.model_value = ChatType.CHATGPT.value
            elif ChatGPTt.value_check(self.config.CHATGPTt):
                self.chat = ChatGPTt(self.config.CHATGPTt)
                self.model_value = ChatType.CHATGPTt.value
            elif Moonshot.value_check(self.config.MOONSHOT):
                self.chat = Moonshot(self.config.MOONSHOT)
                self.model_value = ChatType.MOONSHOT.value
            elif Qwen.value_check(self.config.QWEN):
                self.chat = Qwen(self.config.QWEN)
                self.model_value = ChatType.QWEN.value
            else:
                self.LOG.warning("切换模型失败")
                self.chat = None
                self.model_value = previous_value
    
        self.LOG.info(f"已选择: {self.chat}")


    def handle_summary_request(self, msg: WxMsg, time_hours=2):
        """处理总结请求,使用GPT生成总结，默认提取2小时的聊天记录"""
        messages_withwxid = fetch_messages_from_last_some_hour(msg.roomid, time_hours)
        messages = []
        valid_name = set()
        for message_withwxid in messages_withwxid:
            sender=self.wcf.get_alias_in_chatroom(message_withwxid["sender_id"], msg.roomid)
            # 将messages里的wxid替换成wx昵称，get_info_by_wxid因不明原因出错，故改用get_alias_in_chatroom方法
            if sender == "": # 将messages里的wxid替换成wx昵称
                sender = message_withwxid["sender_id"]
                self.LOG.info(f"{sender}昵称获取错误，已使用wxid替换")
            elif sender not in valid_name:
                self.LOG.info(f"{sender}昵称获取成功")
                valid_name.add(sender)

            message = {
                "content": message_withwxid["content"],
                "sender":sender,
                "time": message_withwxid["time"]
            }
            messages.append(message)

        if messages:
            if "/总结1" in msg.content:
                summary = self.chat.get_summary1(messages, msg.roomid)
            elif "/总结2" in msg.content:
                summary = self.chat.get_summary2(messages, msg.roomid)
            else:
                print("未知的总结请求类型。", msg.sender)
                return

            # 发送总结到微信
            if msg.from_group() and self.calltime > 0:
                self.sendTextMsg(summary, msg.roomid, msg.sender)
                self.sendTextMsg(f"本群总结调用次数还剩{self.calltime}次", msg.roomid, msg.sender)
            else:
                self.sendTextMsg(summary, msg.roomid, msg.sender)
                self.sendTextMsg(f"本群总结调用次数还剩{self.calltime}次", msg.roomid, msg.sender)
            self.calltime -= 1 # 自减并提示 后续需要加入大于0判断以及每日重置
        else:
            print("过去2小时内没有足够的消息来生成总结。", msg.sender)



    def handle_open(self, msg: WxMsg):
        """处理开启机器人的命令"""
        if not self.active:
            self.active = True
            if msg.from_group():
        # 如果在群里被 @，如果消息来自群聊
                if msg.roomid not in self.config.GROUPS:  # 不在配置的响应的群列表里，忽略
                    return
                self.sendTextMsg("我是兔狲机器人，小狲狲，你好鸭", msg.roomid)
            else:
                self.sendTextMsg("我是兔狲机器人，小狲狲，你好鸭", msg.sender)
            self.LOG.info("机器人已开启。")
    
    def handle_close(self, msg: WxMsg):
        """处理关闭机器人的命令"""
        if self.active:
            self.active = False
            if msg.from_group():
        # 如果在群里被 @，如果消息来自群聊
                if msg.roomid not in self.config.GROUPS:  # 不在配置的响应的群列表里，忽略
                    return
                self.sendTextMsg("拜拜辣！有事再叫狲狲", msg.roomid)
            else:
                self.sendTextMsg("拜拜辣！有事再叫狲狲", msg.sender)
            self.LOG.info("机器人已关闭。")
    
    def handle_other_messages(self, msg: WxMsg)-> None:
        """处理除开启和关闭外的其他消息"""
        # 这里可以添加对其他类型消息的处理逻辑
        # 处理群聊消息
        if msg.from_group():
        # 如果在群里被 @，如果消息来自群聊
            if msg.roomid not in self.config.GROUPS:  # 不在配置的响应的群列表里，忽略
                return

            if msg.is_at(self.wxid):  # 如果机器人被@
                self.LOG.info(f"触发toAt{msg.content}")
                if self.hasPermission(msg.roomid,"chat"): self.toAt(msg) # 聊天权限判断
            else:  # 其他群聊消息
                self.toChengyu(msg)

            return  # 处理完群聊信息后，跳出方法

        # 处理非群聊信息
        if msg.type == 37:  # 好友请求
            self.autoAcceptFriendRequest(msg)

        elif msg.type == 10000:  # 系统信息
            self.sayHiToNewFriend(msg)

        elif msg.type == 0x01:  # 文本消息
            if msg.from_self():
                if msg.content == "^更新$":
                    self.config.reload()
                    self.LOG.info("已更新")
            elif msg.sender.startswith('gh_'): # 过滤关注公众号时 公众号的消息
                return
            else:
                self.toChitchat(msg)  # 闲聊

    
    def onMsg(self, msg: WxMsg) -> int:
        try:
            self.LOG.info(msg)  # 打印信息
            self.processMsg(msg)
        except Exception as e:
            self.LOG.error(e)

        return 0

    def enableRecvMsg(self) -> None:
        self.wcf.enable_recv_msg(self.onMsg)

    def enableReceivingMsg(self) -> None:
        def innerProcessMsg(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    self.LOG.info(msg)
                    self.processMsg(msg)
                except Empty:
                    continue  # Empty message# 如果消息队列为空，则继续等待新消息
                except Exception as e:
                    self.LOG.error(f"Receiving message error: {e}")

        self.wcf.enable_receiving_msg()# 启动Wcf的消息接收功能
        threading.Thread(target=innerProcessMsg, name="GetMessage", args=(self.wcf,), daemon=True).start()

    def sendTextMsg(self, msg: str, receiver: str, at_list: str = "") -> None:
        """ 发送消息
        :param msg: 消息字符串
        :param receiver: 接收人wxid或者群id
        :param at_list: 要@的wxid, @所有人的wxid为:notify@all
        """
        # msg 中需要有 @ 名单中一样数量的 @
        ats = ""
        if at_list:
            if at_list == "notify@all":  # @所有人
                ats = " @所有人"
            else:
                wxids = at_list.split(",")
                for wxid in wxids:
                    # 根据 wxid 查找群昵称
                    ats += f" @{self.wcf.get_alias_in_chatroom(wxid, receiver)}"

        # {msg}{ats} 表示要发送的消息内容后面紧跟@，例如 北京天气情况为：xxx @张三
        if ats == "":
            self.LOG.info(f"To {receiver}: {msg}")
            self.wcf.send_text(f"{msg}", receiver, at_list)
        else:
            self.LOG.info(f"To {receiver}: {ats}\r{msg}")
            self.wcf.send_text(f"{ats}\n\n{msg}", receiver, at_list)

    def getAllContacts(self) -> dict:
        """
        获取联系人（包括好友、公众号、服务号、群成员……）
        格式: {"wxid": "NickName"}
        """
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName FROM Contact;")
        return {contact["UserName"]: contact["NickName"] for contact in contacts}

    def keepRunningAndBlockProcess(self) -> None:
        """
        保持机器人运行，不让进程退出
        """
        while True:
            self.runPendingJobs()
            time.sleep(1)

    def autoAcceptFriendRequest(self, msg: WxMsg) -> None:
        try:
            xml = ET.fromstring(msg.content)
            v3 = xml.attrib["encryptusername"]
            v4 = xml.attrib["ticket"]
            scene = int(xml.attrib["scene"])
            self.wcf.accept_new_friend(v3, v4, scene)

        except Exception as e:
            self.LOG.error(f"同意好友出错：{e}")

    def sayHiToNewFriend(self, msg: WxMsg) -> None:
        nickName = re.findall(r"你已添加了(.*)，现在可以开始聊天了。", msg.content)
        if nickName:
            # 添加了好友，更新好友列表
            self.allContacts[msg.sender] = nickName[0]
            self.sendTextMsg(f"Hi {nickName[0]}，我自动通过了你的好友请求。", msg.sender)

    def newsReport(self) -> None:
        receivers = self.config.NEWS
        if not receivers:
            return

        news = News().get_important_news()
        for r in receivers:
            self.sendTextMsg(news, r)

    def sendWeatherReport(self) -> None:
        """发送天气预报给指定的接收者"""
        receivers = ["filehelper"]  # 指定接收者，可以根据需要进行修改

        # 模拟获取天气预报数据
        report = "这就是获取到的天气情况了"

        # 发送天气预报
        for receiver in receivers:
            self.sendTextMsg(report, receiver)
    
    def sendAutoSummary(self,time_hours=2) -> None:
        """自动总结，默认总结2小时的聊天记录"""
        receivers = fetch_roomid_list("autoSummary")  # 指定接收者，可以根据需要进行修改
        developers = fetch_roomid_list("admin")  # 指定调试群组，将总结内容发送至群组
        for receiver in receivers:
            messages_withwxid = fetch_messages_from_last_some_hour(roomid = receiver, time_hours=time_hours)
            # 将messages里的wxid替换成wx昵称
            messages = []
            valid_name = set()
            for message_withwxid in messages_withwxid:
                sender=self.wcf.get_alias_in_chatroom(message_withwxid["sender_id"], receiver)
                if sender == "": # 将messages里的wxid替换成wx昵称
                    sender = message_withwxid["sender_id"]
                    self.LOG.info(f"{sender}昵称获取错误，已使用wxid替换")
                elif sender not in valid_name:
                    self.LOG.info(f"{sender}昵称获取成功")
                    valid_name.add(sender)
                message = {
                    "content": message_withwxid["content"],
                    "sender":sender,
                    "time": message_withwxid["time"]
                }
                messages.append(message)

            summary = self.chat.get_summary1(messages, receiver)# 生成聊天总结
            self.sendTextMsg(summary, receiver)# 发送总结内容
            if developers: # 发送调试消息
                self.sendTextMsg(summary, developers[0])

    def setScheduleSummary(self):
        settings = get_auto_summary_settings()

        for row in settings:
            room_id, summary_time, summary_model = row
            # 设置默认值
            if summary_time is None:
                summary_time = "20:00"
            
            self.onEveryTime(
                summary_time, self.genAndsendSummary,
                room_id, summary_model, time_hours = 24
            )
            self.LOG.info(f"成功设置群聊{room_id}于{summary_time}的自动总结")
        return
    
    def genAndsendSummary(self, receiver, summary_model = None, time_hours = 24):
        developers = fetch_roomid_list("admin")  # 指定调试群组，将总结内容发送至群组
        previous_value = self.model_value
        if summary_model: self.change_model(summary_model)# 切换至群聊设置的总结模型
        messages_withwxid = fetch_messages_from_last_some_hour(roomid = receiver, time_hours=time_hours)
        # 将messages里的wxid替换成wx昵称
        messages = []
        valid_name = set()
        for message_withwxid in messages_withwxid:
            sender=self.wcf.get_alias_in_chatroom(message_withwxid["sender_id"], receiver)
            if sender == "": # 将messages里的wxid替换成wx昵称
                sender = message_withwxid["sender_id"]
                self.LOG.info(f"{sender}昵称获取错误，已使用wxid替换")
            elif sender not in valid_name:
                self.LOG.info(f"{sender}昵称获取成功")
                valid_name.add(sender)
            message = {
                "content": message_withwxid["content"],
                "sender":sender,
                "time": message_withwxid["time"]
            }
            messages.append(message)

        summary = self.chat.get_summary1(messages, receiver)# 生成聊天总结
        self.sendTextMsg(summary, receiver)# 发送总结内容
        if developers: # 发送调试消息
            self.sendTextMsg(summary, developers[0])
        if summary_model: self.change_model(previous_value) # 切换回原本模型
        return
    
    def saveAutoSummary(self, time_hours=2):
        """
        生成并保存聊天总结
        """
        receivers = fetch_roomid_list("autoSummary")  # 指定总结群聊，可以根据需要进行修改
        if not receivers: print("没有指定进行总结的群聊")
        for receiver in receivers:
            messages_withwxid = fetch_messages_from_last_some_hour(receiver, time_hours)
            if not messages_withwxid:continue # 如果没有聊天记录则跳过
            messages = []
            valid_name = set()
            for message_withwxid in messages_withwxid:
                sender=self.wcf.get_alias_in_chatroom(message_withwxid["sender_id"], receiver)
                if sender == "": # 将messages里的wxid替换成wx昵称
                    sender = message_withwxid["sender_id"]
                    self.LOG.info(f"{sender}昵称获取错误，已使用wxid替换")
                elif sender not in valid_name:
                    self.LOG.info(f"{sender}昵称获取成功")
                    valid_name.add(sender)
                message = {
                    "content": message_withwxid["content"],
                    "sender":sender,
                    "time": message_withwxid["time"]
                }
                messages.append(message)

            summary = self.chat.get_summary1(messages,roomid=receiver)
            store_summary(receiver, summary, int(datetime.now().timestamp()))

        return []
    def sendDailySummary(self) -> None:# 以后会新增参数或者函数（sendWeeklySummary）
        '''发送每日总结并存入数据库'''
        receivers = fetch_roomid_list("autoSummary")  # 指定总结群聊，可以根据需要进行修改
        developers = fetch_roomid_list("admin")  # 指定调试群组，将总结内容发送至群组
        if not receivers:print("没有指定进行总结的群聊")
        for receiver in receivers:
            summaries = fetch_summary_from_db(receiver, 'partly')
            if summaries:
                summary = self.chat.get_summary_of_partly(summaries, receiver)
                ts = int(datetime.now().timestamp())
                store_summary(receiver, summary, ts, type='daily') # 存入每日数据库
                self.sendTextMsg(summary, receiver) # 若需要@所有人，添加参数at_list == "notify@all"即可
                self.LOG.info(f"已发送{receiver}的每日总结")
                if developers: # 发送调试消息
                    self.sendTextMsg(summary, developers[0])
            else:
                print("过去没有足够的分段总结内容来生成总结。", receiver)
        

    def process_queue(self, url):
        """若队列为空，则抓取消息；否则，每隔十秒输出消息"""
        while not self.stopEvent.is_set():
            if self.newsQueue.empty():
                print("News queue is empty, fetching data...")
                try:
                    news = fetch_news_json(url)
                    if isinstance(news, list):
                        for new in news:
                            if isinstance(new, dict):
                                required_keys = ['type', 'content', 'base64', 'receiver', 'url']  # 假设这些是必需的键
                                if all(key in new for key in required_keys):  # 确保字典包含所有必需的键
                                    self.newsQueue.put(new)  # 加入队列
                                    if new["base64"]:
                                        shortnew = {
                                            "type": new["type"],
                                            "content": new["content"],
                                            "base64": new["base64"][:10],
                                            "receiver": new["receiver"],
                                            "url": new["url"]
                                        }# 创建一个包含部分数据的字典
                                    else: shortnew = new
                                    print(f"已将图片消息加入队列：{shortnew}")
                                    self.LOG.info(f"已将图片消息加入队列：{shortnew}")
                                else:
                                    print(f"忽略无效新闻：{new}，缺少必要键")
                            else:
                                print(f"忽略非字典项：{new}")
                    else:
                        print(f"从URL:{url}获取的数据不是列表：{news}")
                except Exception as e:
                    print(f"Failed to fetch data: {e}")
                self.stopEvent.wait(timeout=60)  # 等待60秒或直到事件被设置
            else:
                self.sendTopNews()
                print("Send news successfully!")


        # self.sendTextMsg("测试", receiver)
        # self.wcf.send_image("https://t7.baidu.com/it/u=4036010509,3445021118&fm=193&f=GIF", receiver)



    def sendTopNews(self) -> None:
        '''轮询消息与发送'''
        while self.newsQueue.empty() == False: # 如果队列不为空
            new = self.newsQueue.get()
            if new['type'] == "text":
                print(f"发送{new['content']}")
                self.sendTextMsg(new['content'], new['receiver'])
            elif new['type'] == "image":
                # 将base64编码的图片保存为文件,并得到相对路径
                path = base64_image_compress(new['base64'])
                # path = convert_png_base64_to_webp(new['base64'])
                # path=base64_to_image(new['base64'])
                abspath = os.path.abspath(path) # 转为绝对路径
                self.wcf.send_image(abspath, new['receiver'])
                print(f"成功发送图片")
            else : print(f"消息类型错误{new['type']}")
            time.sleep(10)
        print("Queue has been empty")

    def startProcessing(self, url): # 在main函数调用该语句
        """Start the processing thread."""
        thread = threading.Thread(target=self.process_queue, args=(url,))
        thread.start()

    def postReceiverList(self, url):
        not_friends = {
            "fmessage": "朋友推荐消息",
            "medianote": "语音记事本",
            "floatbottle": "漂流瓶",
            "filehelper": "文件传输助手",
            "newsapp": "新闻",
        }
        friends = []
        for cnt in self.wcf.get_contacts():
            if (
                cnt["wxid"].startswith("gh_") or    # 公众号
                cnt["wxid"] in not_friends.keys()   # 其他杂号
            ):
                continue
            friends.append(cnt)

        post_data_to_server(friends, url)


        '''news消息示例
        messages = [
            {
                "type": "text",
                "content": "Hello, this is a text message!",
                "filename":""
                "base64": ""
                "receiver": "bot"
            },
            {
                "type": "image",
                "content": "",
                "filename":"thefilename.png"
                "base64": "the code of base64"
                "receiver": "bot"
            }
        ]
        '''
        

    def send_statistics(self, receiver, type = "daily"):
        '''发送聊天数据统计'''
        leaderboard = collect_stats_in_room(receiver, type)
        if leaderboard:
            msgCount = 0
            current_time = int(datetime.now().timestamp())
            if type == "daily":
                before_time = int(datetime.now().timestamp())-3600*24
            elif type == "weekly":
                before_time = int(datetime.now().timestamp())-3600*24*7
            elif type == "monthly":
                before_time = int(datetime.now().timestamp())-3600*24*30
            # 格式化时间为 "YYYY-MM-DD HH:MM"
            formatted_cu = datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M")
            formatted_be = datetime.fromtimestamp(before_time).strftime("%Y-%m-%d %H:%M")
            stat=["📊群聊数据统计v0.2\n",
                f"🕰时间段：{formatted_be}-{formatted_cu}\n",
                f"👥发言人数：{len(leaderboard)}\n",
                f"💬消息总数：{msgCount}\n",
                f"🏆发言排行榜\n",
            ]

            for i, ld in enumerate(leaderboard):
                msgCount += ld[1] # 统计消息总数
                username=self.wcf.get_alias_in_chatroom(ld[0], receiver) # 将wxid转为群昵称
                stat.append(f"    {i+1}. [{username}]：{ld[1]}条\n")
                if i==4: break # 只显示前5名
            stat[3]=f"💬消息总数：{msgCount}\n" # 更新消息总数
            stat.append("🚀🚀🚀")
            result = ''.join(stat)
            self.sendTextMsg(result, receiver) # 发送统计内容
        else: print(f"最近没有发言记录,无法生成群聊数据统计")

    def handle_statistics_request(self, msg: WxMsg, type="daily"):
        '''统计聊天信息'''
        if msg.from_group:
            self.send_statistics(msg.roomid, type)
        else:
            self.sendTextMsg("该功能仅支持群聊哦！", msg.sender)

    def periodic_statistics(self, type="daily"):
        '''定时统计聊天信息'''
        receivers = fetch_roomid_list("periodStat")
        for receiver in receivers:
            self.send_statistics(receiver, type)
        return []

    def handle_get_id_request(self, msg: WxMsg):
        if msg.from_group:
            self.sendTextMsg(f"您所在的群ID：\n{msg.roomid}\n您的微信id：\n{msg.sender}", msg.roomid, msg.sender)
        else:
            self.sendTextMsg(f"您的微信id：\n{msg.sender}", msg.sender)

    def hasPermission(self, roomid, permission_type = "admin"):
        """
        判断指定房间是否具有某种权限

        参数:
            all_permissions (dict): 包含所有房间权限信息的字典
            roomid (str): 要检查权限的房间ID
            permission_type (str): 要检查的权限类型 (例如 'admin', 'autoSummary', 'callSummary', 'periodStat')

        返回:
            bool: 如果房间具有指定的权限, 则返回 True, 否则返回 False
        """
        # 检查指定的 roomid 是否存在于 all_permissions 字典中
        if roomid not in self.permissions:
            return False
        
        # 获取指定房间的权限字典
        room_permissions = self.permissions[roomid]
        # 若为管理员，则返回 True
        if room_permissions.get("admin"):
            return True
        else:
            print(f"房间或用户{roomid}未拥有admin权限")
        # 检查指定的权限类型是否存在并且为 True
        if room_permissions.get(permission_type, False):
            return True
        else: 
            print(f"房间{roomid}未拥有{permission_type}权限")
            return False


    def handle_url_article_summary_request(self, msg: WxMsg):
        '''处理url形式的文章总结请求'''
        match = re.search(r"https?://[^\s]+", msg.content)
        if match:
            article_url = match.group()
            # 如果URL存在，则抓取文章内容
            article_content = fetch_url_article_content(article_url)
        else:
            print("No valid URL found in the message.")
            return None

        if article_content is None:
            print("Failed to extract article content.")
            return None
        else:
            article_summary = self.chat.get_article_summary(article_content)
            if msg.from_group():
                self.sendTextMsg(article_summary, msg.roomid)
            else:
                self.sendTextMsg(article_summary, msg.sender)

    def handle_card_article_summary_request(self, msg: WxMsg):
        '''处理卡片形式的文章总结请求'''
        # 通过xml获取分享用户名与头像，公众号名与头像，分享时间，文章url
        print("正在解析卡片信息")
        info = fetch_info_from_card_article(msg.content)
        if info['url'] is None:
            print("No url found in the message.")
            return None
        # 提取文章内容
        article_content = fetch_card_article_content(info['url'])
        print("文章内容提取完毕")
        # 交给ai总结
        if article_content is None:
            print("Failed to extract article content.")
            return None
        else:
            article_summary = self.chat.get_article_summary(article_content)
            print("总结生成完毕")
            card_data = struct_summary_to_dict(article_summary)
            card_data['officialName'] = info['sourcedisplayname']
            if msg.from_group():
                card_data['username'] = self.wcf.get_alias_in_chatroom(info['fromusername'], msg.roomid)
                abspath = os.path.abspath(generate_article_summary_card(card_data))
                self.wcf.send_image(abspath, msg.roomid)
                print("卡片生成完毕")
            else:
                card_data['username'] = info['fromusername']
                abspath = os.path.abspath(generate_article_summary_card(card_data))
                self.wcf.send_image(abspath, msg.sender)
                print("卡片生成完毕")
            # if msg.from_group():
            #     self.sendTextMsg(article_summary, msg.roomid)
            # else:
            #     self.sendTextMsg(article_summary, msg.sender)

    def handle_activation_request(self, msg: WxMsg):
        if not msg.from_group: return # 忽略不在群聊的激活请求
        match = re.search(r"/群聊激活\s*(\S.*)", msg.content)
        if match:
            activation_code = match.group(1).strip()  # 获取匹配的激活码并去除首尾空格
            print(f"提取到激活码: {activation_code}")  # 打印激活码

            # 向后端post 激活码以及roomid
            result = submit_activation_code_for_room(activation_code, msg.roomid)

            if result['success']:
                self.LOG.info(f"激活成功: {result['message']}")
                self.sendTextMsg(result['message'], msg.roomid)
            else:
                self.LOG.warning(f"激活失败: {result['message']}")
                self.sendTextMsg(result['message'], msg.roomid)
        else:
            # 表明激活失败
            self.LOG.info("哎呀呀，好像没有找到激活码呢~")  # 如果没有找到，打印提示信息
            self.sendTextMsg("哎呀呀，好像没有找到激活码呢~", msg.roomid)
        return
