import requests
import bs4
from bs4 import BeautifulSoup
import time
import pymongo

myclient = pymongo.MongoClient('localhost', 27017)

mydb = myclient['khanhduy1']

mycol = mydb['mycol_02']


def crawl():

    web = 'https://vnexpress.net'

    lastpage = False

    nextstep = '/giao-duc-p1260'

    while not lastpage:
        link = web + nextstep

        # noinspection PyBroadException
        try:
            response = requests.get(link, allow_redirect=False)
        except Exception:
            lastpage = True
        soup = BeautifulSoup(response.text, 'html.parser')
        find = soup.select('.next-page')
        nextstep = find[0]['href']
        print(nextstep)
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

                data = {"Name": item.get_text(), "Data": detail[0].get_text()}

                mycol.insert_one(data)


if __name__ == '__main__':
    star_time = time.time()
    crawl()
    end_time = time.time()
    print(f"Runtime of the program is {end_time- star_time}")
