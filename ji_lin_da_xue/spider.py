import requests
from lxml import etree
import csv
from queue import Queue
import gevent 
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
        print(len(teachers), teachers)
        for one in teachers:
            title = one.xpath('./text()')[-1]
            url = one.xpath('./a/@href')[0]
            name = one.xpath('./a/text()')[0]
            data = {
                "title": title,
                "name": name,
                "url": url}
            self.q.put(data)
            print(title, name, url)
        next_page_url_ = base_html.xpath('//a[contains(text(), "下页")]/@href')
        print("???????: ", next_page_url_	)
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
        detail_tree = etree.HTML(detail_info)
        email = detail_tree.xpath('')

    def run(self):
        gevent.joinall([
            gevent.spawn(self.get_detail_url),
            gevent.spawn(self.get_detail_info)
            ])


if __name__ == '__main__':

    a = JiLingSpider()
    a.run()

