# -*- coding:utf-8 -*-
# Date   : Mon Nov 05 17:42:05 2018 +0800
# Author : Rory Xiang

import requests
from dong_bei.conf import base_url, headers
from dong_bei.mysql_api import local_cursor
from dong_bei.get_ip import get_ip_from_url
from lxml import etree
from copy import deepcopy


class TeacherSpider(object):

    def __init__(self):
        self.ip_port = get_ip_from_url()
        self.proxies = {
            "http": f"http://{self.ip_port}",
            "https": f"https://{self.ip_port}"
        }

    def get_teacher_list(self):
        print(base_url)
        while True:
            try:
                teachers_res = requests.get(base_url, headers=headers,
                                            proxies=self.proxies, timeout=2)
                if "The requested URL could not be retrieved" in \
                        teachers_res.text:
                    raise requests.exceptions.ProxyError
                break
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ProxyError):
                self.change_ip()
        teachers_tree = etree.HTML(teachers_res.content.decode())
        # print(teachers_res.text)

        faculties = teachers_tree.xpath('//div[@id="department"]/div['
                                        '@class="fellows"]')
        print("---->", faculties)
        for one in faculties:
            facuty = one.xpath('./div[@class="fellows-title"]/text()')[0]
            data = {
                "facuty": facuty,
                "university": "东北大学",
                "college": "材料科学与工程学院"
            }
            detail_urls_ = one.xpath('.//a/@href')
            detail_urls = list(map(
                lambda x: "http://www.mse.neu.edu.cn"+x, detail_urls_
            ))
            print(detail_urls)
            for url in detail_urls:
                one_data = deepcopy(data)
                one_data["url"] = url
                self.get_detail_info(one_data)

    def change_ip(self):
        self.ip_port = get_ip_from_url()
        self.proxies = {
            "http": f"http://{self.ip_port}",
            "https": f"https://{self.ip_port}"
        }

    def get_detail_info(self, data):
        url = data["url"]
        while True:
            try:
                detail_res = requests.get(url, headers=headers,
                                            proxies=self.proxies, timeout=2)
                if "The requested URL could not be retrieved" in \
                        detail_res.text:
                    raise requests.exceptions.ProxyError
                break
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ProxyError):
                self.change_ip()
            except requests.exceptions.ReadTimeout:
                pass
        if detail_res.status_code == 404:
            return
        try:
            detail_tree = etree.HTML(detail_res.content.decode(errors="ignore"))
        except:
            detail_tree = etree.parse(detail_res.content.decode(errors="ignore"))


        # infos = detail_tree.xpath(
        #     '//div[@class="article"]/p/text()|//div['
        #     '@class="article"]/p/span/text()|//div[@class="article"]/h2/text('
        #     ')|//div[@class="article"]/div/span/text()|//div['
        #     '@class="article"]//div/span/strong/text()|//div['
        #     '@class="article"]//a/text()|//div['
        #     '@class="article"]//strong/text()')

        infos = detail_tree.xpath('//div[@class="article"]//text()')
        infos = list(map(
            lambda x: x.replace(
                "\r", "").replace("\n", "").replace(
                "\xa0", "").strip(),
            infos
        ))
        # print(infos)
        info = "".join(infos)
        print(info)
        name_job = info.split("名：")[-1].split("性")[0]
        data["name"] = name_job.split(" ")[0]
        data["job"] = name_job.split(" ")[-1]
        data["email"] = info.split("Email：")[-1].split("1.学习简历")[0]
        data["phone"] = info.split("电话：")[-1].split("Email")[0]
        data["resume"] = info.split("工作简历")[-1].split("3．学术兼职")[0]
        data["education_resume"] = info.split("学习简历")[-1].split("2.工作简历")[0]
        data["society_position"] = info.split("学术兼职")[-1].split("4．研究方向")[0]
        data["research_direction"] = info.split("研究方向")[-1].split("5．近年来承担的科研项目")[0]
        data["research_areas"] = ""
        data["research_project"] = info.split("来承担的科研项目")[-1].split("6. 获奖及荣誉")[0]

        thesis_paten = info.split("学术论文与专利")[-1]
        if len(thesis_paten) < 5:
            data["thesis"] = "无"
            data["patent"] = "无"
        else:
            data["thesis"] = thesis_paten.split("代表性论文有：")[-1].split("代表性专利")[0]
            data["patent"] = "无"
            if "代表性专利" in thesis_paten:
                data["patent"] = thesis_paten.split("代表性专利")[-1]
        print(data)

if __name__ == '__main__':
    a = TeacherSpider()
    a.get_teacher_list()