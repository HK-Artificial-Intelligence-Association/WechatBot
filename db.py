import sqlite3
import os
import time
import re
from utils.token_utils import num_tokens_from_string, get_gptmodel_name
from datetime import datetime, timedelta
from wcferry import Wcf, WxMsg # wcferry库提供的基础类和消息类，用于微信通讯
from tools import contentFilter

db_path = 'wechat_bot.db'

def create_database():
    """创建数据库和表，如果它们不存在的话"""
    db_exists = os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        type INTEGER,
        sender TEXT,
        roomid TEXT,
        content TEXT,
        thumb TEXT,
        extra TEXT,
        sign TEXT,
        ts INTEGER,
        xml TEXT,
        is_self INTEGER,
        is_group INTEGER,
        token INTEGER
    )
    ''')

    
    """
    创建 roomid 表
    """
    c.execute('''
    CREATE TABLE IF NOT EXISTS roomids (
        roomid TEXT PRIMARY KEY,
        timestamp INTEGER
    )
    ''')


    """
    创建 summary 表
    """
    c.execute('''
    CREATE TABLE IF NOT EXISTS summary (
        roomid TEXT NOT NULL,
        date DATE,
        summary TEXT,
        ts INTEGER NOT NULL,
        type TEXT,
        PRIMARY KEY (roomid, ts)
    )
    ''')

    conn.commit()
    conn.close()


    if not db_exists:
        print("数据库和表已创建。")
    else:
        print("已确保表存在于数据库中。")

def store_message(msg):
    """将消息存储到数据库的 'messages' 表中"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    model_name = get_gptmodel_name()
    token = num_tokens_from_string(msg.get('content'), model_name)
    msg_data = (
        msg.get('id'),
        msg.get('type'),
        msg.get('sender'),
        msg.get('roomid'),
        msg.get('content'),
        msg.get('thumb'),
        msg.get('extra'),
        msg.get('sign'),
        msg.get('ts'),
        msg.get('xml'),
        int(msg.get('is_self', False)),
        int(msg.get('is_group', True)),
        token
    )
    try:
        c.execute('''
        INSERT INTO messages (id, type, sender, roomid, content, thumb, extra, sign, ts, xml, is_self, is_group,token)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', msg_data)
        conn.commit()
        print("消息已成功存储到 'messages' 表。")
    except sqlite3.IntegrityError:
        print("消息已存在，未能存储到 'messages' 表。")
    except Exception as e:
        print(f"无法存储消息到 'messages' 表：{e}")
    finally:
        conn.close()


def insert_roomid(roomid):
    """
    向数据库插入新的roomid和当前时间戳，如果roomid已存在则不插入。
    参数：
    - roomid: 要插入的房间ID
    注意：这个函数假设全局变量 db_path 已经被定义为数据库文件的路径。
    """
    conn = sqlite3.connect(db_path)

    try:
        # 创建游标对象
        c = conn.cursor()

        # 检查roomid是否已存在
        c.execute('SELECT roomid FROM roomids WHERE roomid = ?', (roomid,))
        if c.fetchone():
            print("roomids已经存在")
        else:
            # 插入新的roomid和时间戳
            current_timestamp = int(time.time())  # 获取当前时间戳
            c.execute('INSERT INTO roomids (roomid, timestamp) VALUES (?, ?)', (roomid, current_timestamp))
            conn.commit()  # 提交事务
            print("roomids插入成功")
    except Exception as e:
        print("roomids插入失败:", e)
    finally:
        conn.close()


def store_summary(roomid, summary, ts, type='partly'):
    """
    将 roomid, summary 和 ts 插入到 'summary' 表中，其中 date 由 ts 计算得出。
    """
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 从 ts 中提取 date
    date = datetime.fromtimestamp(ts).strftime('%Y年%m月%d日')

    # 插入数据到 'summary' 表
    c.execute('''
    INSERT INTO summary (ts, roomid, summary, date, type)
    VALUES (?, ?, ?, ?, ?)
    ''', (ts, roomid, summary, date, type))

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

    print(f"已将对{roomid}于{date}的{type}聊天记录总结加入数据库")


