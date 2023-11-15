"""
統計關鍵詞出現的次數
"""
import os


def get_keywords(directory, filename):
    # 從檔案讀取關鍵字
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


def find_keywords_in_range(texts, patterns):
    # 解析關鍵字和範圍
    results = []

    for pattern in patterns:
        comma_count = pattern.count(',')
        if comma_count == 0:
            keyword1 = pattern
            for i, word in enumerate(texts):
                if word == keyword1:
                    results.append((i, i))
        else:
            for i in range(comma_count):
                keyword1, parts = pattern.split('[', 1)
                range_start, range_end = int(parts.split(',', 1)[0]), int(parts.split(']', 1)[0].split(',')[1])
                keyword2 = parts.split(']', 1)[1].split('[')[0] if '[' in parts.split(']', 1)[1] \
                    else parts.split(']', 1)[1]
                pattern = pattern.split(']', 1)[1]

                for i, word in enumerate(texts):
                    if word == keyword1:
                        start_index = max(0, i + range_start)
                        end_index = min(i + range_end + 1, len(texts))
                        for j in range(start_index, end_index):
                            if texts[j] == keyword2 and j != i:
                                results.append((i, j))
    return results


# 設定目錄和檔案名稱
directory_dataset = 'dataset'
patent_abstract_processed_file = 'patent_abstracts_processed.txt'

# 讀取Patent contents
patent_contents = get_keywords(directory_dataset, patent_abstract_processed_file)
print(f'\33[92m Total quantity of patents: {len(patent_contents):,}')
patent_contents = [sentence[0].split() for sentence in patent_contents]
total_words = sum(len(sentence) for sentence in patent_contents)
print(f'\33[92m Total quantity of words: {total_words:,}')
unique_words = set(word for sentence in patent_contents for word in sentence)
print(f'\33[92m Total quantity of words: {len(unique_words):,}')

keyword_patterns = [
        ['control[-8,8]system[-8,8]autonomous[-8,8]system[-8,8]control[-8,8]configure', 'processor[-8,8]configure',
         'operate[-8,8]system'],
        ['image[-8,8]process', 'camera[-8,8]process', 'image[-8,8]capture[-8,8]video[-8,8]process', 'image[-8,8]analyze'],
        ['navigation[-8,8]position', 'navigation[-8,8]direction', 'navigation[-8,8]area', 'path', 'route'],
        ['power[-8,8]manage', 'energy[-8,8]manage', 'battery', 'power[-8,8]efficiency', 'battery[-8,8]storage'],
        ['communication[-8,8]wireless', 'transmit[-8,8]data', 'receive[-8,8]data', 'network[-8,8]wireless'],
        ['collaborate', 'coordinate', 'network[-8,8]integrate', 'multiple[-8,8]system', 'team'],
        ['sensor[-8,8]detect', 'detect[-8,8]detect', 'field[-8,8]detect', 'object[-8,8]detect', 'camera[-8,8]detect',
         'image[-8,8]detect', 'view[-8,8]detect'],
        ['remote[-8,8]control', 'autonomous[-8,8]system', 'remote[-8,8]operate', 'autonomous[-8,8]mode'],
        ['sensor[-8,8]detect', 'environment[-8,8]detect', 'field[-8,8]image', 'environment[-8,8]monitor'],
        ['land[-8,8]autonomous', 'land[-8,8]control', 'land[-8,8]system', 'land[-8,8]station'],
        ['load[-8,8]mount', 'load[-8,8]adjust', 'load[-8,8]balance', 'fix[-8,8]mount', 'mount[-8,8]couple'],
        ['maintenance', 'inspect[-8,8]status', 'check[-8,8]status', 'monitor[-8,8]status', 'minitor[-8,8]condition'],
]

for i, keyword_pattern in enumerate(keyword_patterns, start=1):
    search_results = []
    for j, patent_content in enumerate(patent_contents, start=1):
        search_result = find_keywords_in_range(patent_content, keyword_pattern)
        if search_result:
            search_results.append([j, search_result])
    print('\33[92m Technical area_{}, matched quantity = {}'.format(i, len(search_results)))
