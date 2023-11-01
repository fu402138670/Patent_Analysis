import os
import cv2
from PIL import Image, ImageDraw, ImageFont
import re
import matplotlib.pyplot as plt
import easyocr
import numpy as np


def image_ocr(image_path):
    # 創建EasyOCR讀者實例
    reader = easyocr.Reader(['en'])

    # 檢查文件是否存在
    if not os.path.exists(image_path):
        print(f"\33[91m Error: File '{image_path}' does not exist. \33[0m")
    else:
        original_image = cv2.imread(image_path)

        # 檢查圖像是否成功加載
        if original_image is None:
            print(f"\33[91m Error: Could not read the image at \33[95m'{image_path}'. \33[0m")
            return False

        else:
            # 獲取圖像的尺寸
            height, width = original_image.shape[:2]

            # 設定新的尺寸
            new_height = int(height * 1)
            new_width = int(width * 1)
            image = cv2.resize(original_image, (new_width, new_height))

            # 高斯模糊
            image = cv2.GaussianBlur(image, (3, 3), 0)

            # 使用EasyOCR進行文本識別
            result = reader.readtext(image, detail=2, paragraph=False, contrast_ths=0.05, adjust_contrast=0.7,
                                     width_ths=0.5, text_threshold=0.8, link_threshold=0.4)

            # 創建一個空的列表來存儲所有識別到的文本
            detected_texts = []

            # 在圖片上標記識別到的文本
            for i, (bbox, text, prob) in enumerate(result, start=1):
                # 解析邊界框
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                br = (int(br[0]), int(br[1]))

                # 在終端機中打印識別到的文本
                # print(f"Detected text: {text}, Probability: {prob}")

                # 使用正則表達式找到所有的數字, 將識別到的文本添加到列表中
                text = re.findall(r'\d+', text)
                detected_texts.append([bbox, text, prob])
                # print(f"{i}, Detected text: {text}")

            return image, detected_texts


def draw_image(image, detected_texts, symbol_descriptions, font_file):
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    font = ImageFont.truetype(font_file, 35)  # 中文字體路徑

    # 在圖片上標記識別到的文本
    for i, (bbox, text, prob) in enumerate(detected_texts, start=1):
        # 解析邊界框
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1]))
        br = (int(br[0]), int(br[1]))

        # 繪製邊界框和文本
        draw.rectangle([tl, br], outline=(0, 255, 0), width=2)
        draw.text((int(tl[0]), int(tl[1])-35), str(i), font=font, fill=(255, 0, 0))

    # 設定文字的起始位置（左下角）
    x1, y = 50, image.shape[0] - 50  # 第一欄
    x2 = x1 + 500  # 第二欄
    line_height = 40  # 每行的高度

    # 在圖像上添加每一行標簽說明
    for i, label in enumerate(symbol_descriptions):
        x = x1 if i % 2 == 0 else x2  # 選擇第一欄或第二欄
        draw.text((x, y), label, font=font, fill=(255, 0, 0))  # 紅色
        if i % 2 != 0:  # 如果是第二欄，移動到下一行
            y -= line_height

    # 顯示或保存
    image_pil.show()
