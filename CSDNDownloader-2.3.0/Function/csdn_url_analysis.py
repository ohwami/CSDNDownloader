import requests
import parsel
import tomd
import os
import re
import datetime
from urllib.parse import urlparse

from Function.public_function import *

head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52"
}

class CSDN_URL_Analysis():
    # CSDN链接解析类
    def __init__(self, url):
        if len(url) == 1:
            url = url[0]
        self.url = url
        self.gen_md_by_one_url()

    def gen_md_by_one_url(self):
        # 功能封装
        self.get_csdn_texts()
        self.save_md_file_by_local_text()

    def get_csdn_texts(self):
        # 获取文本
        html = requests.get(url=self.url, headers=head).text
        page = parsel.Selector(html)

        # 获取标题
        title = page.css(".title-article::text").get()
        res = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")
        restr = ''
        res.sub(restr, title)

        # 获取内容
        content = page.css("article").get()

        # 提取图片链接并下载
        self.images = []  # 保存本地图片路径
        for img_tag in page.css("article img").getall():
            img_url = re.search(r'<img.*?src="(.*?)"', img_tag)
            if img_url:
                img_url = img_url.group(1)
                local_img_path = self.download_image(img_url)
                if local_img_path:
                    self.images.append((img_url, local_img_path))

        # 替换文章中的图片链接为本地路径
        for img_url, local_img_path in self.images:
            content = content.replace(img_url, local_img_path)

        # 转换为markdown文件
        text = tomd.Tomd(content).markdown

        # 标题及内容存储
        self.title = title
        self.check_title_legal()
        self.text = text

    def download_image(self, img_url):
        try:
            response = requests.get(img_url, headers=head, stream=True)
            if response.status_code == 200:
                # 获取图片保存目录
                img_dir = os.path.join(self.gen_wd(), "images")
                os.makedirs(img_dir, exist_ok=True)

                # 提取文件名并保存
                img_name = os.path.basename(urlparse(img_url).path)
                local_img_path = os.path.join(img_dir, img_name)
                with open(local_img_path, "wb") as f:
                    f.write(response.content)
                return local_img_path
        except Exception as e:
            print(f"Failed to download image {img_url}: {e}")
        return None

    # 由于Windows系统要求文件名不得包含“\\/:*?\"<>|”，故需要做合法性检查，替换所有非法字符为空白
    def check_title_legal(self):
        self.title = re.sub(r'[\\/:*?\"<>|]', ' ', self.title)

    def gen_wd(self):
        # 校验存储路径
        currentWD = get_current_wd()

        current_d = datetime.datetime.today()
        current_y = current_d.year
        current_m = current_d.month
        saveGeneralWD = os.path.join(currentWD, "download")
        full_mkdir(saveGeneralWD)
        yearwd = os.path.join(saveGeneralWD, str(current_y))
        full_mkdir(yearwd)
        monthwd = os.path.join(yearwd, str(current_m))
        full_mkdir(monthwd)
        return monthwd

    def save_md_file_by_local_text(self):
        # 转换为markdown 文件
        saveWD = self.gen_wd()
        filename = self.title + ".md"
        filenameWithD = os.path.join(saveWD, filename)
        with open(filenameWithD, mode="w", encoding="utf-8") as f:
            f.write("# " + self.title + "\n\n")
            f.write(self.text)


def url_lise_gen(urltext):
    # 解析一个或多个url
    reexp_http = 'http[s]?://(?:(?!http[s]?://)[a-zA-Z]|[0-9]|[$\-_@.&+/]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urllist = re.findall(reexp_http, urltext)
    if len(urllist) < 1:
        return [], 0
    elif len(urllist) == 1:
        return urllist[0], 1
    else:
        no_repeat_url_list = list(set(urllist))
        no_repeat_url_list.sort(key=urllist.index)
        return no_repeat_url_list, len(no_repeat_url_list)


def url_text_analysis(urltext):
    # 核心功能
    [url_list, urlnum] = url_lise_gen(urltext)
    titlelist = []
    if urlnum == 0:
        pass
    elif urlnum == 1:
        a = CSDN_URL_Analysis(url_list)
        titlelist.append(a.title)
    else:
        for url in url_list:
            a = CSDN_URL_Analysis(url)
            titlelist.append(a.title)
    return titlelist


if __name__ == '__main__':
    # 单url解析
    url_text_analysis("https://jia666666.blog.csdn.net/article/details/81534260")
