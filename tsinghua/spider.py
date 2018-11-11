# -*- coding: utf-8 -*-

# @Time: 2018/11/11
# @Author: W.R.lin

import requests
from lxml import etree
import time
import csv
import os


class Spider(object):
    """清华大学环境学院"""
    def __init__(self):
        self.institute = ''
        self.host = 'http://www.tsinghua.edu.cn'

    def downloader(self, url):
        response = requests.get(url=url)
        return response.content.decode()

    def parse(self, response):
        html = etree.HTML(response)
        p_list = html.xpath("//div[@class='box_detail']/p")
        content_list = []
        for p in p_list:
            institute = p.xpath(".//span//text()")
            if institute:
                self.institute = institute[0]
            else:
                a_list = p.xpath("./a")
                for a in a_list:
                    name = a.xpath("./text()")
                    link = a.xpath("./@href")
                    item = {
                        '姓名': name[0].replace('\xa0', ''),
                        '个人主页': self.host + link[0],
                        '研究所': self.institute.replace('\xa0', '')
                    }
                    content_list.append(item)
        return content_list

    @staticmethod
    def parse_detail(response):
        html = etree.HTML(response)
        unit = html.xpath("//strong[contains(text(), '所在单位')]/../following-sibling::td[1]/text()")
        if unit:
            unit = unit[0]
        else:
            unit = html.xpath("//td[contains(text(), '所在单位')]/following-sibling::td[1]/text()")
            if unit:
                unit = unit[0]
            else:
                unit = ''
        title = html.xpath("//strong[contains(text(), '职称')]/../following-sibling::td[1]/text()")
        if title:
            title = title[0]
        else:
            title = html.xpath("//td[contains(text(), '职称')]/following-sibling::td[1]/text()")
            if title:
                title = title[0]
            else:
                title = ''
        email = html.xpath("//strong[contains(text(), 'E-mail')]/../following-sibling::td[1]//text()")
        if email:
            email = email[0]
        else:
            email = html.xpath("//strong[contains(text(), '电子邮件')]/../following-sibling::td[1]//text()")
            if email:
                email = email[0]
            else:
                email = html.xpath("//td[contains(text(), '电子邮箱')]/following-sibling::td[1]//text()")
                if email:
                    email = email[0]
                else:
                    email = html.xpath("//td[contains(text(), '电子邮件')]/following-sibling::td[1]//text()")
                    if email:
                        email = email[0]
                    else:
                        email = ""

        phone = html.xpath("//strong[contains(text(), '办公电话')]/../following-sibling::td[1]/text()")
        if phone:
            phone = phone[0]
        else:
            phone = html.xpath("//td[contains(text(), '办公电话')]/following-sibling::td[1]/text()")
            if phone:
                phone = phone[0]
            else:
                phone = ''

        item = {
            '单位': unit,
            '职称': title,
            '电子邮件': email,
            '办公电话': phone
        }
        h4_list = html.xpath("//div[@id='s2_right_con']/h4")
        h4_content = None
        for h4 in h4_list[::-1]:
            h4_pre_content = h4_content
            h4_title = h4.xpath("./text()")
            h4_content = h4.xpath("./following-sibling::p//text()")
            item["".join(h4_title)] = "".join(h4_content)
            if h4_pre_content:
                for a in h4_pre_content:
                    if a in h4_content:
                        h4_content.remove(a)
                item["".join(h4_title)] = "\n".join(h4_content)
                h4_content = h4_pre_content + h4_content
        return item

    @staticmethod
    def save(content):
        with open('清华大学_环境学院_New.csv', 'a', encoding='UTF-8') as f:
            writer = csv.DictWriter(f, fieldnames=['姓名', '个人主页', '研究所', '单位', '职称', '电子邮件', '办公电话',
                                                   '教育背景', '工作履历', '学术兼职', '研究领域', '奖励与荣誉', '学术成果',
                                                   '研究概况', '社会兼职', ''])
            if not os.path.getsize('清华大学_环境学院_New.csv'):
                writer.writeheader()
            # for each in content.keys():
            #     if each not in writer.fieldnames:
            #         writer.fieldnames.append(each)
            #         writer.writeheader()
            if '研究概况' not in content.keys():
                content['研究概况'] = ''
            if '社会兼职' not in content.keys():
                content['社会兼职'] = ''
            writer.writerow(content)

    def run(self):
        url = 'http://www.tsinghua.edu.cn/publish/env/6331/index.html'
        response = self.downloader(url)
        content_list = self.parse(response)
        for content in content_list:
            detail_response = self.downloader(content['个人主页'])
            item = self.parse_detail(detail_response)
            content.update(item)
            time.sleep(2)
            print(content)
            self.save(content)


if __name__ == '__main__':
    tsinghua = Spider()
    tsinghua.run()