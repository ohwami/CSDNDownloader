import requests
import parsel
import tomd
import os
import re
import datetime

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
        title = res.sub(restr, title)
        self.title = title
        self.check_title_legal()

        # 获取内容
        content = page.css("article").get()

        # 下载图片
        content = self.download_and_replace_images(content)

        # 转换为 Markdown
        text = tomd.Tomd(content).markdown
        self.text = text

    def download_and_replace_images(self, content):
        # 找出所有图片
        img_tags = re.findall(r'<img\s+[^>]*src="([^"]+)"', content)

        # 创建图片存储文件夹
        img_folder = os.path.join(self.gen_wd(), "images")
        os.makedirs(img_folder, exist_ok=True)

        for img_url in img_tags:
            try:
                # 下载图片
                img_data = requests.get(img_url, headers=head).content
                img_name = os.path.basename(img_url).split("?")[0]  # 去掉可能的 URL 参数
                img_path = os.path.join(img_folder, img_name)

                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)

                # 替换为相对路径
                relative_img_path = os.path.join("images", img_name).replace("\\", "/")
                content = content.replace(img_url, relative_img_path)
            except Exception as e:
                print(f"图片下载失败：{img_url}, 错误信息：{e}")

        return content

    def check_title_legal(self):
        # 检查标题是否合法
        illegal_chars = "\\/:*?\"<>|"
        for char in illegal_chars:
            self.title = self.title.replace(char, ' ')

    def gen_wd(self):
        # 校验存储路径并创建文章目录
        current_wd = os.getcwd()
        current_date = datetime.datetime.today()
        save_dir = os.path.join(current_wd, "download", str(current_date.year), str(current_date.month), self.title)

        # 创建文件夹
        os.makedirs(save_dir, exist_ok=True)
        return save_dir

    def save_md_file_by_local_text(self):
        # 保存为 Markdown 文件
        save_dir = self.gen_wd()
        filename = f"{self.title}.md"
        file_path = os.path.join(save_dir, filename)

        with open(file_path, mode="w", encoding="utf-8") as f:
            f.write("# " + self.title + "\n")
            f.write(self.text)

        print(f"Markdown 文件已保存：{file_path}")


def url_lise_gen(urltext):
    # 解析一个或多个 URL
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
    # 单 URL 测试
    url_text_analysis("https://jia666666.blog.csdn.net/article/details/81534260")
