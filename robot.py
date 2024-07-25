# -*- coding: utf-8 -*-
# UTF-8 编码

import logging# 导入日志库，用于记录日志信息
import re# 导入正则表达式库，用于文本匹配和处理
import time# 导入时间库，用于处理时间相关的功能
import xml.etree.ElementTree as ET # 用于处理XML格式数据，如微信消息中的数据
from queue import Empty # 从队列库导入Empty异常，用于处理队列空异常
from multiprocessing import Queue
from threading import Thread
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
from db import fetch_messages_from_last_some_hour,fetch_summary_from_db
from utils.yaml_utils import update_yaml
from tools import fetch_news_json
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
        self.calltime = 10 # 初始化调用次数
        self.newsQueue = Queue() # 初始化新闻队列

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
                self.chat = None# 如果没有合适的配置，将聊天模型设置为None
        else:
            # 如果聊天类型不在支持的列表中，也尝试进行初始化
            # 类似的逻辑处理...
            if TigerBot.value_check(self.config.TIGERBOT):
                self.chat = TigerBot(self.config.TIGERBOT)
            elif ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
            elif ChatGPTt.value_check(self.config.CHATGPTt):
                self.chat = ChatGPTt(self.config.CHATGPTt)
            elif Moonshot.value_check(self.config.MOONSHOT):
                self.chat = Moonshot(self.config.MOONSHOT)
            elif Qwen.value_check(self.config.QWEN):
                self.chat = Qwen(self.config.QWEN)
            elif XinghuoWeb.value_check(self.config.XINGHUO_WEB):
                self.chat = XinghuoWeb(self.config.XINGHUO_WEB)
            elif ChatGLM.value_check(self.config.CHATGLM):
                self.chat = ChatGLM(self.config.CHATGLM)
            elif BardAssistant.value_check(self.config.BardAssistant):
                self.chat = BardAssistant(self.config.BardAssistant)
            elif ZhiPu.value_check(self.config.ZhiPu):
                self.chat = ZhiPu(self.config.ZhiPu)
            elif DeepSeek.value_check(self.config.DEEPSEEK):
                self.chat = DeepSeek(self.config.DEEPSEEK)
            else:
                self.LOG.warning("未配置模型")
                self.chat = None

        self.LOG.info(f"已选择: {self.chat}")
        #self.current_msg = None

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
                "2. /总结 - 获取聊天总结，我可以帮你总结一小时的聊天内容哦\n"
                "3. /help - 获取帮助信息\n"
                "3. 后续功能还在开发中，敬请期待！\n",
                msg_dict["roomid"]
            )

        # 新的判断条件，消息类型为1，is_group为1，并且content中包含'\func'
        if msg_dict['type'] == 1 and msg_dict['is_group'] == 1 and '/help' in msg_dict['content']:
            self.sendTextMsg(
                f"我是兔狲机器人，小狲狲，你好鸭。当前我使用的模型是：{self.model_type}\n"
                "你可以使用以下命令：\n"
                "1. /help - 获取帮助信息\n"
                "2. /总结1 - 获取2小时内分话题式聊天总结\n"
                "3. /总结2 - 获取2小时内不话题式聊天总结\n"
                "4. 后续功能还在开发中，敬请期待！\n",
                msg_dict["roomid"]
            )

        
        else:
            content = msg.content.strip()
            # print(content)
            # 检查是否是控制命令或是否包含“总结”关键字
            if content == "/sun":
                self.handle_open(msg)
            elif content == "/nus":
                self.handle_close(msg)
            elif "@" in content and "总结" in content and msg_dict['type'] != 49:
                self.handle_summary_request(msg)
            elif "/change" in content:
                self.change_model(msg)
            elif self.active:
                # 如果机器人处于活跃状态，则处理其他消息
                self.handle_other_messages(msg)


    def change_model(self, msg):
        content = msg.content
        print("消息内容:", content)  # 打印消息内容以调试

            # 获取最后一位字符并尝试将其转换为数字
        try:
            chat_type = int(content[-1])
            print("提取的数字是:", chat_type)
        except ValueError:
            chat_type = None
            print("没有找到匹配的数字")
    
        if chat_type and ChatType.is_in_chat_types(chat_type):
            if chat_type == ChatType.CHATGPT.value and ChatGPT.value_check(self.config.CHATGPT):
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
            elif chat_type == ChatType.DeepSeek.value and DeepSeek.value_check(self.config.DEEPSEEK):
                self.chat = DeepSeek(self.config.DEEPSEEK)
                self.model_type = 'DeepSeek-deepseek-chat'
            else:
                self.LOG.warning("未配置模型")
                self.chat = None  # 如果没有合适的配置，将聊天模型设置为None
                self.model_type = None
        else:
            # 如果聊天类型不在支持的列表中，也尝试进行初始化
            if ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
            elif ChatGPTt.value_check(self.config.CHATGPTt):
                self.chat = ChatGPTt(self.config.CHATGPTt)
            elif Moonshot.value_check(self.config.MOONSHOT):
                self.chat = Moonshot(self.config.MOONSHOT)
            elif Qwen.value_check(self.config.QWEN):
                self.chat = Qwen(self.config.QWEN)
            else:
                self.LOG.warning("未配置模型")
                self.chat = None
    
        self.LOG.info(f"已选择: {self.chat}")


    def handle_summary_request(self, msg: WxMsg, time_hours=2):
        """处理总结请求,使用GPT生成总结，默认提取2小时的聊天记录"""
        messages_withwxid = fetch_messages_from_last_some_hour(msg.roomid, time_hours)
        
        messages = []
        for message_withwxid in messages_withwxid:
            message = {
                "content": message_withwxid["content"],
                "sender":self.wcf.get_alias_in_chatroom(message_withwxid["sender_id"], msg.roomid),# 将messages里的wxid替换成wx昵称
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
            if msg.from_group():
                self.sendTextMsg(summary, msg.roomid, msg.sender)
                self.sendTextMsg(f"本群总结调用次数还剩{self.calltime}次", msg.roomid, msg.sender)
            else:
                self.sendTextMsg(summary, msg.sender)
                self.sendTextMsg(f"本群总结调用次数还剩{self.calltime}次", msg.sender)
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
                self.toAt(msg)
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
        Thread(target=innerProcessMsg, name="GetMessage", args=(self.wcf,), daemon=True).start()

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
        receivers = []  # 指定接收者，可以根据需要进行修改
        for receiver in receivers:
            messages_withwxid = fetch_messages_from_last_some_hour(roomid = receiver, time_hours=time_hours)
            # 将messages里的wxid替换成wx昵称
            messages = []
            
            for message_withwxid in messages_withwxid:
                message = {
                    "content": message_withwxid["content"],
                    #"sender": self.wcf.get_info_by_wxid(message_withwxid["sender_id"]),
                    "sender":self.wcf.get_alias_in_chatroom(message_withwxid["sender_id"], receiver),
                    "time": message_withwxid["time"]
                }
                messages.append(message)

            summary = self.chat.get_summary1(messages, receiver)# 生成聊天总结
            self.sendTextMsg(summary, receiver)# 发送总结内容


    def saveAutoSummary(self, time_hours=2):
        """
        生成并保存聊天总结 目前只用深度求索
        """
        receivers = ["45647094112@chatroom","19046067886@chatroom"]  # 指定总结群聊，可以根据需要进行修改
        if not receivers:print("没有指定进行总结的群聊")
        #切换到DeepSeek模型进行总结
        # self.chat = DeepSeek(self.config.DEEPSEEK)
        # self.model_type = 'DeepSeek-deepseek-chat'
        # self.LOG.info(f"已选择: {self.chat}")
        for receiver in receivers:
            messages_withwxid = fetch_messages_from_last_some_hour(receiver, time_hours)
            if not messages_withwxid:continue # 如果没有聊天记录则跳过
            messages = []
            for message_withwxid in messages_withwxid:
                sender=self.wcf.get_alias_in_chatroom(message_withwxid["sender_id"], receiver),
                if not sender: # 将messages里的wxid替换成wx昵称
                    sender = message_withwxid["sender_id"]
                    self.LOG.info(f"{sender}昵称获取错误，已使用wxid替换")
                else:
                    self.LOG.info(f"{sender}昵称获取成功啦")
                message = {
                    "content": message_withwxid["content"],
                    "sender":sender,
                    "time": message_withwxid["time"]
                }
                messages.append(message)

            summary = self.chat.get_summary1(messages,roomid=receiver)
            store_summary(receiver, summary, int(datetime.now().timestamp()))
        # 切换回4o
        # self.chat = ChatGPTt(self.config.CHATGPTt)
        # self.model_type = 'gpt-4-turbo-2024-04-09'
        # self.LOG.info(f"已选择: {self.chat}")

        return []
    def sendDailySummary(self) -> None:# 以后会新增参数或者函数（sendWeeklySummary）
        '''发送每日总结并存入数据库'''
        receivers = ["19046067886@chatroom"]  # 指定总结群聊，可以根据需要进行修改
        for receiver in receivers:
            summaries = fetch_summary_from_db(receiver, 'partly')
            if summaries:
                summary = self.chat.get_summary_of_partly(summaries, receiver)
                ts = int(datetime.now().timestamp())
                store_summary(receiver, summary, ts, type='daily') # 存入每日数据库
                self.sendTextMsg(summary, receiver) # 若需要@所有人，添加参数at_list == "notify@all"即可
                self.LOG.info(f"已发送{receiver}的每日总结")
            else:
                print("过去没有足够的分段总结内容来生成总结。", receiver)
        

    def process_queue(self, url):
        """若队列为空，则抓取消息；否则，每隔十秒输出消息"""
        while True:
            if self.newsQueue.empty():
                print("News queue is empty, fetching data...")
                try:
                    news = fetch_news_json(url)
                    if isinstance(news, list):
                        for new in news:
                            if isinstance(new, dict):
                                required_keys = ['type', 'url', 'content', 'receiver']  # 假设这些是必需的键
                                if all(key in new for key in required_keys):  # 确保字典包含所有必需的键
                                    self.newsQueue.put(new)  # 加入队列
                                    print(f"已加入队列：{new}")
                                else:
                                    print(f"忽略无效新闻：{new}，缺少必要键")
                            else:
                                print(f"忽略非字典项：{new}")
                                # self.newsQueue.put(new) # 加入队列
                    else:
                        print(f"从URL:{url}获取的数据不是列表：{news}")
                except Exception as e:
                    print(f"Failed to fetch data: {e}")
                    time.sleep(60)  # Wait for 1 minute before retrying
            else:
                self.sendTopNews()
                print("Send news successfully!")
                break


        # self.sendTextMsg("测试", receiver)
        # self.wcf.send_image("https://t7.baidu.com/it/u=4036010509,3445021118&fm=193&f=GIF", "45647094112@chatroom")



    def sendTopNews(self) -> None:
        '''轮询消息与发送'''
        while self.newsQueue.empty() == False: # 如果队列不为空
            new = self.newsQueue.get()
            if new['type'] == "text":
                print(f"发送{new['content']}")
                self.sendTextMsg(new['content'], new['receiver'])
            elif new['type'] == "image":
                self.wcf.send_image(new['url'], new['receiver'])
                print(f"发送{new['url']}图片")
            else : print(f"消息类型错误{new['type']}")
            time.sleep(10)
        print("Queue has been empty")

    def start_processing(self, url): # 在main函数调用该语句
        """Start the processing thread."""
        thread = Thread(target=self.process_queue, args=(url,))
        thread.start()

        
        '''news消息示例
        messages = [
            {
                "type": "text",
                "url": "",
                "content": "Hello, this is a text message!",
                "receiver": "bot"
            },
            {
                "type": "image",
                "url": "https://example.com/path/to/image.jpg",
                "content": "",
                "receiver": "bot"
            }
        ]
        '''
        