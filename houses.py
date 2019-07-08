import requests
from bs4 import BeautifulSoup

# Тест сбора инфы о доме

# response = requests.get('http://dom.mingkh.ru/permskiy-kray/perm/589731')
# soup = BeautifulSoup(response.text, 'html.parser')
# urls_tag = soup.findAll('tr')


def get_materials(obj, info, constructions):
    materials = BeautifulSoup(str(obj), 'html.parser')
    try:
        about = materials.getText().split('\n')
    except IndexError:
        pass
    try:
        constructions.append(about[1].split('\n')[0])
    except IndexError:
        pass
    try:
        info.append(about[2].split('\n')[0])
    except IndexError:
        pass
