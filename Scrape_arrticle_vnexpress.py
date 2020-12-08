import time
from multiprocessing import Pool
import multiprocessing
import bs4
import pymongo
import requests
from bs4 import BeautifulSoup

myclient = pymongo.MongoClient('localhost', 27017)
mydb = myclient['vnexpress_giao_duc']
mycol = mydb['vnexpress_aritcle']


def get_link(queue_links):
    """
    Crawl links and put to queue
    :param queue_links:
    :return:
    """
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
                queue_links.put(item['href'])

    queue_links.put('last_page')


def get_article_content(queue_links):
    """
    Get article content
    :link:
    :return:
    """
    while True:
        try:
            link = queue_links.get(block=True, timeout=2)
            if link == 'last_page':
                break
        except Exception:
            print('continue after queue block')
            continue

        # crawl data
        print(link)
        response1 = requests.get(link)
        soup1 = BeautifulSoup(response1.text, 'html.parser')
        detail = soup1.select('.title-detail')  # scarped title of the news
        response2 = requests.get(link)
        soup2 = BeautifulSoup(response2.text, 'html.parser')
        detail1 = soup2.select('.fck_detail')  # scarped data in each link
        if len(detail) == 0:
            continue
        if len(detail1) == 0:
            continue

        # print(detail1[0].get_text())
        data = {
            "Name": detail[0].get_text(),
            "Data": detail1[0].get_text()
        }
        print(data)
        # save in mongodb
        mycol.insert_one(data)


if __name__ == '__main__':
    start_time = time.time()

    # crawl links
    m = multiprocessing.Manager()
    queue_link = m.Queue()
    pool_getlinks = Pool(processes=1)
    pool_getlinks.apply_async(get_link, (queue_link,))

    # crawl article content
    pool_getarticle = Pool(processes=3)
    pool_getarticle.apply_async(get_article_content, (queue_link,))

    pool_getlinks.close()
    pool_getlinks.join()

    pool_getarticle.close()
    pool_getarticle.join()

    end_time = time.time()
    print(end_time - start_time)
