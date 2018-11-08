import requests
from lxml import etree
import csv
from queue import Queue
from copy import deepcopy
import gevent
from gevent import monkey
import re
import time

monkey.patch_all()

base_url = "http://ee.jlu.edu.cn/szdw/wdkxygcx.htm"

key_list = ["研究方向", "科研项目", "讲授课程", "论文", "联系方式", "简历"]

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
}


class JiLingSpider(object):
    """docstring for  JiLingSpider"""

    def __init__(self, ):
        self.base_info = self.downloader(base_url)
        self.q = Queue()
        self.index = 0
        self.end = False
        pass

    def downloader(self, url):
        info = requests.get(url, headers=headers)
        return info.content.decode()

    def get_detail_url(self):
        base_html = etree.HTML(self.base_info)
        li_list = base_html.xpath('//ul[@class="js"]/li')
        c_faculty = base_html.xpath('//h3/a[3]/text()')[0]
        for li in li_list:
            name = li.xpath('./a/@title')[0]
            url = li.xpath('./a/@href')[0]
            url = "http://ee.jlu.edu.cn/" + url.replace("..", "")
            data = {
                "名字": name,
                "主页地址": url,
                "系": c_faculty,
                "学院": "电子科学与工程学院",
                "大学": "吉林大学"
            }
            self.q.put(data)
        url_list = base_html.xpath(
            '//li[@class="dq"]/a[contains(text(), "系")]/@href')
        self.index += 1
        if len(url_list) > self.index:
            next_url = "http://ee.jlu.edu.cn/szdw/" + url_list[self.index]
            self.base_info = self.downloader(next_url)
            return
        else:
            self.end = True

    def iter_aculty(self):
        while not self.end:
            self.get_detail_url()

    def get_detail_info(self):
        teacher_infos = []
        while True:
            time.sleep(5)
            if self.q.empty():
                break
            data = self.q.get()
            url = data["主页地址"]
            print(url)
            detail_info = self.downloader(url)
            detail_tree = etree.HTML(detail_info)
            infos = detail_tree.xpath(
                '//div[@class="v_news_content"]/p//text()')
            info = "".join(infos)
            data = self.extract_info_by_re(info, deepcopy(data))
            teacher_infos.append(data)
        self.save(teacher_infos)

    def extract_info_by_re(self, info, data):

        # 简历
        introductionre = r'(简\s*历)[\s\S]+?(一、|二、|三、|四、|五、|六、|七、)'
        introduction = re.search(introductionre, info)
        if introduction:
            introduction = introduction.group()[:-2].replace(
                "。", "。\n").replace("简", "").replace("历", "").strip()
        else:
            introduction = ""
        data["简历"] = introduction

        # 研究方向
        searchrex = r'研究方向[\s\S]+?(一、|二、|三、|四、|五、|六、|七、)'
        reserch = re.search(searchrex, info)
        if reserch:
            reserch = reserch.group()[:-2].replace(
                "。", "。\n").replace("研究方向", "").strip()
        else:
            reserch = ""
        data["研究方向"] = reserch

        # 讲授课程
        coursere = r'讲授课程[\s\S]+?(一、|二、|三、|四、|五、|六、|七、)'
        course = re.search(coursere, info)
        if course:
            course = course.group()[:-2].replace(
                "。", "。\n").replace("讲授课程", "").strip()
        else:
            course = ""
        data["讲授课程"] = course

        # 论文
        paperre = r'代表性工作及论文[\s\S]+?(一、|二、|三、|四、|五、|六、|七、)'
        paper = re.search(paperre, info)
        if paper:
            print("have")
            paper = paper.group()[:-2].replace(
                "。", "。\n").replace("代表性工作及论文", "").strip()
            if "专利" in paper:
                print(paper)
                paper_ = re.search(
                    r'[\s\S]+?(已\S+?专利|授\S+?专利|申\S+?专利)',
                    paper)
                if paper_:
                    paper_ = paper_.group()
                else:
                    paper_ = ""
                paper_ = re.sub("[已授]\S+?专利", "", paper_)
                patent = re.search(
                    r'专利[\s\S]+', paper).group().replace("；", "；\n")
                patent = re.sub('(专利:|专利)', '', patent)
                print("paten--:", patent)
                data["代表性工作及论文"] = paper_
                data["专利"] = patent
            else:
                data["代表性工作及论文"] = paper
                data["专利"] = ""

        conections = info.split("联系方式")[-1]
        phonerex = r"[()\d-]+"
        phone = re.search(phonerex, conections)
        phone = phone.group() if phone else ""
        data["电话"] = phone if len(phone) > 5 else ""

        emailregex = r"[-_\w\.]{0,64}@([-\w]{1,63}\.)*[-A-Za-z0-9]{1,63}"
        email = re.search(emailregex, conections)
        data["邮箱"] = email.group() if email else ""
        return data

    @staticmethod
    def save(content_list):
        with open('test.csv', 'a', encoding='UTF-8') as f:
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
            gevent.spawn(self.iter_aculty),
            gevent.spawn(self.get_detail_info)
        ])


if __name__ == '__main__':

    a = JiLingSpider()
    a.run()
