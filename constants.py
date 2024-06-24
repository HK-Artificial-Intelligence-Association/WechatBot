from enum import IntEnum, unique


@unique
class ChatType(IntEnum):
    # UnKnown = 0  # 未知, 即未设置
    TIGER_BOT = 1  # TigerBot
    CHATGPT = 2  # ChatGPT
    CHATGPTt = 3  # ChatGPT
    MOONSHOT = 4 #Moonshot
    QWEN = 5
    XINGHUO_WEB = 6  # 讯飞星火
    CHATGLM = 8  # ChatGLM
    BardAssistant = 9  # Google Bard
    ZhiPu = 10  # ZhiPu

    @staticmethod
    #is_in_chat_types 是一个静态方法，用于检查给定的 chat_type 是否在支持的聊天类型列表中。
    def is_in_chat_types(chat_type: int) -> bool:
        if chat_type in [ChatType.TIGER_BOT.value, ChatType.CHATGPT.value,ChatType.CHATGPTt.value,ChatType.MOONSHOT.value,ChatType.QWEN.value,
                         ChatType.XINGHUO_WEB.value, ChatType.CHATGLM.value,
                         ChatType.BardAssistant.value]:
            return True
        return False

    @staticmethod
    def help_hint() -> str:
        return str({member.value: member.name for member in ChatType}).replace('{', '').replace('}', '')
