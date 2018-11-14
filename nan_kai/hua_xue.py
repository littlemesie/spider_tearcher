# -*- coding:utf-8 -*-
import requests,json
from bs4 import BeautifulSoup
from data import conn_mysql
from selenium import webdriver

def start():
    url = 'http://chem.nankai.edu.cn/ejym_wide.aspx?m=1.2&n=-1&t=3'
    driver = webdriver.PhantomJS()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    tr_list = soup.find('td',id='tbxm').find('table').find_all('tr')
    for tr in tr_list:
        name = tr.find('a').text.strip()
        detail_url = 'http://chem.nankai.edu.cn/' + tr.find('a')['href']
        print(name,detail_url)
        detail_info(name,detail_url)
  
        # break

def detail_info(name,url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    tr_list = soup.find('table',width='580').find_all('tr')
    job = tr_list[4].find_all('td')[1].text.strip()
    faculty = tr_list[5].find_all('td')[2].text.strip()
    phone = tr_list[8].find_all('td')[1].text.strip()
    email = tr_list[9].find_all('td')[1].text.strip()
    research_areas = tr_list[11].find_all('td')[1].text.strip()
    education_resume = tr_list[12].find_all('td')[1].text.strip()
    thesis = tr_list[14].find_all('td')[1].text.strip()
    # print(thesis)

    university = '南开大学'
    college = '化学学院'

    conn = conn_mysql.MysqlUtil()
    # sql =
    # conn.get_one()
    insert_sql = "insert into tearchers (name,university,college,faculty,job,email,phone,education_resume,research_areas" \
                 ",thesis) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (name,university,college,faculty,job,email,phone,education_resume,research_areas,thesis)
    insert_result = conn.insert_one(insert_sql, values)
    print(insert_result)




start()
# detail_info('蔡飞','http://chem.nankai.edu.cn/dt.aspx?n=A000301558')