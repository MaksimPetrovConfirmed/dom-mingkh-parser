import requests, re, time, queue, threading, os.path
from bs4 import BeautifulSoup
from houses import get_materials
from table import csv_dict_writer

class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Elapsed time: {:.3f} sec".format(time.time() - self._startTime))

def get_region_urls(): # Сбор ссылок на области
    res = requests.get("http://dom.mingkh.ru/region/")
    region = BeautifulSoup(res.text, 'html.parser')
    base_links = \
        ["http://dom.mingkh.ru/", "#", "http://mingkh.ru/", "None", "/feedback", "/region/", "/city/", "/about", "/"]
    region_urls = []
    for link in region.findAll('a'):
        if not str(link.get('href')) in base_links and not re.match(r'#\w*', str(link.get('href'))):
            region_urls.append(str(link.get('href')).split('/')[1])
    print("Total {0} regions".format(len(region_urls)))
    return region_urls

def get_cities_urls(): # Сбор ссылок на города
    cities_urls = []
    for each in get_region_urls():
        res = requests.get('http://dom.mingkh.ru/{0}/'.format(each))
        cities = BeautifulSoup(res.text, 'html.parser')
        for link in cities.findAll('a'):
            if not str(link.get('href')) in base_links and \
                re.match(r'/{0}/\w*(?!year-stats)/?'.format(each), str(link.get('href'))):
                    cities_urls.append(str(link.get('href')))
    return cities_urls

def handle_url(url, index):
    data = {
        'current': '1',
        'rowCount': '-1',
        'searchPhrase': '',
        'region_url': '{0}'.format(url)
    }
    test = requests.post("http://dom.mingkh.ru/api/houses", data=data)  # header вроде как не понадобился
    print(url, test.reason)

    path = "{0}.tsv".format(url)

    try:
        a = test.json()
        i += 1

        houses_links = []
        for i in range(index,len(a['rows'])):
            houses_links.append(a['rows'][i]['url'])

        row_index = 0

        for house_link in houses_links:
            info = []
            constructions = []
            response = requests.get('http://dom.mingkh.ru{0}'.format(house_link))
            soup = BeautifulSoup(response.text, 'html.parser')
            house = soup.findAll('tr')

            info.append('{0}'.format(row_index + 1))
            info.append(a['rows'][row_index]['address'])
            constructions.append('#')
            constructions.append('Адрес')

            for block in house:
                get_materials(block, info, constructions)

            row_index += 1

            fieldnames = constructions
            my_list = []
            inner_dict = dict(zip(fieldnames, info))
            my_list.append(inner_dict)
            csv_dict_writer(path, fieldnames, my_list)

            print("Адресов собрано в {0}: {1}".format(url, row_index))
    except:
        pass



def count_lines(file):
    try:
        with open(file) as f:
            return len(f.readlines())
    except:
        return 0

with Profiler() as p:
    # засекаем время

    # POST запрос для сбора ссылок на все дома
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 YaBrowser/19.6.1.153 Yowser/2.5 Safari/537.36',
        'X-requested-with': 'XMLHttpRequest',
        'Host': 'http://dom.mingkh.ru',
        'Referer': 'http://dom.mingkh.ru/',
        'Content-Type': 'application/json; charset=utf-8; charset=UTF-8'
    }

    q = queue.Queue()
    for url in get_region_urls():
        q.put(url)

    def worker(url_queue):
        i = 0  # проверил, сколько регионов проходит
        while url_queue:
            url = url_queue.get(False);
            if not os.path.exists('{0}.tsv'.format(url)):
                handle_url(url,0)
            elif os.path.exists('{0}.tsv'.format(url)):
                data = {
                    'current': '1',
                    'rowCount': '-1',
                    'searchPhrase': '',
                    'region_url': '{0}'.format(url)
                }
                test = requests.post("http://dom.mingkh.ru/api/houses", data=data)
                if len(test.json()['rows']) != count_lines('{0}'.format(url))/2:
                    handle_url(url, count_lines('{0}'.format(url))/2)

        print(i, " out of {0} regions are successfully checked".format(len(region_urls)))

    thread_count = 3
    for i in range(thread_count):
        t = threading.Thread(target=worker, args=(q,))
        t.start()