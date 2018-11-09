# -*- coding:utf-8 -*-
# Date   : Fri Nov 09 12:42:05 2018 +0800
# Author : Rory Xiang

import requests
from lxml import etree
import csv
from queue import Queue
import gevent
from copy import deepcopy
import re
import time
from gevent import monkey
monkey.patch_all()

base_url = "http://chem.jlu.edu.cn/szll/js2.htm"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}

phonerex = r"(86)?(1[345789]\\d{9})|\d{3，4}-\d{5-9}"


class JiLingSpider(object):
    """docstring for  JiLingSpider"""
    def __init__(self,):
        self.base_info = self.downloader(base_url)
        self.q = Queue()

    def downloader(self, url):
        info = requests.get(url, headers=headers)
        if info.status_code == 404:
            return None
        return info.content.decode()

    def get_detail_url(self):
        base_html = etree.HTML(self.base_info)
        teachers = base_html.xpath('//div[@class="teacher"]/ul/li')
        for one in teachers:
            title = one.xpath('./text()')[-1]
            url = one.xpath('./a/@href')[0]
            if "../" in url:
                url = "http://chem.jlu.edu.cn/" + url.replace("../", "")
            if url[0] != "h":
                url = "h" + url
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
        teachers = []
        time.sleep(3)
        while True:
            if self.q.empty():
                break
            data = self.q.get(timeout=180)
            url = data["主页地址"]
            print("??????", url, data)
            detail_info = self.downloader(url)
            if not detail_info:
                teachers.append(data)
                continue
            info_html = etree.HTML(detail_info)
            data = self.extract_info(info_html, deepcopy(data))
            print("##", data)
            teachers.append(data)
        self.save(teachers)

    def extract_info(self, info_html, data):
        """
        判断使用什么提取方法，每个格式的页面提取方法不一样
        :param info_html:
        :param data:
        :return:
        """
        red_flag = info_html.xpath('//div[@class="t"]//h2/text()')
        red_flag = "".join(red_flag)
        if "基本信息" in red_flag:
            data = self.extract_red_head_page_info(info_html, data)
            return data
        yellow_flag = info_html.xpath('//div[@id="cqjdzwmbzylg"]/@class')
        yellow_flag = "".join(yellow_flag)
        if "logo" in yellow_flag:
            data = self.extract_yello_head_page_info(info_html, data)
            return data
        wite_back_flag = info_html.xpath(
            '//div[@class="PersonalContent"]/ul[1]/li[2]/strong//text()')
        wite_back_flag = "".join(wite_back_flag)
        if data["名字"] in wite_back_flag:
            data = self.extract_wite_back_page_info(info_html, data)
            return data
        leaf_flag = info_html.xpath(
            '//div[@class="banner-con-right"]//h3/text()')
        leaf_flag = "".join(leaf_flag)
        if data["名字"] in leaf_flag:
            data = self.extract_leaf_head_page_info(info_html, data)
            return data
        green_flag = info_html.xpath('//h4[@class="tab_title"]/text()')
        green_flag = "".join(green_flag)
        print("^^^^^^^", green_flag)
        if data["名字"] in green_flag:
            data = self.extract_green_back_page_info(info_html, data)
            return data
        return data

    def extract_red_head_page_info(self, info_html, data):
        name_box_info = info_html.xpath('//div[@class="namebx"]//text()')
        name_box_info = "".join(name_box_info)
        print("%%%%%%%%%", name_box_info)
        emailregex = r"[-_\w\.]{0,64}@([-\w]{1,63}\.)*[-A-Za-z0-9]{1,63}"
        email = re.search(emailregex, name_box_info)
        data["邮箱"] = email.group() if email else ""
        phone = re.search(phonerex, name_box_info)
        print(phone)
        phone = phone.group() if phone else ""
        data["电话"] = phone if len(phone) > 5 else ""
        # 研究方向
        researchs = info_html.xpath('//h2[contains(text(), '
                                    '"研究方向")]/../following::div[1]//text()')
        research = "".join(researchs).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["研究方向"] = research
        # 教育经历
        educations = info_html.xpath('//h2[contains(text(), '
                                     '"教育经历")]/../following::div[1]//text()')
        education = "".join(educations).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["工作经历"] = education
        # 工作经历
        resumes = info_html.xpath('//h2[contains(text(), '
                                  '"工作经历")]/../following::div[1]//text()')
        resume = "".join(resumes).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["工作经历"] = resume
        #个人简介
        introductions = info_html.xpath('//h2[contains(text(), '
                                        '"个人简介")]/../following::div[1]//text()')
        introduction = "".join(introductions).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["个人简介"] = introduction
        return data

    def extract_yello_head_page_info(self, info_html, data):
        # 个人简介
        introductions = info_html.xpath(
            '//h2[contains(text(), "研究方向")]/../following::div[1][cont'
            'ains(@class, "ct")]//text()')
        introduction = "".join(introductions).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["个人简介"] = introduction
        # 联系方式
        connections = info_html.xpath(
            '//h2[contains(text(), "其他联系方式")]/../following::div[1][cont'
            'ains(@class, "ct")]//text()')
        connection = "".join(connections)
        emailregex = r"[-_\w\.]{0,64}@([-\w]{1,63}\.)*[-A-Za-z0-9]{1,63}"
        email = re.search(emailregex, connection)
        data["邮箱"] = email.group() if email else ""
        phone = re.search(phonerex, connection)
        phone = phone.group() if phone else ""
        data["电话"] = phone if len(phone) > 5 else ""
        # 工作经历
        resumes = info_html.xpath(
            '//h2[contains(text(), "工作经历：")]/../following::div[1][cont'
            'ains(@class, "ct")]//text()')
        resume = "".join(resumes).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["工作经历"] = resume
        # 教育经历
        educations = info_html.xpath(
            '//h2[contains(text(), "教育经历：")]/../following::div[1][cont'
            'ains(@class, "ct")]//text()')
        education = "".join(educations).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["教育经历"] = education
        # 社会兼职
        society_positions = info_html.xpath(
            '//h2[contains(text(), "社会兼职：")]/../following::div[1][cont'
            'ains(@class, "ct")]//text()')
        society_position = "".join(society_positions).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["社会兼职"] = society_position
        # 研究方向：
        researchs = info_html.xpath(
            '//h2[contains(text(), "研究方向：")]/../following::div[1][cont'
            'ains(@class, "ct")]//text()')
        research = "".join(researchs).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["研究方向"] = research
        return data

    def extract_leaf_head_page_info(self, info_html, data):
        name_box_infos = info_html.xpath(
            '//div[@class="banner-con-right"]//text()')
        name_box_info = "".join(name_box_infos)
        emailregex = r"[-_\w\.]{0,64}@([-\w]{1,63}\.)*[-A-Za-z0-9]{1,63}"
        email = re.search(emailregex, name_box_info)
        data["邮箱"] = email.group() if email else ""
        phone = re.search(phonerex, name_box_info)
        phone = phone.group() if phone else ""
        data["电话"] = phone if len(phone) > 5 else ""
        # 个人简介
        introduces = info_html.xpath(
            '//div[contains(text(), "个人简介")]/following::div[1]//text()')
        introduce = "".join(introduces).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["个人简介"] = introduce
        # 教育经历
        educations = info_html.xpath('//div[@class="conWrap"]/div[1]//text()')
        education = "".join(educations).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["教育经历"] = education
        # 工作经历
        works = info_html.xpath('//div[@class="conWrap"]/div[2]//text()')
        work = "".join(works).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["教育经历"] = work
        return data

    def extract_wite_back_page_info(self, info_html, data):
        # 个人简介
        introduces = info_html.xpath(
            '//div[contains(text(), "个人简介")]/following::div[1]//text()')
        introduce = "".join(introduces).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["个人简介"] = introduce
        # 教育经历
        educations = info_html.xpath(
            '//div[contains(text(), "教育经历")]/following::div[1]//text()')
        education = "".join(educations).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["教育经历"] = education
        # 工作经历
        works = info_html.xpath(
            '//div[contains(text(), "工作经历")]/following::div[1]//text()')
        work = "".join(works).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["工作经历"] = work
        # 社会兼职
        society_positions = info_html.xpath(
            '//div[contains(text(), "社会兼职")]/following::div[1]//text()')
        society_position = "".join(society_positions).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["社会兼职"] = society_position
        # 研究方向
        research_directions = info_html.xpath(
            '//div[contains(text(), "研究方向")]/following::div[1]//text()')
        research_direction = "".join(research_directions).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("。", "。\n")
        data["研究方向"] = research_direction
        # 联系方式
        connections = info_html.xpath(
            '//div[contains(text(), "联系方式")]/following::div[1]//text()')
        connection = "".join(connections)
        emailregex = r"[-_\w\.]{0,64}@([-\w]{1,63}\.)*[-A-Za-z0-9]{1,63}"
        email = re.search(emailregex, connection)
        data["邮箱"] = email.group() if email else ""
        phone = re.search(phonerex, connection)
        phone = phone.group() if phone else ""
        data["电话"] = phone if len(phone) > 5 else ""
        return data

    def extract_green_back_page_info(self, info_html, data):
        name = data["名字"]
        connections = info_html.xpath(
            f'//h4[contains(text(), "{name}")]/following::ul[1]//text()')
        connection = "".join(connections)
        emailregex = r"[-_\w\.]{0,64}@([-\w]{1,63}\.)*[-A-Za-z0-9]{1,63}"
        email = re.search(emailregex, connection)
        data["邮箱"] = email.group() if email else ""
        # 研究方向
        researchs = info_html.xpath(
            '//h4[contains(text(),"研究方向")]/following::ul[1]//text()')
        research = "\n".join(researchs).replace(
            "\n", "").replace("\t", "").replace("\xa0", "")
        data["研究方向"] = research

        # 论文著作
        thesis = info_html.xpath(
            '//span[contains(text(),"代表性论文")]/../../following::div[2]//text()')
        thesis = "".join(thesis).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("浏览", "浏览\n")
        data["论文著作"] = thesis

        # 专利
        paten = info_html.xpath(
            '//span[contains(text(),"专利")]/../../following::div[2]//text()')
        paten = "".join(paten).replace(
            "\n", "").replace("\t", "").replace("\xa0", "").replace("浏览", "浏览\n")
        data["专利"] = paten
        return data


    @staticmethod
    def save(content_list):
        with open('化学学院.csv', 'a', encoding='UTF-8') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=['系', '名字', '主页地址', '电话', '邮箱',
                                                '专利', '社会兼职', '研究方向',
                                                '讲授课程', '学院', '大学', '教育经历',
                                                "个人简介", "工作经历", "职位", "论文著作"])
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

