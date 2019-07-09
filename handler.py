import requests
from bs4 import BeautifulSoup
from houses import get_materials
from table import csv_dict_writer


def handle_url(url, index):
    # POST запрос для сбора ссылок на все дома
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

        houses_links = []
        print(len(a['rows']))
        for j in range(index,len(a['rows'])+1):
            houses_links.append(a['rows'][j]['url'])

        row_index = index

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

