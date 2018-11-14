# -*- coding:utf-8 -*-
import requests,json
from bs4 import BeautifulSoup
from data import conn_mysql

from xlwt import *

def start():
    url = 'http://env.nankai.edu.cn/shiziduiwu/fujiaoshou/'

    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    li_list = soup.find('ul',class_='teacherList').find_all('li')
    # file = Workbook(encoding='utf-8')
    # table = file.add_sheet('b3')
    for i,li in enumerate(li_list):
        name = li.text.strip()
        detail_url = 'http://env.nankai.edu.cn' + li.find('a')['href']
        print(i,name, detail_url)
        # try:
        #     detail_info(name, detail_url,i,table)
        # except:
        #     pass

    # file.save('b3' + '.xlsx')
        # break

def detail_info(name,url,i,table):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    detail_url = 'http://env.nankai.edu.cn' + soup.find('div').text
    res1 = requests.get(detail_url)
    soup1 = BeautifulSoup(res1.content, 'lxml')
    fck_list = soup1.find_all('div',class_='fck')
    resume = ''
    education_resume = fck_list[1].text.strip()
    society_position = fck_list[2].text.strip()
    research_project = fck_list[3].text.strip()
    thesis = fck_list[4].text.strip()
    # print(education_resume)
    # print(society_position)
    # print(research_project)
    # print(thesis)
    university = '南开大学'
    college = '环境科学与工程学院'
    faculty = ''
    arr = [name,university,college,education_resume,society_position,research_project,thesis]
    table.write(i, 0, arr[0])
    table.write(i, 1, arr[1])
    table.write(i, 2, arr[2])
    table.write(i, 3, arr[3])
    table.write(i, 4, arr[4])
    table.write(i, 5, arr[5])
    table.write(i, 6, arr[6])
    print(arr)
    # save_excel(i,arr,'aa')
    # conn = conn_mysql.MysqlUtil()
    #
    # insert_sql = "insert into tearchers (name,university,college,education_resume,society_position,research_project,thesis) values (%s,%s,%s,%s,%s,%s,%s)"
    # values = (name,university,college,education_resume,society_position,research_project,thesis)
    # insert_result = conn.insert_one(insert_sql, values)
    # print(insert_result)


def save_excel(i,arr,sheet_name):
    file = Workbook(encoding='utf-8')
    table = file.add_sheet(sheet_name)
    table.write(i,0,arr[0])
    table.write(i, 1, arr[1])
    table.write(i, 2, arr[2])
    table.write(i, 3, arr[3])
    table.write(i, 4, arr[4])
    table.write(i, 5, arr[5])
    table.write(i, 6, arr[6])


    file.save(sheet_name + '.xlsx')

start()
# save_excel()