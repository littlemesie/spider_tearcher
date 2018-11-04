# -*- coding:utf-8 -*-
import requests,json
from bs4 import BeautifulSoup

def start():
    url = 'http://sky.nankai.edu.cn/_wp3services/generalQuery?queryObj=teacherHome'
    form_data = {
        'siteId': '126',
        'pageIndex': '1',
        'conditions': '[{"orConditions": [{"field": "exField1", "value": "教授", "judge": "="},{"field": "exField1", '
                      '"value": "研究员", "judge": "="}]},{"field": "published", "value": 1, "judge": "="}]',
        'orders': '[{"field": "letter", "type": "asc"}]',
        'returnInfos': '[{"field": "title", "name": "title"}, {"field": "exField1", "name": "exField1"},'
                      '{"field": "exField2", "name": "exField2"}, {"field": "exField3", "name": "exField3"},'
                      '{"field": "exField4", "name": "exField4"}, {"field": "email", "name": "email"},'
                      '{"field": "phone", "name": "phone"}, {"field": "exField5", "name": "exField5"},'
                      '{"field": "exField6", "name": "exField6"}, {"field": "exField7", "name": "exField7"},'
                      '{"field": "headerPic", "name": "headerPic"}, {"field": "cnUrl", "name": "cnUrl"}]',
        'articleType': '1',
        'level': '1',
    }
    res = requests.post(url,data=form_data)
    soup = BeautifulSoup(res.text, 'lxml')
    p_text = json.loads(soup.find('p').text)
    total = p_text['total']
    for i in range(total):
        name = p_text['data'][i]['title']
        job = p_text['data'][i]['exField1']
        cnUrl = p_text['data'][i]['cnUrl']
        detail_info(name,job,cnUrl)
        print (name,job,cnUrl)
        # break

def detail_info(name,job,url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    phone = soup.find('div',class_='jj').find_all('div',class_='news_list')[0].find_all('p',class_='news_text')[1].text.strip().replace('电话：  ','')
    email = soup.find('div',class_='jj').find_all('div',class_='news_list')[1].find_all('p',class_='news_text')[0].text.strip().replace('邮箱：  ','')
    div_list = soup.find_all('div',class_='maincon')
    education_resume = div_list[0].find_all('div', class_='post')[1].find('div', class_='con').text.strip()
    resume = div_list[0].find_all('div', class_='post')[2].find('div', class_='con').text.strip()
    research_direction = div_list[2].find('div', class_='con').text.strip()
    try:
        society_position = div_list[4].find('div', class_='con').text.strip()
    except IndexError:
        society_position = ''
    try:
        thesis = div_list[6].find('div', class_='con').find_all('p')[2].text.strip().replace('研究成果: ','')
    except IndexError:
        thesis = ''
    print (phone,email)
    print (education_resume)
    print (resume)
    print (research_direction)
    print (society_position)
    print (thesis)

start()