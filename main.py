#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#signal模块，用于处理程序中的信号。信号是用来处理异步事件的机制。
import signal
#ArgumentParser用于编写用户友好的命令行界面。程序定义它需要的参数，argparse会从sys.argv中解析这些参数。
from argparse import ArgumentParser
import db
from apscheduler.schedulers.background import BackgroundScheduler
#位于base目录下的func_report_reminder模块（或子模块）中导入了ReportReminder类。这不是标准Python库，表明它是自定义的或第三方代码。
#from base.func_report_reminder import ReportReminder
from configuration import Config
#名为constants的模块中导入了ChatType。ChatType可能是一个类、枚举或常量变量，用于定义应用中不同类型的聊天。
from constants import ChatType
from robot import Robot, __version__
#从一个名为wcferry的模块中导入了Wcf。# type: ignore注释用于告诉类型检查器（如mypy）忽略这一行的类型检查，这在类型检查可能引发错误时非常有用（例如，如果wcferry模块没有类型注解）
from wcferry import Wcf # type: ignore




def main(chat_type: int):

    db.create_database()  # 确保数据库已创建
    
    config = Config()# 创建配置类实例
    wcf = Wcf(debug=True)# 创建微信通信接口实例，开启调试模式

    def handler(sig, frame):# 定义信号处理函数
        print("u had pressed Ctrl+C, now exit...")
        robot.stopFlag=True
        wcf.cleanup()  # 退出前清理环境
        exit(0)

    signal.signal(signal.SIGINT, handler)# 将SIGINT信号（通常是Ctrl+C）绑定到handler函数

    robot = Robot(config, wcf, chat_type)# 创建机器人实例
    robot.LOG.info(f"WeChatRobot【{__version__}】成功启动···") # 日志记录机器人启动信息

    # 机器人启动发送测试消息 # 机器人启动时向'filehelper'发送启动成功的消息
    robot.sendTextMsg("机器人启动成功！", "filehelper")

    # 接收消息# 启动消息接收队列，避免消息丢失
    # robot.enableRecvMsg()     # 可能会丢消息？
    robot.enableReceivingMsg()  # 加队列

    # 设置定时任务，每天特定时间执行特定任务
    # 注意onEveryTime函数的参数是可调用对象，即函数或方法。
    
    # 每天8点收集23-8群聊摘要
    robot.onEveryTime("08:00", robot.saveAutoSummary, time_hours=9)
    # 每天12点收集8-12群聊摘要
    robot.onEveryTime("12:00", robot.saveAutoSummary, time_hours=4)
    # 每天17点收集12-17群聊摘要
    robot.onEveryTime("19:00", robot.saveAutoSummary, time_hours=7)
    # 每天23点收集17-23群聊摘要
    robot.onEveryTime("23:00", robot.saveAutoSummary, time_hours=4)
    # 每天24点发送每日聊天总结
    robot.onEveryTime("20:00", robot.sendDailySummary)
    # 测试
    # robot.postReceiverList(url='-----------------')# POST请求测试
    # robot.saveAutoSummary(time_hours = 4)
    robot.startProcessing(url='')# GET请求测试
    # robot.sendReport() # 发送图片测试

    # 每天 7 点发送天气预报
    #robot.onEveryTime("07:00", robot.sendWeatherReport)
    
    # 每天 7:30 发送新闻
    #robot.onEveryTime("07:30", robot.newsReport)

    # 每天 16:30 提醒发日报周报月报
    #robot.onEveryTime("16:30", ReportReminder.remind, robot=robot)

    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()


if __name__ == "__main__":
    #创建参数解析器
    parser = ArgumentParser()

    parser.add_argument('-c', type=int, default=0, help=f'选择模型参数序号: {ChatType.help_hint()}')
    # 添加一个整数类型的命令行参数 -c，默认值为0，帮助信息为 '选择模型参数序号: ' 加上 ChatType.help_hint() 返回的字符串
    args = parser.parse_args().c
    main(args)
