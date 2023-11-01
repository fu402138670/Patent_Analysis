import os


def label_lookup(symbol_path, symbol_list):
    # 檢查文件是否存在
    if not os.path.exists(symbol_path):
        print(f"\33[91m Error: File '{symbol_path}' does not exist.\33[0m")
        return False

    # 打開文件並讀取內容
    with open(symbol_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 將內容字符串轉換為字典
    content_dict = {}
    for item in content.split(" "):
        key, value = item.split(":")
        content_dict[key] = value

    # 根據符號列表生成符號內容列表
    symbol_content = [content_dict.get(symbol, "未找到") for symbol in symbol_list]

    return symbol_content


