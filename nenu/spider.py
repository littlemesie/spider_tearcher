import requests
from lxml import etree
import csv


class Spider(object):
    """东北师范大学-环境学院"""
    def __init__(self):
        self.title = None

    @staticmethod
    def downloader(url):
        response = requests.get(url=url)
        return response.content.decode()

    def parse(self, content):
        content_list = []
        html = etree.HTML(content)
        p_list = html.xpath('//div[@id="vsb_content"]/p')
        for each in p_list:
            title = each.xpath('.//span//text()')
            if title:
                # 职称
                self.title = title[0].replace('\u3000', '')
            else:
                name_list = each.xpath('./a')
                for a in name_list:
                    # 姓名
                    name = a.xpath('./text()')[0].replace('\u3000', '')
                    # 主页地址
                    link = a.xpath('./@href')
                    if link:
                        link = link[0]
                    if link.startswith('..'):
                        link = link.replace('..', 'http://hjxy.nenu.edu.cn')
                    item = {
                        '职称': self.title,
                        '名字': name,
                        '主页地址': link
                    }
                    content_list.append(item)
        return content_list

    @staticmethod
    def parse_detail(detail_content):
        detail_html = etree.HTML(detail_content)
        # 电话
        phone = detail_html.xpath('//p[contains(text(), "电话")]/text()')
        if phone:
            phone = phone[0].replace('电话：', '')
        # 邮箱
        email = detail_html.xpath('//p[contains(text(), "邮箱")]/text()')
        if email:
            email = email[0].replace('邮箱：', '')

        num = 1
        # 教育和工作经历
        edu_and_job_all = ''
        while True:
            edu_and_job = detail_html.xpath(f'//strong[contains(text(), "教育与工作经历")]/../../following-sibling::p[{num}]/text()')
            if edu_and_job:
                edu_and_job_all = edu_and_job_all + edu_and_job[0] + '\n'
                num += 1
            else:
                num = 1
                break
        # 主要学术兼职
        academic_job_all = ''
        while True:
            academic_job = detail_html.xpath(f'//strong[contains(text(), "主要学术兼职")]/../../following-sibling::p[{num}]/text()')
            if academic_job:
                academic_job_all = academic_job_all + academic_job[0] + '\n'
                num += 1
            else:
                num = 1
                break
        # 研究领域和兴趣
        interest_area_all = ''
        while True:
            interest_area = detail_html.xpath(
                f'//strong[contains(text(), "研究领域与兴趣")]/../../following-sibling::p[{num}]/text()')
            if interest_area:
                interest_area_all = interest_area_all + interest_area[0] + '\n'
                num += 1
            else:
                num = 1
                break
        # 讲授课程
        course_all = ''
        while True:
            course = detail_html.xpath(f'//strong[contains(text(), "讲授课程")]/../../following-sibling::p[{num}]/text()')
            if course:
                course_all = course_all + course[0] + '\n'
                num += 1
            else:
                break
        item = {
            '电话': phone,
            '邮箱': email,
            '教育和工作经历': edu_and_job_all,
            '主要学术兼职': academic_job_all,
            '研究领域和兴趣': interest_area_all,
            '讲授课程': course_all
        }
        return item

    @staticmethod
    def save(content_list):
        with open('东北师范大学_环境学院.csv', 'a', encoding='UTF-8') as f:
            writer = csv.DictWriter(f, fieldnames=['职称', '名字', '主页地址', '电话', '邮箱', '教育和工作经历', '主要学术兼职', '研究领域和兴趣', '讲授课程'])
            writer.writeheader()
            for content in content_list:
                writer.writerow(content)

    def run(self):
        url = 'http://hjxy.nenu.edu.cn/szdw/zrjs.htm'
        content = self.downloader(url=url)
        content_list = self.parse(content)
        for content in content_list:
            detail_content = self.downloader(url=content['主页地址'])
            item = self.parse_detail(detail_content)
            content.update(item)
        self.save(content_list)
        print('保存成功')


if __name__ == '__main__':
    neau = Spider()
    neau.run()
