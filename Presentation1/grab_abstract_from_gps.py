"""
從https://patents.google.com/patent/，根據專利號碼，抓取專利摘要
"""

import os
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


# 從檔案讀取IDS
def get_ids(directory, filename):
    ids = []
    full_path = os.path.join(directory, filename)
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            ids.append(line.strip())
        return ids
    else:
        print(f"\033[92m File \033[91m{filename} \033[92min directory \033[91m{directory} \033[92mnot existed.\033[0m")
        return None


# 儲存檔案
def save_to_file_append(directory, filename, keywords, encoding='utf-8'):
    full_path = os.path.join(directory, filename)

    # 創建或取代檔案
    with open(full_path, 'a', encoding=encoding) as f:
        for keyword in keywords:
            f.write(keyword + "\n")


def get_headers_from_initial_request(url):
    response = requests.get(url)
    response = requests.get(url)
    headers = response.headers
    if response.status_code == 200:
        custom_headers = {
            'User-Agent': headers.get('User-Agent', 'default_user_agent'),
            'Accept': headers.get('Accept', 'default_accept'),
            'Accept-Language': headers.get('Accept-Language', 'default_accept_language'),
            'Accept-Encoding': headers.get('Accept-Encoding', 'default_accept_encoding'),
            'Upgrade-Insecure-Requests': headers.get('Upgrade-Insecure-Requests', 'default_'),
            'Cache-Control': headers.get('Cache-Control', 'default_'),
            'Cookie': headers.get('Cookie', 'default_')
        }
    else:
        # print(f"Error {response.status_code}: Could not fetch the headers.")
        custom_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
                          "Chrome/118.0.0.0 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8," \
                        "application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-CN;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Cookie': 'OGPC=19010599-1:19010602-1:19008535-1:19039026-1:; OGP=-19010599:-19010602:-19008535:-19039026:;' \
                      'SID=cQi6vVNsJHqp2Lj2EdfUH2KIhp7D_n-AJdMuR-SyV5RxwoKmhe3YTyDXiOfqtbvT4u1bMg.;' \
                      '__Secure-1PSID=cQi6vVNsJHqp2Lj2EdfUH2KIhp7D_n-AJdMuR-SyV5RxwoKmBqwmuA1QnEVjXd6q6KbULA.; ' \
                      '__Secure-3PSID=cQi6vVNsJHqp2Lj2EdfUH2KIhp7D_n-AJdMuR-SyV5RxwoKm75nHE11BE6nH6qPTrC1qMw.; ' \
                      'HSID=ASnspjKgpkekNTWpJ; SSID=A2ujxK9JAAa82Cv2s; APISID=24JRX2rgrCAHM0Q8/AXvgpjj5B8sGmP07g; ' \
                      'SAPISID=xNyHJtKBQHYVxBKZ/AgwtT8kzlez1gDeHh; __Secure-1PAPISID=xNyHJtKBQHYVxBKZ/AgwtT8kzlez1gDeHh; ' \
                      '__Secure-3PAPISID=xNyHJtKBQHYVxBKZ/AgwtT8kzlez1gDeHh; 1P_JAR=2023-10-27-05; ' \
                      'AEC=Ackid1QSfhcipQ1uCOudzqLhs8WudxdBFCACWDrZMnVhSiU3__PR5kK1hw; ' \
                      'NID=511=k9YlM3VdrMAP6pMIuWTFlnVGxpWhyyIcboNTtkCxiZQa-8Ar-36cPkCz3yqam8yOEFqIhvJL6SR-POvPxFDsTUpbn4yJ' \
                      'wLPy1Q0z1Y_MWkf5qiMggk7ahCg6yq6T1Zmncb8ajWKaWEuZLTNKm94tQAFikTg9qAIIyrhfaGCdpKdSJrBb9J7A5vR9E7X3E4R9' \
                      'yfljYumlH9aSkUSlle8tKon1GyohJeE_pyy_8Dny2HcfqS7Frn8QvgmwnxumSz5QpFnUvVS_KM8rOt3XK0CndNNE7_AZYrHLjfVi' \
                      'LTLJTzmSRhoZE593-apBNoSQA00SPztsLDDtltXkUZj7-axvPfEY-89RzFoG9pQ6mT935cAO8Fb-FvQrqMMwETlESfef3pIo;' \
                      '__Secure-1PSIDTS=sidts-CjEBNiGH7vFTcU8-OGsbS5uEnaPrl1z67CfWawtmaahFIxGE8TxT8weNgupe1GFN4-nJEAA;' \
                      '__Secure-3PSIDTS=sidts-CjEBNiGH7vFTcU8-OGsbS5uEnaPrl1z67CfWawtmaahFIxGE8TxT8weNgupe1GFN4-nJEAA;' \
                      'SIDCC=ACA-OxNzu04rIT7n0rcUsKmz4VOP7TpnOaaVN8eNduakuuikrw9cXZAPnF1vdz4zrYwO5eL8BA;' \
                      '__Secure-1PSIDCC=ACA-OxPkusaB1_1R9V8ekrSoNX6iIqQiO7KvmrGqPPDykDCnQRxgDLf1G2Zvc0z97Eo3M-QniNY;' \
                      '__Secure-3PSIDCC=ACA-OxMqGAl20_KXlV3xNwKPQayMG2oquSJ58kpOiWrzwCPKVN5wz6SpNeiDVda-PcLyU60L3g'
        }
    return custom_headers


# 從Google專利搜索查詢專利ID的Abstract
def get_patent_abstract(patent_id):
    url = f'https://patents.google.com/patent/{patent_id}/en'

    headers = get_headers_from_initial_request(url)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # 找到所有class為"abstract"的<div>標籤
        abstracts = soup.find_all('div', {'class': 'abstract'})
        if not abstracts:
            abstracts = soup.find_all('abstract')
        # 初始化一個空列表來存儲所有的abstract文本
        abstract_texts = []
        # 遍歷每一個abstract並提取文本
        for abstract in abstracts:
            abstract_texts.append(abstract.text.strip())
        # print(abstract_texts)
        return abstract_texts

    else:
        print(f'Error {response.status_code}: Could not fetch the patent data.')
        # time.sleep(30)
        return []


# 設定目錄和檔案名稱
directory_dataset = 'dataset'
ids_file = 'patent_ids.txt'
patent_fetch_file = 'patent_abstracts.txt'

# 檢查並刪除已存在的檔案
patent_fetch_full_path = os.path.join(directory_dataset, patent_fetch_file)
if os.path.exists(patent_fetch_full_path):
    if input('Confirm to delete?'):
        os.remove(patent_fetch_full_path)

ids_list = get_ids(directory_dataset, ids_file)

patent_fetch = []
batch_size = 100  # 每100個ID儲存一次

for i, ids in enumerate(tqdm(ids_list, desc="Processing", unit="units")):
    abstracts = ' '.join(get_patent_abstract(ids))
    patent_fetch.append(f"{abstracts}")

    # 每100個ID儲存一次
    if (i + 1) % batch_size == 0:
        save_to_file_append(directory_dataset, patent_fetch_file, patent_fetch)
        patent_fetch = []  # 清空列表以處理下一批次

# 處理剩餘ID並儲存
if patent_fetch:
    save_to_file_append(directory_dataset, patent_fetch_file, patent_fetch)
