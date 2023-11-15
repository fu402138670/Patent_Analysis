"""
文字檔案内容清洗
"""

import string
import nltk
import os
import math
from keywords_gen import get_keywords
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from collections import Counter
from googletrans import Translator
from tqdm import tqdm


# 設定目錄和檔案名稱
directory_config = 'config'
directory_dataset = 'dataset'
patent_titles_file = 'patent_abstracts.txt'
patent_abstract_processed_file = 'test_only.txt'

# 定義NLP數據集和其相對應的目錄
datasets = {
    'stopwords': 'corpora/stopwords',
    'punkt': 'tokenizers/punkt',
    'wordnet': 'corpora/wordnet',
    'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger'
}

# 讀取Patent contents
patent_contents_list_ori = get_keywords(directory_dataset, patent_titles_file)
start_reading = 1500  # List的第一個是0
patent_contents_list = patent_contents_list_ori[start_reading:]  # 排除異常字bug后，手動切割List繼續執行
print(f"\33[92m Total patent abstracts : {len(patent_contents_list)}, starting fetch on {start_reading}\33[0m")

# 檢查並下載未下載的數據集
for dataset, path in datasets.items():
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(dataset)


# 儲存檔案
def save_to_file_append(directory, filename, keywords, encoding='utf-8'):
    full_path = os.path.join(directory, filename)

    # 創建或取代檔案
    with open(full_path, 'a', encoding=encoding) as f:
        for keyword in keywords:
            f.write(keyword + "\n")


def get_wordnet_pos(treebank_tag):
    """將treebank POS標籤映射到WordNet POS標籤"""
    if treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag.startswith('J'):
        return wordnet.ADJ
    else:
        return wordnet.NOUN  # 默認為名詞


def get_synonyms(word, top_n=10):
    """取得詞的同義詞列表, 僅考慮前top_n個同義字"""
    synonyms = set()
    synsets = wordnet.synsets(word)
    for idx, syn in enumerate(synsets):
        for lemma in syn.lemmas()[:top_n]:
            synonyms.add(lemma.name())
        if idx >= top_n:
            break
    return list(synonyms)


def merge_synonyms(lemmatized_freq):
    """如果為同義詞，合并計算頻率"""
    merged_freq = dict()

    for word, freq in lemmatized_freq.items():
        # 查找word的同義詞
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())

        total_freq = freq
        for syn_word in synonyms:
            if syn_word in lemmatized_freq and syn_word != word:
                total_freq += lemmatized_freq[syn_word]

        merged_freq[word] = total_freq

    return merged_freq


def remove_stopwords(text):
    """過濾停用字"""
    stop_words = set(stopwords.words('english'))
    print(len(stop_words))
    print(stop_words)
    word_tokens = word_tokenize(text)
    filtered = [word for word in word_tokens if word not in stop_words]
    return ' '.join(filtered)


def translate_to_english(text):
    translator = Translator()
    # 偵測文本語言
    detected_language = translator.detect(text).lang
    # 如果文本不是英文，則進行翻譯
    if detected_language != 'en':
        translated = translator.translate(text, src=detected_language)
        return translated.text
    else:
        return text


def preprocess_words(patent_contents, batch_index):
    """刪除標點符號、轉換小寫、翻譯為英文、刪除停用字、詞形還原"""
    preprocessed = []
    lemmatizer = WordNetLemmatizer()
    for n, patent_content in tqdm(enumerate(patent_contents), total=len(patent_contents),
                                  desc=f'Processing batch {batch_index}'):
        if isinstance(patent_content, list):
            content = ' '.join([str(item) for item in patent_content if isinstance(item, str)])
            content = content.lower()
            content = content.translate(str.maketrans('', '', string.punctuation))
            content = translate_to_english(content)
            content = ''.join([j for j in content if not j.isdigit()])
            filtered = remove_stopwords(content)
            word_tokens = word_tokenize(filtered)
            lemmatized = [lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in nltk.pos_tag(word_tokens)]
            lemmatized_freq = Counter(lemmatized)
            merged = merge_synonyms(lemmatized_freq)
            preprocessed.append(' '.join(merged.keys()))
        else:
            tqdm.write(f"Warning: No content found. Location: {n}")
    return preprocessed


batch_size = 500  # 一次處理500筆資料
total_batch = math.ceil(len(patent_contents_list)/batch_size)

for i in range(total_batch):
    ind = i * batch_size
    processed_batch = preprocess_words(patent_contents_list[ind:ind+batch_size], i)
    save_to_file_append(directory_dataset, patent_abstract_processed_file, processed_batch)
