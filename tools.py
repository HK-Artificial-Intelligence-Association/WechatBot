import re
import requests
import base64
from PIL import Image
import io
import os

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

def fetch_news_json(url):
    # 发送GET请求获取JSON数据
    response = requests.get(url)
    if response.status_code == 200:
        print(f"获取到数据{response.json()}")
        return response.json()
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return []

def base64_to_image(base64_str, filename):
    output_path = f"images" # 保存图片的路径
    try:
        # 解码Base64字符串
        image_data = base64.b64decode(base64_str)
        
        # 使用io.BytesIO将解码后的数据转换为文件对象
        image_file = io.BytesIO(image_data)
        
        # 使用PIL打开图片
        image = Image.open(image_file)

        # 构建完整的文件路径
        output_path = os.path.join("images", filename)
        
        # 创建目录如果不存在
        os.makedirs("images", exist_ok=True)
        
        # 保存图片到本地
        image.save(output_path)
        
        print(f"图片已保存到：{output_path}")
    except Exception as e:
        print(f"保存图片时出错：{e}")
        return ''
    return output_path

def post_data_to_server(data, url)->bool:
    # 发送 POST 请求
    response = requests.post(url, json=data)

    # 检查响应状态码
    if response.status_code == 200:
        print("数据成功发送并得到响应")
        return True
    else:
        print(f"发送数据失败，状态码: {response.status_code}")
        print(response.text)
        return False