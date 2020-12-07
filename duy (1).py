import time
from multiprocessing import Pool
import multiprocessing
import bs4
import pymongo
import requests
from bs4 import BeautifulSoup

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['khanhduy2']
mycol = mydb['mycol_01']


def get_link(qu):
    response = None
    url = 'https://vnexpress.net'
    last_page = False
    query_param = '/giao-duc'

    while not last_page:
        link = url + query_param
        print(link)

        try:
            response = requests.get(link)               # get link and identification the last_page from the web
            if response.status_code == 302:
                break
        except Exception:
            last_page = True

        soup = BeautifulSoup(response.text, 'html.parser')
        find = soup.select('.next-page')
        query_param = find[0]['href']
        title = soup.select('.title-news > a')           # scarped the title of the link
        for item in title:
            if type(item) is not bs4.element.NavigableString:
                qu.put(item['href'])
    qu.put('last_page')


def page(link):
    print(link)
    response1 = requests.get(link)
    soup1 = BeautifulSoup(response1.text, 'html.parser')
    detail = soup1.select('.title-detail')  # scarped title of the news
    response2 = requests.get(link)
    soup2 = BeautifulSoup(response2.text, 'html.parser')
    detail1 = soup2.select('.fck_detail')  # scarped data in each link
    if len(detail1) == 0:
        return
    print(detail1[0].get_text())
    qu1.put(detail1[0])
    data = {
        "Name": detail.get_text(),
        "Data": detail1[0].get_text()
    }
    # save in mongodb
    mycol.insert_one(data)


if __name__ == '__main__':
    m = multiprocessing.Manager()
    qu = m.Queue()
    qu1 = m.Queue()
    star_time = time.time()
    pool = Pool(1)
    last_page = False
    pool.apply_async(get_link, (qu,))

    while not last_page and not qu.empty():
        link = qu.get()
        if link == 'last_page':
            if not qu.empty():
                qu.put('last_page')
            else:
                last_page = True
            break
    pool1 = Pool(4)
    pool1.apply_async(page, (qu1,))
    pool.close()
    pool.join()
    pool1.close()
    pool1.join()
    end_time = time.time()
    print(end_time - star_time)
