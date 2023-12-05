# pr_hw#02C_111c51502
# CY Chingyao Fu,
# AI-EMBA Program, NTUT
# 2023/11/01


import os
from image_ocr import image_ocr, draw_image
from label_match import label_lookup


# 設定目錄和圖案檔案名稱
directory_config = 'config'
directory_figure = 'figure'
directory_symbol = 'dataset'
fig_file = 'Patent_Analysis.jpg'
symbol_file = 'symbol_111106564.txt'
font_file = 'kaiu.ttf'

image_path = os.path.join(directory_figure, fig_file)
symbol_path = os.path.join(directory_symbol, symbol_file)
font_path = os.path.join(directory_config, font_file)

# 文字識別
image, detected_text = image_ocr(image_path)

# for i, (bbox, text, prob) in enumerate(detected_text, start=1):
#     print(f"\33[92m Detected #{i} text: {text[0]}\33[0m")

# 從符號説明檔案抓取對應説明
label_list = [item[1][0] for item in detected_text]
label_contents = label_lookup(symbol_path, label_list)

# 將標簽和對應説明組合為List
symbol_descriptions = []
for i in range(len(label_list)):
    symbol = label_list[i] + ':' + label_contents[i]
    symbol_descriptions.append(symbol)

# 重繪圖面
draw_image(image, detected_text, symbol_descriptions, font_path)