def fetch_messages_from_last_two_hour(roomid):
    """从数据库中获取过去两小时内的所有消息，并打印获取到的消息内容"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #获取当前时间戳和两小时前的时间戳
    current_time = int(datetime.now().timestamp())
    two_hour_ago = current_time - 7200
    print(f"当前时间戳：{current_time}, 两小时前时间戳：{two_hour_ago}")  # 打印当前时间和两小时前的时间戳
    #执行SQL查询以获取消息
    try:
        # 查询符合 roomid 和时间戳条件的消息，且 content 不包含 "@小狲狲"
        cursor.execute(
            "SELECT content, sender, ts FROM messages WHERE roomid = ? AND ts >= ? AND content NOT LIKE '%@小狲狲%'",
            (roomid, two_hour_ago)
        )
        rows = cursor.fetchall()
        
        if rows:
            print("成功获取以下消息：")
            messages = []
            for row in rows:
                content, sender_id, timestamp = row
                readable_time = datetime.fromtimestamp(timestamp).strftime('%Y年%m月%d日 %H:%M:%S')
                message = {
                    "content": content,
                    "sender_id": sender_id,
                    "time": readable_time
                }
                messages.append(message)
                print(f"内容: {content}, 发送者ID: {sender_id}, 时间: {readable_time}")
        else:
            print("过去一小时内没有消息。")
            return []

        return messages
    except Exception as e:
        print(f"获取消息失败：{e}")
        return []
    finally:
        conn.close()

# 调用指定时间内的消息
def fetch_messages_from_last_some_hour(roomid,time_hours):
    """从数据库中获取过去几个小时内的所有消息，并打印获取到的消息内容"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #获取当前时间戳和几小时前的时间戳
    current_time = int(datetime.now().timestamp())
    before_time = int(current_time - 3600*time_hours)# 首先乘以秒数再转为int防止数据库检索失败
    print(f"当前时间戳：{current_time}, {time_hours}小时前时间戳：{before_time}")  # 打印当前时间和n小时前的时间戳
    #执行SQL查询以获取消息
    try:
        # 查询符合 roomid 和时间戳条件的消息，且 content 不包含 "@小狲狲"
        cursor.execute(
            "SELECT content, sender, ts FROM messages WHERE roomid = ? AND ts >= ? AND content NOT LIKE '%@小狲狲%'",
            (roomid, before_time)
        )
        rows = cursor.fetchall()
        
        if rows:
            print("成功获取以下消息：")
            messages = []
            for row in rows:
                content, sender_id, timestamp = row
                readable_time = datetime.fromtimestamp(timestamp).strftime('%Y年%m月%d日 %H:%M:%S')
                content = contentFilter(content)#过滤掉xml
                message = {
                    "content": content,
                    "sender_id": sender_id,
                    "time": readable_time
                }
                messages.append(message)
                print(f"内容: {content}, 发送者ID: {sender_id}, 时间: {readable_time}")
        else:
            print(f"过去{time_hours}小时内没有消息。")
            return []

        return messages
    except Exception as e:
        print(f"获取消息失败：{e}")
        return []
    finally:
        conn.close()


def fetch_roomid_from_db():
    """从数据库获取最新的单个roomid"""
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 执行查询，只获取最新的一个条目
        cursor.execute("SELECT roomid FROM roomids ORDER BY timestamp DESC LIMIT 1")
        
        # 获取查询结果
        result = cursor.fetchone()
        room_id = result[0] if result else None
        
        # 关闭数据库连接
        conn.close()
        
        return room_id
    except sqlite3.DatabaseError as e:
        print(f"数据库错误: {e}")
        return None
    except Exception as e:
        print(f"其他错误: {e}")
        return None

def fetch_roomids_from_db():
    """从数据库中获取房间ID列表。"""
    conn = sqlite3.connect(db_path)  # 确保数据库路径是正确的
    cursor = conn.cursor()
    cursor.execute("SELECT roomid FROM roomids")
    room_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return room_ids

def fetch_summary_from_db(roomid, type):
    '''从数据库收集指定类型的定时总结

    parameter:
        roomid: 要获取总结的房间ID
        type: 要获取总结的类型，可选值为'partly', 'daily', 'weekly', 'monthly'
    '''
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    typelist=['partly','daily','weekly','monthly']
    type2=typelist[(typelist.index(type)+1) % len(typelist)] # 防止下标越界
    if type2=='daily':hour=24
    elif type2=='weekly':hour=24*7
    elif type2=='monthly':hour=24*31
    elif type2=='partly':hour=24*365
    # 还有else的情况 以及总结过程中的时间问题，月总结是否需要日期？
    current_time = int(datetime.now().timestamp())
    before_time = current_time - 3600*hour
    # 执行SQL查询，获取特定roomid且ts大于temp_ts的所有summary数据
    c.execute("SELECT summary FROM summary WHERE roomid = ? AND type = ? AND ts >= ?", (roomid, type, before_time))
    
    # 获取所有查询结果
    
    summaries = c.fetchall()
    print(f"成功从数据库收集到{len(summaries)}条{type}总结")
    # 关闭数据库连接
    conn.close()

    # 将结果转换为列表，因为fetchall()返回的是元组列表
    return [summary[0] for summary in summaries]


def collect_stats_in_room(roomid, type="daily"):
    '''获取指定房间ID和时间段的用户发言次数'''
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if type == "daily":
        hour = 24
    elif type == "weekly":
        hour = 24 * 7
    elif type == "monthly":
        hour = 24 * 30
    else:
        raise ValueError("Invalid type. Valid types are 'daily', 'weekly', or 'monthly'.")
    current_time = int(datetime.now().timestamp())
    before_time = current_time - 3600 * hour

    # 执行 SQL 查询
    query = """
    SELECT sender, COUNT(*) as count
    FROM messages
    WHERE roomid = ? AND ts >= ?
    GROUP BY sender
    ORDER BY count DESC
    """
    cursor.execute(query, (roomid, before_time))
    
    # 获取查询结果
    result = cursor.fetchall()
    
    # 关闭数据库连接
    conn.close()
    
    return result