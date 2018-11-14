# -*- coding:utf-8 -*-
import requests,json
from bs4 import BeautifulSoup
from data import conn_mysql
from xlwt import *

def start():
    url = 'http://sky.nankai.edu.cn/_wp3services/generalQuery?queryObj=teacherHome'
    form_data = {
        'siteId': '126',
        'pageIndex': '1',
        'conditions': '[{"orConditions": [{"field": "exField1", "value": "讲师", "judge": "="},{"field": "exField1", '
                      '"value": "助理研究员", "judge": "="}]},{"field": "published", "value": 1, "judge": "="}]',
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
    file = Workbook(encoding='utf-8')
    table = file.add_sheet('e2')
    total = p_text['total']
    for i in range(total):
        name = p_text['data'][i]['title']
        job = p_text['data'][i]['exField1']
        cnUrl = p_text['data'][i]['cnUrl']
        detail_info(name,job,cnUrl,i,table)
        # print (name,job,cnUrl)
        # break
    file.save('e2' + '.xlsx')

def detail_info(name,job,url,i,table):
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
        society_position = None
    try:
        thesis = div_list[6].find('div', class_='con').find_all('p')[2].text.strip().replace('研究成果: ','')
    except IndexError:
        thesis = None
    university = '南开大学'
    college = '生命科学学院'
    faculty = ''
    arr = [name,university,college,job,email,phone,resume,education_resume,society_position,research_direction,thesis]
    table.write(i, 0, arr[0])
    table.write(i, 1, arr[1])
    table.write(i, 2, arr[2])
    table.write(i, 3, arr[3])
    table.write(i, 4, arr[4])
    table.write(i, 5, arr[5])
    table.write(i, 6, arr[6])
    table.write(i, 7, arr[7])
    table.write(i, 8, arr[8])
    table.write(i, 9, arr[9])
    table.write(i, 10, arr[10])
    print(email)
    # conn = conn_mysql.MysqlUtil()
    # # sql =
    # # conn.get_one()
    # insert_sql = "insert into tearchers (name,university,college,job,email,phone,resume," \
    #              "education_resume,society_position,research_direction,thesis) " \
    #              "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    # values = (name,university,college,job,email,phone,resume,education_resume,society_position,research_direction,
    #           thesis)
    # # insert_result = conn.insert_one(insert_sql, values)
    # # print(insert_result)

    print(phone, email)
    print(education_resume)
    print(resume)
    print(research_direction)
    print(society_position)
    print(thesis)



start()