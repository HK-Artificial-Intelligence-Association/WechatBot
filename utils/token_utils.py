import tiktoken
from configuration import Config


def num_tokens_from_string(string: str, model_name: str) -> int:
    """
    parameter:
        string:str 参数接受的文本字符串，函数计算此字符串的令牌数
        model_name: str print (model_name) = gpt-3.5-turbo 模型的名称
    
    mid:
        encoding_name:model_name的编码名称,格式为encoding_name == <Encoding 'o200k_base'>
        encoding_name.name == o200k_base

    result
        num_tokens:int类型的数字,token数
    
    """
    # Returns the number of tokens in a text string.

    encoding_name = tiktoken.encoding_for_model(model_name)

    encoding = tiktoken.get_encoding(encoding_name.name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# print(tiktoken.encoding_for_model('gpt-4o').name)
# print(num_tokens_from_string('tiktoken is great!', 'o200k_base'))
# print(num_tokens_from_string('大模型是什么？', 'o200k_base'))

# 获得使用的GPT模型
def get_gptmodel_name() -> str:
    config = Config().CHATGPT
    return config['model']
