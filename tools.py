import re

# 去除content中的xml代码并提取关键信息
'''在func的append之前调用
        content_question_ = {"role": role, "content": question}
        self.conversation_list[wxid].append(content_question_)
'''
def is_xml(content, threshold=15):
    # 计算符号 "<"、">" 和 "/" 的数量
    num_symbols = content.count('<') + content.count('>') + content.count('/')
    return num_symbols > threshold

def contentFilter(content):
    # 尝试解析 content，如果能够解析则说明是xml代码，如果解析失败则认为是普通文本
    if is_xml(content):
        # 检查是否包含 "img"
        if "<img" in content:
            content = "图片"
        elif "refermsg" in content:
            # 提取 <title> 和 </title> 之间的内容
            title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
            reply = title_match.group(1) if title_match else ""

            # 提取 <content> 和 </content> 之间的内容
            content_match = re.search(r"<content>(.*?)</content>", content, re.DOTALL)
            refermsg = content_match.group(1) if content_match else ""
            if len(refermsg) > 30:
                refermsg = refermsg[:10]
            # 提取 <displayname> 和 </displayname> 之间的内容
            displayname_match = re.search(r"<displayname>(.*?)</displayname>", content, re.DOTALL)
            referredname = displayname_match.group(1) if displayname_match else ""

            # 合并提取的内容
            content = f'针对{referredname}的消息"{refermsg}"进行了回复：{reply}'.strip()
            print("过滤成功")
        else:
            content = ""
    return content