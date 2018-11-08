import requests
from lxml import etree
import csv
from queue import Queue
import gevent
from copy import deepcopy
import re
from gevent import monkey
monkey.patch_all()

base_url = "http://chem.jlu.edu.cn/szll/js2.htm"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}


class JiLingSpider(object):
    """docstring for  JiLingSpider"""
    def __init__(self,):
        self.base_info = self.downloader(base_url)
        self.q = Queue()

    def downloader(self, url):
        info = requests.get(url, headers=headers)
        return info.content.decode()

    def get_detail_url(self):
        base_html = etree.HTML(self.base_info)
        teachers = base_html.xpath('//div[@class="teacher"]/ul/li')
        for one in teachers:
            title = one.xpath('./text()')[-1]
            url = one.xpath('./a/@href')[0]
            name = one.xpath('./a/text()')[0]
            data = {
                "职位": title,
                "名字": name,
                "主页地址": url}
            self.q.put(data)
            print(title, name, url)
        next_page_url_ = base_html.xpath('//a[contains(text(), "下页")]/@href')
        if next_page_url_:
            if "js2" in next_page_url_[0]:
                next_page_url = "http://chem.jlu.edu.cn/szll/" + \
                    next_page_url_[0]
            else:
                next_page_url = "http://chem.jlu.edu.cn/szll/js2/" + \
                    next_page_url_[0]
            self.base_info = self.downloader(next_page_url)
            self.get_detail_url()

    def get_detail_info(self):
        data = self.q.get()
        url = data["url"]
        detail_info = self.downloader(url)
        info_html = etree.HTML(detail_info)
        data = self.extract_red_head_page_info(info_html, deepcopy(data))

    def extract_red_head_page_info(self, info_html, data):
        name_box_info = info_html.xpath('//div[@class="namebx"]//text()')
        name_box_info = "".join(name_box_info)
        emailregex = r"[-_\w\.]{0,64}@([-\w]{1,63}\.)*[-A-Za-z0-9]{1,63}"
        email = re.search(emailregex, name_box_info)
        data["邮箱"] = email.group() if email else ""

        return data

    @staticmethod
    def save(content_list):
        with open('化学学院.csv', 'a', encoding='UTF-8') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=['系', '名字', '主页地址', '电话', '邮箱',
                                                '专利', '代表性工作及论文', '研究方向',
                                                '讲授课程', '学院', '大学', '承担科研项目及获奖',
                                                "简历"])
            writer.writeheader()
            for content in content_list:
                writer.writerow(content)

    def run(self):
        gevent.joinall([
            gevent.spawn(self.get_detail_url),
            gevent.spawn(self.get_detail_info)
            ])


if __name__ == '__main__':

    a = JiLingSpider()
    a.run()

