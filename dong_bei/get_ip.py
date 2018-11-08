# -*- coding:utf-8 -*-
# Date   : Mon Nov 05 17:42:05 2018 +0800
# Author : Rory Xiang
import requests


def get_ip_from_url():
    url = "http://116.196.118.3:1312/getIp"
    while True:
        try:
            res = requests.get(url, timeout=2)
            break
        except:
            pass
    print("ip_port: ", res.content.decode())
    return res.content.decode()