#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config# 导入logging.config模块，用于配置日志系统
import os  # 导入os模块，用于操作文件和目录
import shutil # 导入shutil模块，用于复制文件
import yaml # 导入yaml模块，用于处理YAML配置文件


class Config(object):
    def __init__(self) -> None:
        self.reload()# 在类的实例被创建后，自动重新加载配置

    def _load_config(self) -> dict:
        pwd = os.path.dirname(os.path.abspath(__file__))
         # 获取当前文件的目录路径
        try:
             # 尝试打开并加载config.yaml文件
            with open(f"{pwd}/config.yaml", "rb") as fp:
                yconfig = yaml.safe_load(fp)
        except FileNotFoundError:
            # 如果config.yaml文件不存在，则复制模板文件，并加载它
            shutil.copyfile(f"{pwd}/config.yaml.template", f"{pwd}/config.yaml")
            with open(f"{pwd}/config.yaml", "rb") as fp:
                yconfig = yaml.safe_load(fp)

        return yconfig# 返回加载的配置字典

    def reload(self) -> None:
        yconfig = self._load_config()# 重新加载配置文件# 调用_load_config方法获取配置字典
        logging.config.dictConfig(yconfig["logging"])
        # 从配置文件中获取并设置各个部分的配置
        self.GROUPS = yconfig["groups"]["enable"]
        self.NEWS = yconfig["news"]["receivers"]
        self.REPORT_REMINDERS = yconfig["report_reminder"]["receivers"]
        # 获取可选配置，如果不存在则返回空字典
        self.CHATGPT = yconfig.get("chatgpt", {})
        self.CHATGPTt = yconfig.get("chatgptt",{})
        self.MOONSHOT = yconfig.get("moonshot",{})
        self.QWEN = yconfig.get("qwen",{})
        self.TIGERBOT = yconfig.get("tigerbot", {})
        self.XINGHUO_WEB = yconfig.get("xinghuo_web", {})
        self.CHATGLM = yconfig.get("chatglm", {})
        self.BardAssistant = yconfig.get("bard", {})
        self.ZhiPu = yconfig.get("zhipu", {})
        #get 方法用于从配置字典中读取可选的配置项，如果这些项不存在，它将返回一个空字典而不是引发错误。

    def update_config(self, key: str, value) -> None:
        pwd = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(f"{pwd}/config.yaml", "rb") as fp:
                yconfig = yaml.safe_load(fp)
            keys = key.split('.')
            sub_config = yconfig
            for k in keys[:-1]:
                sub_config = sub_config.setdefault(k, {})
            sub_config[keys[-1]] = value

            with open(f"{pwd}/config.yaml", "w", encoding='utf-8') as fp:
                yaml.safe_dump(yconfig, fp, default_flow_style=False, sort_keys=False, indent=2, allow_unicode=True)
            self.reload()
        except Exception as e:
            print(f"Error updating configuration: {e}")