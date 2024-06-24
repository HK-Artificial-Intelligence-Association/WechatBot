from configuration import Config
from db import fetch_roomids_from_db


def update_yaml():
    config = Config()
    room_ids = fetch_roomids_from_db()
    #调用 config 对象的 update_config 方法，将 groups.enable 配置项更新为从数据库中获取的 room_ids。
    config.update_config('groups.enable', room_ids)
    print(room_ids)
    print(config.GROUPS)
    config.GROUPS = room_ids
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(config.GROUPS)
    config.reload()



config = Config()
room_ids = fetch_roomids_from_db()

config.update_config('groups.enable', room_ids)

