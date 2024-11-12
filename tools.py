import re
import requests
import base64
from PIL import Image
import io
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import xml.etree.ElementTree as ET

# 去除content中的xml代码并提取关键信息
'''在func的append之前调用
        content_question_ = {"role": role, "content": question}
        self.conversation_list[wxid].append(content_question_)
'''
def is_xml(xml_string):
    try:
        ET.fromstring(xml_string)  # 尝试解析字符串
        return True  # 如果没有抛出异常，说明是有效的 XML
    except ET.ParseError:  # 如果发生解析错误
        return False  # 说明不是有效的 XML

def contentFilter(content):
    # 判断是否为xml代码
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
        data = response.json()
        messages = data['messages']
        print(f"获取到响应{response.json()}")
        if messages:
            print(f"获取到数据{messages}")
        else: print("获取消息内容为空")
        return messages
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return []

def base64_to_image(base64_str):
    output_path = f"images" # 保存图片的路径
    try:
        if ',' in base64_str:
            header, encoded = base64_str.split(',', 1)
        else:
            header, encoded = '', base64_str

        # 解码Base64字符串
        image_data = base64.b64decode(encoded)
        
        # 使用io.BytesIO将解码后的数据转换为文件对象
        image_file = io.BytesIO(image_data)
        
        # 使用PIL打开图片
        image = Image.open(image_file)

        # 获取当前的日期时间
        now = datetime.now()

        # 格式化日期时间作为文件名
        filename = now.strftime(f'%Y%m%d%H%M.png')

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

def convert_png_base64_to_webp(base64_str, quality = 95):
    if ',' in base64_str:
        header, encoded = base64_str.split(',', 1)
    else:
        header, encoded = '', base64_str
    
    png_data = base64.b64decode(encoded)
    
    # 使用BytesIO来处理PNG数据
    with io.BytesIO(png_data) as png_io:
        # 打开PNG图片
        with Image.open(png_io) as img:
            # 确保输出目录存在
            os.makedirs('images', exist_ok=True)
            # 获取当前时间并格式化为文件名
            now = datetime.now()
            output_filename = now.strftime('%Y%m%d%H%M.webp')
            # 创建输出文件路径
            output_path = os.path.join('images', output_filename)
            # 保存为WebP格式，并设置质量
            img.save(output_path, format='WEBP', quality=quality)
            # 返回生成的WebP图片路径
            return output_path

def post_data_to_server(payload, url, headers=None)->bool:
    # 发送 POST 请求
    response = requests.post(url, json=payload, headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        print("数据成功发送并得到响应")
        return True
    else:
        print(f"发送数据失败，状态码: {response.status_code}")
        print(response.text)
        return False
    
def is_card_article(content):
    # 检查字符串中是否包含 "mp.weixin.qq.com" 以判断是否为需要分析的卡片类型文章
    if is_xml(content) and "mp.weixin.qq.com" in content:
        print("检测到卡片类型文章")
        return True
    return False

def fetch_url_article_content(url):
    '''通过用户提供的url获取文章文本'''

    if url is None:
        print("No url found in the message.")
        return None
    
    # 检查 URL 是否有协议前缀，如果没有则添加 http://
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        # 发送 HTTP 请求获取网页内容，并设置超时时间为 30 秒
        response = requests.get(url, timeout=30)
        
        # 检查请求状态
        if response.status_code == 200:
            # 解析 HTML 内容
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 假设文章内容在 <p> 标签内，可以根据实际网页结构调整
            paragraphs = soup.find_all('p')
            
            # 提取并组合所有 <p> 标签内的文字
            article_content = '\n'.join([p.get_text() for p in paragraphs])
            
            return article_content
        else:
            print("Failed to retrieve the webpage. Status code:", response.status_code)
            return None
    except requests.Timeout:
        print("Request timed out after 30 seconds.")
        return None
    
def fetch_card_article_content(url):
    '''通过卡片类型文章的url获取文章文本'''
    # 初始化 Selenium 浏览器驱动
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; WeChat 8.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.90 Mobile Safari/537.36 MicroMessenger/8.0.0 WeChat/8.0.0.2140(0x28000000) NetType/WIFI Language/zh_CN")
    options.add_argument("--headless")  # 无头模式
    driver = webdriver.Chrome(options=options)

    try:
        # 打开页面并处理可能的验证操作
        driver.get(url)
        time.sleep(5)  # 等待页面完全加载

        try:
            # 尝试找到“去验证”按钮并点击
            verify_button = driver.find_element(By.ID, "js_verify")
            ActionChains(driver).move_to_element(verify_button).click(verify_button).perform()
            print("点击了验证按钮")

            # 等待验证过程完成
            time.sleep(5)
        except:
            # 如果未找到验证按钮，直接获取页面内容
            print("未找到验证按钮，直接获取页面内容")

        # 使用 BeautifulSoup 解析页面源代码
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 假设文章内容在 <p> 标签内，可以根据实际网页结构调整
        paragraphs = soup.find_all('p')
        
        # 提取并组合所有 <p> 标签内的文字
        article_content = '\n'.join([p.get_text() for p in paragraphs])
        # 提取并返回文章内容
        return article_content

    finally:
        # 关闭浏览器
        driver.quit()

def fetch_info_from_card_article(xml_string):
    '''通过xml代码获取文章信息'''
    try:
        # 解析 XML 字符串
        root = ET.fromstring(xml_string)
        
        # 提取所需的字段
        title = root.find(".//title").text if root.find(".//title") is not None else None
        url = root.find(".//url").text if root.find(".//url") is not None else None
        sourcedisplayname = root.find(".//sourcedisplayname").text if root.find(".//sourcedisplayname") is not None else None
        fromusername = root.find(".//fromusername").text if root.find(".//fromusername") is not None else None
        
        # 返回提取的字段
        return {
            "title": title,
            "url": url,
            "sourcedisplayname": sourcedisplayname,
            "fromusername": fromusername
        }
    except ET.ParseError as e:
        raise ValueError(f"XML 解析错误: {e}")