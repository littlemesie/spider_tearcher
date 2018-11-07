import requests
from lxml import etree
import time
import csv
import os


class Spider(object):
    """东北农业大学-园林学院"""
    def __init__(self):
        pass

    @staticmethod
    def downloader(url):
        response = requests.get(url=url)
        return response.content.decode()

    def parse(self, content):
        html = etree.HTML(content)
        li_list = html.xpath('//li[@class="line_green"]')
        content_list = []
        for li in li_list:
            cate = li.xpath('./a/text()')[0]
            cate_link = "http://yyxy.neau.edu.cn/szdw/" + li.xpath('./a/@href')[0]
            print(cate, cate_link)
            item = {
                '分类': cate,
                '分类地址': cate_link
            }
            content_list.append(item)
        return content_list

    @staticmethod
    def parse_cate(content, each):
        html = etree.HTML(content)
        tr_list = html.xpath('//div[@id="vsb_content"]//tr')
        content_list = []
        for tr in tr_list[1:]:
            duty = tr.xpath('./td//text()')[0]
            name = tr.xpath('./td//text()')[1]
            detail_url = tr.xpath('./td/a/@href')
            if detail_url:
                detail_url = detail_url[0]
                if detail_url.startswith('..'):
                    detail_url = detail_url.replace('..', 'http://yyxy.neau.edu.cn')
            else:
                detail_url = ''
            remark = tr.xpath('./td//text()')[2].strip()
            item = {
                '分类': each['分类'],  # 分类
                '分类地址': each['分类地址'],  # 分类地址
                '职称': duty,  # 职称
                '姓名': name,  # 姓名
                '个人主页': detail_url,  # 个人主页
                '备注': remark  # 备注
            }
            content_list.append(item)
        return content_list

    @staticmethod
    def parse_detail(content):
        html = etree.HTML(content)
        p_list = html.xpath("//div[@class='mt30']/p")
        introduction_all = ''
        for p in p_list:
            introduction = p.xpath('.//text()')
            if introduction:
                introduction = introduction[0]
                if '一、个人简历' not in introduction:
                    introduction_all = introduction_all + introduction
                else:
                    break

        num = 1
        resume_all = ''
        while True:
            resume = html.xpath(
                f'//strong[contains(text(), "一、个人简历")]/../following-sibling::p[{num}]//text()')
            if resume:
                if '二、社会兼职：' not in resume[0]:
                    if isinstance(resume, list):
                        resume_all = resume_all + ''.join(resume) + '\n'
                    else:
                        resume_all = resume_all + resume[0] + '\n'
                    num += 1
                else:
                    break

        num = 1
        social_appointments_all = ''
        while True:
            social_appointments = html.xpath(
                f'//strong[contains(text(), "二、社会兼职：")]/../following-sibling::p[{num}]//text()')
            if social_appointments:
                if '三、教学工作：' not in social_appointments[0]:
                    if isinstance(social_appointments, list):
                        social_appointments_all = social_appointments_all + ''.join(social_appointments) + '\n'
                    else:
                        social_appointments_all = social_appointments_all + social_appointments[0] + '\n'
                    num += 1
                else:
                    break

        num = 1
        teaching_work_all = ''
        while True:
            teaching_work = html.xpath(
                f'//strong[contains(text(), "三、教学工作：")]/../following-sibling::p[{num}]//text()')
            if teaching_work:
                if '四、科研与成果' not in teaching_work[0]:
                    if isinstance(social_appointments, list):
                        teaching_work_all = teaching_work_all + ''.join(teaching_work) + '\n'
                    else:
                        teaching_work_all = teaching_work_all + teaching_work[0] + '\n'
                    num += 1
                else:
                    break

        num = 1
        research_achievements_all = ''
        while True:
            research_achievements = html.xpath(
                f'//strong[contains(text(), "四、科研与成果")]/../following-sibling::p[{num}]//text()')
            if research_achievements:
                if '科研奖励' not in research_achievements[0]:
                    if isinstance(research_achievements, list):
                        research_achievements_all = research_achievements_all + ''.join(research_achievements) + '\n'
                    else:
                        research_achievements_all = research_achievements_all + research_achievements[0] + '\n'
                    num += 1
                else:
                    break

        num = 1
        research_award_all = ''
        while True:
            research_award = html.xpath(
                f'//strong[contains(text(), "科研奖励")]/../following-sibling::p[{num}]//text()')
            if research_award:
                    if isinstance(research_award, list):
                        research_award_all = research_award_all + ''.join(research_award) + '\n'
                    else:
                        research_award_all = research_award_all + research_award[0] + '\n'
                    num += 1
            else:
                break

        item = {
            'introduction': introduction_all,
            'resume': resume_all,
            'social_appointments': social_appointments_all,
            'teaching_work': teaching_work_all,
            'research_achievements': research_achievements_all,
            'research_award': research_award_all,
        }
        return item

    @staticmethod
    def save(content_list):
        with open('东北农业大学_园林学院.csv', 'a', encoding='UTF-8') as f:
            writer = csv.DictWriter(f, fieldnames=['分类', '分类地址', '职称', '姓名', '个人主页', '备注'])
            if not os.path.getsize('东北农业大学_园林学院.csv'):
                writer.writeheader()
            for content in content_list:
                writer.writerow(content)

    def run(self):
        url = 'http://yyxy.neau.edu.cn/szdw/xyld.htm'
        index_content = self.downloader(url=url)
        index_list = self.parse(index_content)
        for each in index_list:
            content = self.downloader(each['分类地址'])
            content_list = self.parse_cate(content, each)
            for content in content_list:
                if content['分类'] == '分类':
                    continue
                # 个人主页解析 待定
                # if content['detail_url']:
                #     detail_content = self.downloader(content['detail_url'])
                #     item = self.parse_detail(detail_content)
                #     content.update(item)
                print(content)
                time.sleep(2)
            self.save(content_list)


if __name__ == '__main__':
    neau = Spider()
    neau.run()