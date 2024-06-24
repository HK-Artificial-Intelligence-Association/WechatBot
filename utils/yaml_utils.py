
import sqlite3
import yaml
from db import fetch_roomids_from_db
from configuration import Config

yaml_path = 'config.yaml'

def update_yaml():
    config = Config()
    room_ids = fetch_roomids_from_db()
    config.update_config('groups.enable', room_ids)
    print("--------------------已更新配置文件--------------------")
