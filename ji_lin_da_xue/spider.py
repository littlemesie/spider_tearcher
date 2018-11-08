import requests
from lxml import etree
import csv
from queue import Queue
import gevent 
from gevent import monkey
monkey.patch_all()

base_url = "http://chem.jlu.edu.cn/szll/js2.htm"

headers = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	"Accept-Encoding": "gzip, deflate",
	"Accept-Language": "zh-CN,zh;q=0.9",
	"Cache-Control": "max-age=0",
	"Connection": "keep-alive",
	"Cookie": "JSESSIONID=8A42A0A032FC3352786E61FC75B8B628",
	"Host": "chem.jlu.edu.cn",
	"If-Modified-Since": "Mon, 05 Nov 2018 02:14:04 GMT",
	"If-None-Match": "44ed-579e1706a019a-gzip",
	"Upgrade-Insecure-Requests": "1",
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
	}

class  JiLingSpider(object):
	"""docstring for  JiLingSpider"""
	def __init__(self,):
		self.base_info = self.downloader(base_url)
		self.q = Queue()
		pass

	def downloader(self, url):
		info = requests.get(url, headers=headers)
		return info.content.decode()

	def get_detail_url(self):
		base_html = etree.HTML(self.base_info)
		teachers = base_html.xpath('//div[@class="teacher"]/ul/li')
		print(len(teachers), teachers)
		for one in teachers:
			title = one.xpath('./text()')[-1]
			url = one.xpath('./a/@href')[0]
			name = one.xpath('./a/text()')[0]
			data = {
				"title": title,
				"name": name,
				"url": url
			}
			self.q.put(data)
			print(title, name, url)
		next_page_url_ = base_html.xpath('//a[contains(text(), "下页")]/@href')
		print("???????: ", next_page_url_	)
		if next_page_url_:
			if "js2" in next_page_url_[0]:
				next_page_url = "http://chem.jlu.edu.cn/szll/" + next_page_url_[0]
			else:
				next_page_url = "http://chem.jlu.edu.cn/szll/js2/" + next_page_url_[0]
			self.base_info = self.downloader(next_page_url)
			self.get_detail_url()


	def get_detail_info(self):
		data = self.q.get()
		url = data["url"]
		detail_info = self.downloader(url)
		detail_tree = etree.HTML(detail_info)
		# email
		email = detail_tree.xpath('')

	def run(self):
		gevent.joinall([
			gevent.spawn(self.get_detail_url), 
			gevent.spawn(self.get_detail_info)
			])


a = JiLingSpider()
a.run()

