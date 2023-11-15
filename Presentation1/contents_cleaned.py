"""
深度清洗
"""

import os


# 從檔案讀取關鍵字
def get_keywords(directory, filename):
    keywords_2d = []
    full_path = os.path.join(directory, filename)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            keywords = [word.strip() for word in line.strip().split(",")]
            keywords_2d.append(keywords)
        return keywords_2d
    else:
        print(f"\033[92m File \033[91m{filename} \033[92min directory \033[91m{directory} \033[92mnot existed.\033[0m")
        return None


def filter_descriptions(descriptions, screen_words):
    filtered_descriptions = []
    for description in descriptions:
        # 將描述分割成單詞，並過濾掉 screen 列表中的單詞
        filtered_description = ' '.join(word for word in description.split() if word not in screen_words)
        filtered_descriptions.append(filtered_description)
    return filtered_descriptions


# 儲存檔案
def save_to_file_append(directory, filename, keywords, encoding='utf-8'):
    full_path = os.path.join(directory, filename)

    # 創建或取代檔案
    with open(full_path, 'a', encoding=encoding) as f:
        for keyword in keywords:
            f.write(keyword + "\n")


# 設定目錄和檔案名稱
directory_dataset = 'dataset'
patent_titles_file = 'patent_abstracts.txt'
patent_abstract_processed_file = 'patent_abstracts_processed.txt'
patent_abstract_cleaned = 'patent_abstract_cleaned.txt'

patent_contents_list = get_keywords(directory_dataset, patent_abstract_processed_file)
print(len(patent_contents_list))

screen = ['method', 'drone', 'uav', 'uavs', 'unman', 'unmanned', 'provide', 'include', 'use', 'one', 'base',
          'control', 'flight', 'first', 'one', 'two', 'second', 'determine', 'information', 'least', 'may',
          'wherein', 'present', 'accord', 'disclose', 'comprise', 'comprises', 'body', 'obtain', 'fly', 'system',
          'perform', 'operation', 'user', 'also', 'end', 'set', 'embodiment', 'part', 'figure', 'within', 'support',
          'discloses', 'vehicle', 'move']

for i, patent_abstract in enumerate(patent_contents_list):
    filtered_patent_contents_list = filter_descriptions(patent_abstract, screen)
    save_to_file_append(directory_dataset, patent_abstract_cleaned, filtered_patent_contents_list)
