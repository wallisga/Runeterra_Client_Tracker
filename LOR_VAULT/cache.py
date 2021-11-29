import os
import subprocess
import json

class DictToClass(object):
    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])

    def add(self, data):
        for key in data:
            setattr(self, key, data[key])

def check_cache(folder): 
    return os.path.abspath(os.getenv('LOCALAPPDATA')+folder)

def get_username():
    lor_dir = os.path.abspath(check_cache('\\Riot Games\\Legends of Runeterra\\Logs'))
    with open(lor_dir+'\\'+os.listdir(lor_dir)[-1], 'r') as f:
        content = f.readlines()
    for line in content:
        if line.find('alias (gamename)') != -1:
            result = ''
            for char in line[line.find('alias (gamename)')+17:]:
                if char == '#':
                    break
                result += char
            if len(result) != 0:    
                return result
    return None    

#Could be useful to build out a card_code ref file that can be cached to locate which file the card is in faster.
def get_card_info(card_code):
    data_dir = 'C://Projects//Programming Projects//Runeterra API//data_dragon//en_us//data//'
    for i in range(1,5):
        with open(data_dir+'set'+str(i)+'-en_us.json', 'r', encoding='utf8') as f:
            cards = json.load(f)
        for card in cards:
            if card['cardCode']==card_code:
                return DictToClass(card)
    print(card_code)
    return None    

def read():
    with open(os.path.abspath(check_cache('\\LOR_VAULT')+'\\cache.json'), 'r') as f:
        content = json.load(f)
    return DictToClass(content)

def write(data):
    with open(os.path.abspath(check_cache('\\LOR_VAULT')+'\\cache.json'), 'w') as f:
        json.dump(data, f)
    return True