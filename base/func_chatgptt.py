#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
import json

import httpx
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI


class ChatGPTt():
    """
    conf:字典包含初始的配置信息
    
    """
    def __init__(self, conf: dict) -> None:
        key = conf.get("key")
        api = conf.get("api")
        proxy = conf.get("proxy")
        prompt = conf.get("prompt")
        self.model = conf.get("model", "gpt-4-turbo-2024-04-09")
        self.LOG = logging.getLogger("ChatGPTt")
        if proxy:
            self.client = OpenAI(api_key=key, base_url=api, http_client=httpx.Client(proxy=proxy))
        else:
            self.client = OpenAI(api_key=key, base_url=api)
        self.conversation_list = {} #初始化一个字典，可能用于存储对话历史
        self.system_content_msg = {"role": "system", "content": prompt}#创建一个包含系统角色和内容的字典，这里的内容由配置中的prompt

    def __repr__(self):
        return 'ChatGPTt'

    @staticmethod
    def value_check(conf: dict) -> bool:
        if conf:
            if conf.get("key") and conf.get("api") and conf.get("prompt"):
                return True
        return False
    
    def get_summary(self, messages, roomid):
        """根据微信群聊消息列表生成总结，由一名经验丰富的大学物理教授执行。"""
    
        # 构建新的提示词
        summary_prompt = (
                "你是一名专业的聊天内容总结专家狲狲，你是一只兔狲，但是你又很会总结话题，并且语言风格俏皮。现在需要你为一个微信群聊的消息进行提取并总结每个时间段大家在重点讨论的话题内容。请按以下格式和要求进行总结：\n"
                "请帮我将给出的群聊内容总结成一个半小时的群聊报告，请你一步步思考,包含不多于10个的话题的总结(要判定Json内容和你生成话题数要对应，不要自行生成多余的话题)（如果还有更多话题，可以在后面简单补充）。每个话题包含以下内容："
                "话题名：(50字以内，带序号1️⃣2️⃣3️⃣，同时附带热度(热度根据成员讨论话题的数量决定），以🔥数量表示）\n"
                "- 👫参与者(不超过5个人，将重复的人名去重)"
                "- 🕰️时间段(从几点到几点)"
                "- 过程(50到200字左右）"
                "- 评价(50字以下)"
                "- 关键点总结(要求分点,类似keywords)"
                "- 😺未来话题评估(100字左右，你对未来话题延申的猜测)"
                "- 👻表情符号(给每一个话题后面增加三个有关话题的emoji表情符号)"
                "- 分割线： ---------------------    "   
                "另外有以下要求："
                "1. 每个话题结束使用 ------------ 分割"
                "2. 使用中文冒号"
                "3. 无需大标题"
                "4. 对输出的结果进行重复检验,确保输出的内容与下面提供的json内容一致，不能出现无关的内容"
                "5. 开始给出本群讨论风格的整体评价，例如本群讨论很活跃哦！、本群无关话题太多了好水鸭、此群好像话题不集中呢、本群的话题有些无聊呢等等诸如此类,最好加点俏皮语气词(要求以一个话题专家狲狲口吻回答)" + json.dumps(messages, ensure_ascii=False, indent=2)
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": summary_prompt}],
                temperature=0.5
            )
            summary = response.choices[0].message.content
            return summary
        except Exception as e:
            self.LOG.error(f"本次生成总结时出错：{str(e)}")
            return "本次无法生成总结。"

    def get_answer(self, question: str, wxid: str) -> str:
        # wxid或者roomid,个人时为微信id，群消息时为群id
        self.updateMessage(wxid, question, "user")
        rsp = ""
        try:
            ret = self.client.chat.completions.create(model=self.model,
                                                      messages=self.conversation_list[wxid],
                                                      temperature=0.2)
            rsp = ret.choices[0].message.content
            rsp = rsp[2:] if rsp.startswith("\n\n") else rsp
            rsp = rsp.replace("\n\n", "\n")
            self.updateMessage(wxid, rsp, "assistant")
        except AuthenticationError:
            self.LOG.error("OpenAI API 认证失败，请检查 API 密钥是否正确")
        except APIConnectionError:
            self.LOG.error("无法连接到 OpenAI API，请检查网络连接")
        except APIError as e1:
            self.LOG.error(f"OpenAI API 返回了错误：{str(e1)}")
        except Exception as e0:
            self.LOG.error(f"发生未知错误：{str(e0)}")

        return rsp

    def updateMessage(self, wxid: str, question: str, role: str) -> None:
        """
        parameter:
            wxid:微信用户的唯一标识符
            question:用户的提问或消息内容
            role:发送消息的角色（例如用户或系统）
        
        mid
            now_time:str 获取当前的日期和时间 转为年月日时分秒形式
            if wxid not in self.conversation_list.keys():检查是否已经有该Wxid对话记录,如果没有执行下面操作
            content_question_ = 创建一个新的字典，包含当前问题的角色和内容,updateMessage传过来的
        """
        now_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        time_mk = "当需要回答时间时请直接参考回复:"
        # 初始化聊天记录,组装系统信息
        if wxid not in self.conversation_list.keys():
            question_ = [
                self.system_content_msg,
                {"role": "system", "content": "" + time_mk + now_time}
            ]
            self.conversation_list[wxid] = question_

        # 当前问题
        content_question_ = {"role": role, "content": question}
        self.conversation_list[wxid].append(content_question_)

        for cont in self.conversation_list[wxid]:
            if cont["role"] != "system":
                continue
            if cont["content"].startswith(time_mk):
                cont["content"] = time_mk + now_time

        # 只存储10条记录，超过滚动清除
        i = len(self.conversation_list[wxid])
        if i > 10:
            print("滚动清除微信记录：" + wxid)
            # 删除多余的记录，倒着删，且跳过第一个的系统消息
            del self.conversation_list[wxid][1]
        

if __name__ == "__main__":
    from configuration import Config
    config = Config().CHATGPTt
    if not config:
        exit(0)

    chat = ChatGPTt(config)

    while True:
        q = input(">>> ")
        try:
            time_start = datetime.now()  # 记录开始时间
            print(chat.get_answer(q, "wxid"))
            time_end = datetime.now()  # 记录结束时间

            print(f"{round((time_end - time_start).total_seconds(), 2)}s")  # 计算的时间差为程序的执行时间，单位为秒/s
        except Exception as e:
            print(e)