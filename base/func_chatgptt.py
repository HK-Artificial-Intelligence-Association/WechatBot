#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
import json
from tools import contentFilter

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
        self.model = conf.get("model", "GPT-4o")
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
    
    def get_summary1(self, messages, roomid):
        """根据微信群聊消息列表生成总结"""
    
        # 构建新的提示词
        summary_prompt = (
            '''
            ## Character
            你是一名专业的聊天内容总结专家狲狲，你是一只兔狲，而且你很会总结话题，你的总结风格具有非常强的攻击性，以刻薄和挑衅的风格而闻名。
            现在需要你为一个微信群聊的消息进行提取并总结每个时间段大家在重点讨论的话题内容。

            ## Skills
            ### Skills 1: 总结话题
            - 将给出的群聊内容总结成群聊报告。每个报告包含不多于5个话题(要判定Json内容和生成话题数要对应，不能自行生成多余话题)。优先选择持续时间较长、参与人数较多的话题。
            - 每个话题包含以下内容：
            - 话题名：(思考一个话题名并替换'话题名'，20字以内，带序号1️⃣2️⃣3️⃣，同时附带热度(热度根据成员讨论话题的数量决定），以🔥数量表示）
            - 内容概述(60到200字左右,要详细的提到每个发言人的观点)
            - emoji叙事(给每一个话题后面增加三个有关话题的emoji表情符号)
            - 👫参与者(不超过5个人，人名不重复)
            - 🕰️YYYY年mm月dd日 HH:MM - %YYYY年mm月dd日 HH:MM
            - ---------------------(分割线)

            ## Constraints
            - 每个话题分段并空一行
            - 使用中文冒号
            - 无需大标题
            - 对输出结果进行重复检验，确保输出内容与提供的json内容一致，不能出现无关内容
            - 在总结的最后一段的下一行加上'----Summarized by LLM🚀🚀🚀'
            '''
             + json.dumps(messages, ensure_ascii=False, indent=2)
    )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": summary_prompt}],
                temperature=0
            )
            summary = response.choices[0].message.content
            return summary
        except Exception as e:
            self.LOG.error(f"本次生成总结时出错：{str(e)}")
            return "本次无法生成总结。"
    

    def get_summary2(self, messages, roomid):
        """根据微信群聊消息列表生成总结"""
    
        # 构建新的提示词
        summary_prompt = (
                "你是一名专业的聊天内容总结专家狲狲，你是一只兔狲，但是你很会总结话题，并且语言风格俏皮。现在需要你为一个微信群聊的消息进行提取并总结。请按以下格式和要求进行总结：\n"
                "请帮我将给出的群聊内容总结成一个两小时的群聊报告，请你一步步思考，总结应覆盖所有讨论内容（要判定Json内容和你生成总结的内容要对应，不要自行生成多余的内容）。总结包括以下内容："
                "1. 参与者：不超过5个人，将重复的人名去重"
                "2. 时间段：从几点到几点"
                "3. 讨论概述：50到200字左右，描述这段时间内的整体讨论内容"
                "4. 亮点评论：50字以下，对讨论内容的整体评价"
                "5. 关键点总结：要求分点，类似keywords"
                "6. 主要观点：列出讨论中的主要观点或意见（不超过5点）"
                "7. 引发的疑问：列出讨论中提出的主要问题或需要进一步讨论的疑问"
                "8. 未来计划：描述讨论中提出的未来计划或行动（如有）"
                "9. 未来话题预测：100字左右，你对未来话题延申的猜测"
                "10. 表情符号：给整个总结后面增加三个有关话题的emoji表情符号"
                "11. 分割线： ---------------------    "   
                "另外有以下要求："
                "1. 总结结束使用 ------------ 分割"
                "2. 使用中文冒号"
                "3. 无需大标题"
                "4. 对输出的结果进行重复检验，确保输出的内容与下面提供的json内容一致，不能出现无关的内容"
                "5. 开始给出本群讨论风格的整体评价，例如：本群讨论很活跃哦！、本群无关话题太多了好水鸭、此群好像话题不集中呢、本群的话题有些无聊呢等等诸如此类，最好加点俏皮语气词（要求以一个话题专家狲狲的口吻回答）"
                "6. 使用提供的json内容，确保总结内容与其大致相似，不要生成幻觉内容，严格依据提供的内容进行总结。" + json.dumps(messages, ensure_ascii=False, indent=2)
    )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": summary_prompt}],
                temperature=0
            )
            summary = response.choices[0].message.content
            return summary
        except Exception as e:
            self.LOG.error(f"本次生成总结时出错：{str(e)}")
            return "本次无法生成总结。"

    def get_summary_of_partly(self, summaries, roomid):
        """根据微信群聊消息列表生成总结"""
        summary_prompt = ( 
            """
            ## Character
            你是一名专业的聊天内容总结专家狲狲，你是一只兔狲，而且你很会总结话题，你的总结风格具有非常强的攻击性，以刻薄和挑衅的风格而闻名。
            现在需要你根据用户给出的多个之前生成的“分段总结”来制作一份每日总结报告。

            ## Skills
            ### Skill 1: 制作每日总结报告
            - 根据用户提供的“分段总结”内容，选择出持续时间较长、参与人数较多或较为重要的话题（确保不要生成多余的内容，并将相似内容的话题合并）。
            - 格式要求请参考如下例子：

            话题名：1️⃣2️⃣3️⃣ 带序号话题名（20字以内）🔥🔥🔥（根据成员讨论话题的数量决定）
            讨论概述：50到200字左右,要详细的提到每个发言人的观点
            emoji叙事：三个有关话题的emoji表情符号
            👫参与者：不超过5个人，人名不重复
            🕰️YYYY年mm月dd日 HH:MM - YYYY年mm月dd日 HH:MM
            分割线：---------------------

            ### Skill 2: 整体评价
            在开始给出本群讨论风格的整体评价，可以结合聊天内容，字数少于100字。例如：
            {
            你们在群聊里关于“AI技术”的讨论，简直就像是一群刚从床上滚下来的程序员，试图用那件格子T恤般的理论去解释深度学习。那些所谓的“见解”，散发出强烈的“我试图与墙纸融为一体”的气息，完全无法引起任何人的兴趣。还有那些充满bug的代码片段？它们在尖叫“我懒得找些效果更好的参数。”不过，嘿，至少你们看起来很舒服。舒适是关键，对吧？只是在试图发表有深度的技术见解时，可能就不太合适了。
            }

            ## Constraints
            - 每个话题分段并空一行
            - 使用中文冒号
            - 无需大标题
            - 从每一段时间的总结中选取1至2个持续时间较长的话题进行总结，一共不超过5个话题
            - 各个话题按照时间的先后顺序排列
            """
        )
        summaries_str = "接下来是另一段时间的总结".join(summaries)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": summaries_str}
                ],
                temperature=0
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

        # 去除content中的xml代码并提取关键信息
        question = contentFilter(question)
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