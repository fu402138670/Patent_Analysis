"""
字元圖像化
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import Counter
from wordcloud import WordCloud
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from keywords_gen import get_keywords


# 設定目錄和檔案名稱
directory_dataset = 'dataset'
patent_abstract_processed_file = 'patent_abstract_cleaned.txt'

# 讀取Patent contents
patent_contents_list_ori = get_keywords(directory_dataset, patent_abstract_processed_file)

start = 0

# 排除異常字bug后，手動切割List繼續執行
patent_contents_list = patent_contents_list_ori[start:]

# 将每个句子分割成单词列表
patent_contents_list = [sentence[0].split() for sentence in patent_contents_list if sentence]

print(f"\33[92m Total patent abstracts : {len(patent_contents_list)}, starting fetch on {start}\33[0m")

# 訓練Word2Vec模型
model = Word2Vec(sentences=patent_contents_list, vector_size=50, min_count=1, workers=4)
model.save("word2vec.model")

# 展平
flattened_words = [word for sublist in patent_contents_list for word in sublist]
print(f"\33[92m Total key words : {len(flattened_words)}\33[0m")

# 計算詞頻
word_freq = Counter(flattened_words)
top_words = [item[0] for item in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:100]]  # top 50
word_vectors = [model.wv[word] for word in top_words if word in model.wv.key_to_index]
for word in top_words:
    print(f"{word}, {word_freq[word]}")

# PCA降維
pca = PCA(n_components=2)
result = pca.fit_transform(word_vectors)

# 計算圖標大小
sizes = [word_freq[word] * 3 for word in top_words[:len(word_vectors)]]  # 乘以10 圖標大小

# 繪製2D詞向量圖
plt.figure(figsize=(10, 6))
plt.scatter(result[:, 0], result[:, 1], s=sizes, alpha=0.6)
for i, word in enumerate(top_words[:len(word_vectors)]):
    plt.annotate(word, xy=(result[i, 0], result[i, 1]), fontsize=8)
plt.title('Word Embeddings Visualization')

# # 绘制3D词向量图
# fig = plt.figure(figsize=(10, 6))
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(result[:, 0], result[:, 1], result[:, 2], s=sizes, alpha=0.6)
# for i, word in enumerate(top_words[:len(word_vectors)]):
#     ax.text(result[i, 0], result[i, 1], result[i, 2], word, fontsize=8)
# plt.title('3D Word Embeddings Visualization')


# 繪製詞雲圖
wordcloud = WordCloud(background_color="white", width=800, height=400).generate_from_frequencies(word_freq)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
plt.show()
