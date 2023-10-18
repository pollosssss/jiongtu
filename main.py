import os
import requests
import threading
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

url = 'https://www.gamersky.com/ent/147/'
pool = ThreadPoolExecutor(max_workers=10)
root_path = './images/'
path = ""
# 发送HTTP请求并获取页面内容
def fetch_pics():
    if not os.path.exists(root_path):
        os.mkdir(root_path)
    responses = requests.get(url)
    if responses.status_code == 200:
        soup = BeautifulSoup(responses.text, 'html.parser')
        target_ul = soup.find('ul', class_='pictxt')
        if target_ul:
            time_div = target_ul.find('div', class_='time')
            time = time_div.text.strip()
            time_trip = time[:10]
            global path
            path = f"{root_path}{time_trip}"
            if not os.path.exists(path):
                os.mkdir(path)
            else:
                return None
            first_a = target_ul.find('a')  # 替换为你要查找的class
            if first_a:
                first_a_url = first_a.get('href')
                images_pagination(first_a_url)


def images_pagination(root_url):
    store_images(root_url)
    for i in range(2, 20):
        page_url = f"{root_url[:-6]}_{i}.shtml"
        pool.submit(store_images, page_url)


def store_images(url):
    image_url_response = requests.get(url)
    if image_url_response.status_code == 200:
        image_soup = BeautifulSoup(image_url_response.text, 'html.parser')

        # 查找页面上的所有图片标签
        img_tags = image_soup.find_all('img', class_="picact")

        # 遍历每个图片标签，下载图片并保存到本地
        for img_tag in img_tags:
            img_url = img_tag.get('src')  # 获取图片的URL
            if img_url and not img_url.endswith(".gif"):
                img_url = urljoin(url, img_url)  # 构建完整的图片URL
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    # 从URL中提取图片文件名
                    global path
                    img_filename = os.path.join(path, os.path.basename(img_url))

                    # 保存图片到本地
                    with open(img_filename, 'wb') as img_file:
                        img_file.write(img_response.content)
                    print(f'Saved: {img_filename}')
                else:
                    print(f'Failed to download image: {img_url}')
    else:
        print(f'Failed to fetch URL: {url}')


if __name__ == '__main__':
    fetch_pics()

