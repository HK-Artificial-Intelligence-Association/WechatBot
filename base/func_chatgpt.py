#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from datetime import datetime
from tools import contentFilter

import httpx
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI


class ChatGPT():
    """
    conf:字典包含初始的配置信息
    
    """
    def __init__(self, conf: dict) -> None:
        key = conf.get("key")
        api = conf.get("api")
        proxy = conf.get("proxy")
        prompt = conf.get("prompt")
        self.model = conf.get("model", "gpt-4o-mini")
        self.LOG = logging.getLogger("ChatGPT")
        if proxy:
            self.client = OpenAI(api_key=key, base_url=api, http_client=httpx.Client(proxy=proxy))
        else:
            self.client = OpenAI(api_key=key, base_url=api)
        self.conversation_list = {} #初始化一个字典，可能用于存储对话历史
        self.system_content_msg = {"role": "system", "content": prompt}#创建一个包含系统角色和内容的字典，这里的内容由配置中的prompt

    def __repr__(self):
        return 'ChatGPT'

    @staticmethod
    def value_check(conf: dict) -> bool:
        if conf:
            if conf.get("key") and conf.get("api") and conf.get("prompt"):
                return True
        return False
    
    def get_summary1(self, messages, roomid):
        """根据微信群聊消息列表生成总结"""
    
        messages_as_text = self.messages_to_text(messages)
        messages_with_boundaries = self.add_boundaries(messages_as_text)
        messages_as_string = "\n".join(messages_with_boundaries)
        
        # 构建新的提示词
        summary_prompt = (
            '''
            ## Character
            - 你是一名微信群聊内容总结专家，同时你也是一只生活在青藏高原的兔狲（Pallas's cat），作为野生猫科动物，你性格厌世且冷傲。
            - 你的语言风格与"鲁迅"、"钱钟书"、"王朔" 等大师高度一致，你擅长一针见血的表达和隐喻，你对现实的批判讽刺刻薄但幽默。
            - 你的任务是根据所收到的聊天记录列表来制作一份每日总结报告。

            ## Skills
            ### Skill 1: 今天选谁吐吐槽
            - 随机选择一位今日活跃群成员的聊天内容进行吐槽，内容要求如下：
            - 围绕结合讨论中这位群友的发言
            - 吐槽凸显技术性、观点性、价值性
            - 用词尖酸刻薄，说话阴阳怪气，可以适当说脏话，有话直说无所顾忌，但要有理有据
            - 体现自己作为一只青藏高原野生兔狲的身份
            - 不能原封不动的使用群成员的发言，必须通过你自己的思考来吐槽
            - 字数少于50字

            ### Skill 2: 今天群里聊了啥
            - 根据聊天记录列表，筛选出具有理论或技术价值的话题，或内容有趣、新颖的话题，或持续时间较长、参与人数较多、较为重要的话题进行总结（确保不要生成多余的内容，并将相似内容的话题合并）。
            - 在总结中，对讨论中提到的晦涩或少见的技术性内容时，请进行非常简短的拓展补充说明（不超过一两句话）。
            - 每日总结报告的输出格式要求请参考如下例子：

            话题名：带序号的话题总结（20字以内）  
            讨论概述：50到150字左右。提炼对话有价值的聊天内容与群友观点。应选择重点、有价值的内容或观点进行展示，避免泛泛地进行概括性省略。要做到有因有果、有始有终，正确引用群成员名称
            狲狲评价：给出针对这个话题的简短评价  
            参与者：不超过5个人，人名不重复  
            🕰 YYYY.MM.DD HH:MM - HH:MM  
            分割线：---------------------

            ## Constraints
            - 每个话题分段并空一行
            - 使用中文冒号
            - 无需大标题
            - 每日总结报告一共不超过5个话题
            - 各个话题按照时间的先后顺序排列
            - 整个总结内容不超过600字
            '''
             + messages_as_string
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
    
        messages_as_text = self.messages_to_text(messages)
        messages_with_boundaries = self.add_boundaries(messages_as_text)
        messages_as_string = "\n".join(messages_with_boundaries)

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
                "6. 使用提供的json内容，确保总结内容与其大致相似，不要生成幻觉内容，严格依据提供的内容进行总结。"
                  + messages_as_string
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
            你是一名专业的聊天内容总结专家狲狲，你是一只兔狲，
            你的总结风格和"Oscar Wilde" "鲁迅" "林语堂"等大师高度一致，你擅长一针见血的表达隐喻，你对现实的批判讽刺幽默。
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
            在最开头给出对于本群讨论内容的评价，要求如下：
            - 结合讨论的内容
            - 观点性要突出
            - 要熟练使用比喻
            - 用词尖酸刻薄，说话阴阳怪气
            - 字数少于20字

            ## Constraints
            - 每个话题分段并空一行
            - 使用中文冒号
            - 无需大标题
            - 从每一段时间的总结中选取1至2个持续时间较长的话题进行总结，一共不超过5个话题
            - 各个话题按照时间的先后顺序排列
            """
        )
        summaries_str = "\n接下来是另一段时间的总结\n".join(summaries)
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
        
    def get_article_summary(self, article_content:str):
        article_prompt = '''
            ## Role: 文章总结专家
            ## version: 0.1
            ## Description: 你是一个总结文章的专家
            ## Goals: 提取每篇文章最关键的核心内容，并生成一篇总结

            ## Constrains:
            - 除非有充分理由，请不要随意修改和缩减原先JSON中的内容
            - 如果没有明显的内容重组，直接使用原始值构建文章
            - 确保输出的日报格式完全符合Output Format
            - 输出语言为[中文]

            ## Output format:
            按照以下格式输出文章的总结：
            <title>{标题}</title>
            <content>{总结的文章内容}</content>
            <keywords>{关键词}</keywords>

            ## Example
            <title>这是标题</title>
            <content>这里是总结的文章内容</content>
            <keywords>关键词1 关键词2 关键词3</keywords>

            ## Workflow: 
            - 阅读输入的文章内容
            - 给这篇文章取一个标题
            - 提炼出文章的核心内容与观点，生成文章总结
            - 生成具有代表性的关键词
            - 严格按照Output format输出
        '''
        try:
            rsp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": article_prompt},
                    {"role": "user", "content": article_content}
                ],
                temperature=0
            )
            article_summary = rsp.choices[0].message.content
        except AuthenticationError:
            self.LOG.error("OpenAI API 认证失败，请检查 API 密钥是否正确")
        except APIConnectionError:
            self.LOG.error("无法连接到 OpenAI API，请检查网络连接")
        except APIError as e1:
            self.LOG.error(f"OpenAI API 返回了错误：{str(e1)}")
        except Exception as e0:
            self.LOG.error(f"发生未知错误：{str(e0)}")
        return article_summary
    
    def add_boundaries(self, messages):
        # 创建一个新的列表用于存储带边界的消息
        messages_with_boundaries = []
        
        # 遍历每一条消息
        for message in messages:
            # 使用json.dumps将字典转换为JSON字符串
            messages_with_boundaries.append(json.dumps(message, ensure_ascii=False, indent = 2))  # 确保支持Unicode字符
            # 在每条消息后添加边界符
            messages_with_boundaries.append("----------------")
        
        # 返回处理后的消息列表
        return messages_with_boundaries

    #将格式化消息转化为口语化消息
    def messages_to_text(self, messages):
        # 初始化一个空列表来存储格式化后的消息
        messages_text = []

        # 使用 for 循环逐一处理每个 message
        for message in messages:
            message_text = f"{message['sender']}在{message['time']}发布了一条消息，内容为：{message['content']}"
            messages_text.append(message_text)
        return messages_text

    def add_boundaries(self, messages):
        # 创建一个新的列表用于存储带边界的消息
        messages_with_boundaries = []
        
        # 遍历每一条消息
        for message in messages:
            # 使用json.dumps将字典转换为JSON字符串
            messages_with_boundaries.append(json.dumps(message, ensure_ascii=False, indent = 2))  # 确保支持Unicode字符
            # 在每条消息后添加边界符
            messages_with_boundaries.append("----------------")
        
        # 返回处理后的消息列表
        return messages_with_boundaries
    
if __name__ == "__main__":
    from configuration import Config
    config = Config().CHATGPT
    if not config:
        exit(0)

    chat = ChatGPT(config)

    while True:
        q = input(">>> ")
        try:
            time_start = datetime.now()  # 记录开始时间
            print(chat.get_answer(q, "wxid"))
            time_end = datetime.now()  # 记录结束时间

            print(f"{round((time_end - time_start).total_seconds(), 2)}s")  # 计算的时间差为程序的执行时间，单位为秒/s
        except Exception as e:
            print(e)
