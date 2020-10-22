import requests
import bs4
from bs4 import BeautifulSoup
import pymongo
import time

myclient = pymongo.MongoClient('localhost', 27017)

mydb = myclient['scarpe_data']

mycol = mydb['save_data']


def crawl():

    web = 'https://vnexpress.net'

    lastpage = False

    nextpage = '/giao-duc'

    while not lastpage:
        link = web + nextpage
        try:
            response = requests.get(link)
            print(response)
            if response.status_code == 404:
                break
        except Exception:
            lastpage = True
        soup = BeautifulSoup(response.text, 'html.parser')
        find = soup.select('.next-page')
        next_page = find[0]['href']
        print(next_page)
        title = soup.select('.title-news > a')
        for item in title:
            print(item['href'])
            if type(item) is not bs4.element.NavigableString:
                print(item.get_text())

            response1 = requests.get(item['href'])
            soup1 = BeautifulSoup(response1.text, 'html.parser')
            detail = soup1.select('.fck_detail')
            if len(detail) == 0:
                continue
            print(detail[0].get_text())

            print(response1)
            if response1.status_code == 404:
                break

            data = {"Source": next_page, "Name": item.get_text(), "Data": detail[0].get_text()}

            mycol.insert_one(data)


if __name__ == '__main__':
    star_time = time.time()
    crawl()
    end_time = time.time()
    print(f"Runtime of the program is {end_time- star_time}")
