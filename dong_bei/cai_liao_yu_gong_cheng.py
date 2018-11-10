# -*- coding:utf-8 -*-
# Date   : Mon Nov 05 17:42:05 2018 +0800
# Author : Rory Xiang

import requests
from dong_bei.conf import base_url, headers
from lxml import etree
from copy import deepcopy
import re, time
import csv
from queue import Queue
from gevent import monkey
import gevent
monkey.patch_all()

phonerex = r"(86)?(1[345789]\d{9})|\d{2,5}-\d{5,10}"


class TeacherSpider(object):

    def __init__(self):
        self.q = Queue()

    def get_teacher_list(self):
        teachers_res = requests.get(base_url, headers=headers)
        teachers_tree = etree.HTML(teachers_res.content.decode())
        faculties = teachers_tree.xpath('//div[@id="department"]/div['
                                        '@class="fellows"]')
        for one in faculties:
            facuty = one.xpath('./div[@class="fellows-title"]/text()')[0]
            data = {
                "系": facuty,
                "大学": "东北大学",
                "学院": "材料科学与工程学院"
            }
            detail_urls_ = one.xpath('.//a/@href')
            detail_urls = list(map(
                lambda x: "http://www.mse.neu.edu.cn"+x, detail_urls_
            ))
            for url in detail_urls:
                one_data = deepcopy(data)
                one_data["主页地址"] = url
                self.q.put(one_data)

    def get_detail_info(self):
        teacher_infos = []
        time.sleep(2)
        while True:
            if self.q.empty():
                break
            data = self.q.get()
            url = data["主页地址"]
            detail_res = requests.get(url, headers=headers)
            if detail_res.status_code == 404:
                teacher_infos.append(data)
                continue
            detail_tree = etree.HTML(detail_res.content.decode(errors="ignore"))

            infos = detail_tree.xpath('//div[@class="article"]//text()')
            infos = list(map(
                lambda x: x.replace(
                    "\r", "").replace("\n", "").replace(
                    "\xa0", "").strip(),
                infos
            ))
            info = "".join(infos)
            data = self.extract_info_by_re(info, deepcopy(data))
            teacher_infos.append(data)
        self.save(teacher_infos)

    def extract_info_by_re(self, info, data):

        # 教育经历
        educations = r'(学习简历)[\s\S]+?(工作简历)'
        education = re.search(educations, info)
        if education:
            educations = education.group().replace(
                "。", "。\n").replace("学习简历", "").replace("工作简历", "").strip()[:-2]
        else:
            educations = ""
        data["教育经历"] = educations

        # 工作经历
        works = r'(工作简历)[\s\S]+?(学术兼职)'
        work = re.search(works, info)
        if work:
            work = work.group().replace(
                "。", "。\n").replace("工作简历", "").replace("学术兼职", "").strip()[:-2]
        else:
            work = ""
        data["工作经历"] = work

        # 社会兼职
        society_positions = r'(学术兼职)[\s\S]+?(研究方向)'
        society_position = re.search(society_positions, info)
        if society_position:
            society_position = society_position.group().replace(
                "。", "。\n").replace("学术兼职", "").replace("研究方向", "").strip()[:-2]
        else:
            society_position = ""
        data["社会兼职"] = society_position

        # 研究方向
        research_directions = r'(研究方向)[\s\S]+?(近年来承担的科研项目)'
        research_direction = re.search(research_directions, info)
        if research_direction:
            research_direction = research_direction.group().replace(
                "。", "。\n").replace("研究方向", "").replace("近年来承担的科研项目", "").strip()[:-2]
        else:
            research_direction = ""
        data["研究方向"] = research_direction

        # 科研项目
        research_projects = r'(科研项目)[\s\S]+?(获奖及荣誉)'
        research_project = re.search(research_projects, info)
        if research_project:
            research_project = research_project.group().replace(
                "。", "。\n").replace("科研项目", "").replace("获奖及荣誉", "").strip()[:-2]
        else:
            research_project = ""
        data["科研项目"] = research_project

        # 学术论文与专利
        paperre = r'学术论文与专利[\s\S]+'
        paper = re.search(paperre, info)
        if paper:
            paper = paper.group()[:-2].replace(
                "（", "\n（").replace("学术论文与专利", "").strip()
            if "代表性专利" in paper or "发明专利" in paper:
                paper_ = re.search(
                    r'(代表性论文有：)[\s\S]+?(代表性专利|发明专利)',
                    paper)
                if paper_:
                    paper_ = paper_.group().replace("代表性论文有：", "")
                else:
                    paper_ = ""
                paper_ = re.sub("(代表性专利|发明专利)", "", paper_)
                try:
                    patent = re.search(
                        r'专利：[\s\S]+', paper).group()
                    patent = re.sub('(专利：)', '', patent)
                except:
                    patent = ""
                data["论文著作"] = paper_
                data["专利"] = patent
            else:
                data["论文著作"] = paper
                data["专利"] = ""

        connectre = r"[\s\S]+?(学习简历)"
        connections = re.search(connectre, info)
        if connections:
            connection = connections.group()
            phone = re.search(phonerex, connection)
            phone = phone.group() if phone else ""
            data["电话"] = phone if len(phone) > 5 else ""

            emailregex = r"[-_\w\.]{0,64}@([-\w]{1,63}\.)*[-A-Za-z0-9]{1,63}"
            email = re.search(emailregex, connection)
            data["邮箱"] = email.group() if email else ""
        else:
            data["电话"] = ""
            data["邮箱"] = ""
        return data

    @staticmethod
    def save(content_list):
        with open('东北大学_材料科学与工程学院.csv', 'a', encoding='UTF-8') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=['系', '名字', '主页地址', '电话', '邮箱',
                                                '专利', '社会兼职', '研究方向',
                                                '科研项目', '学院', '大学', '教育经历',
                                                "个人简介", "工作经历", "职位", "论文著作"])
            writer.writeheader()
            for content in content_list:
                writer.writerow(content)

    def run(self):
        gevent.joinall([
            gevent.spawn(self.get_teacher_list),
            gevent.spawn(self.get_detail_info)
        ])


if __name__ == '__main__':
    a = TeacherSpider()
    a.run()