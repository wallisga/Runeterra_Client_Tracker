import requests
from datetime import datetime
from time import sleep, time
import logging
import json
from lor_deckcodes import LoRDeck
from cache import check_cache, get_card_info, get_username

with open('token.json') as f:
    token = json.loads(f)

class DictToClass(object):
    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])

    def add(self, data):
        for key in data:
            setattr(self, key, data[key])

def hb():
    endpoint_list = [{'name': 'active_deck', 'url': 'http://127.0.0.1:2133/static-decklist'}, {'name': 'card_positions', 'url': 'http://127.0.0.1:2133/positional-rectangles'}, 
                {'name': 'expedition_state', 'url': 'http://127.0.0.1:2133/expeditions-state'}, {'name': 'game_result', 'url': 'http://127.0.0.1:2133/game-result'}]
    heartbeat = {'cache_data': {'timestamp': datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"), 'username': get_username()}}
    
    for endpoint in endpoint_list:
        success = False
        while not success:
            try:
                response = requests.get(endpoint['url'])
                success = True
            except requests.exceptions.RequestException as e:
                logging.warning('Heartbeat Status Code: None')
                logging.info('Runeterra is not running... ')
                sleep(5)
                continue
        result = response.json()
        heartbeat[endpoint['name']] = result

    sleep(0.5)
    return DictToClass(heartbeat)

def get_puuid(username):
    url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+username
    result = requests.get(url, headers=token)
    logging.info('get_puuid Status Code - '+str(result.status_code))
    sleep(5)
    while result.status_code != 200:
        logging.error('/lol/summoner/v4/summoners/by-name/$username - Endpoint Unavailable')    
        sleep(5)
        result = requests.get(url, headers=token)
    return result.json()

def get_summoner(puuid):
    url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/'+puuid
    headers = {
        "X-Riot-Token": "RGAPI-999f2ede-be54-4053-82c2-bafbc381c9fe"
    }    
    result = requests.get(url, headers=token)
    logging.info('get_summoner Status Code - '+str(result.status_code))
    sleep(5)
    while result.status_code != 200:
        logging.error('/lol/summoner/v4/summoners/by-puuid/$puuid - Endpoint Unavailable')
        sleep(5)
        result = requests.get(url, headers=token)
    return result.json()    

def get_match_history(puuid):
    url = 'https://americas.api.riotgames.com/lor/match/v1/matches/by-puuid/'+puuid+'/ids'
    headers = {
        "X-Riot-Token": "RGAPI-999f2ede-be54-4053-82c2-bafbc381c9fe"
    }    
    result = requests.get(url, headers=token)
    logging.info('get_match_history Status Code - '+str(result.status_code))
    sleep(5)
    while result.status_code != 200:
        logging.error('/lor/match/v1/matches/by-puuid/$puuid/ids - Endpoint Unavailable')
        sleep(5)
        result = requests.get(url, headers=token)
    return result.json()

def get_match(match):
    url = 'https://americas.api.riotgames.com/lor/match/v1/matches/'+match[0]
    headers = {
        "X-Riot-Token": "RGAPI-999f2ede-be54-4053-82c2-bafbc381c9fe"
    }    
    result = requests.get(url, headers=token)
    logging.info('get_match Status Code - '+str(result.status_code))
    sleep(5)
    while result.status_code != 200:
        logging.error('/lor/match/v1/matches/ - Endpoint Unavailable')
        sleep(5)
        result = requests.get(url, headers=token)
    data = result.json() 
    data['index']=match[1]
    return data

def decode_deck(deck_code):
    deck = []
    if deck_code:
        for card in LoRDeck.from_deckcode(deck_code):
            index = int(card[0])
            while index >= 1:
                deck.append(card[2:])
                index-=1
        deck.sort()
        return deck
    return None

def encode_deck(deck):
    try:
        deck.sort()
    except AttributeError as e:
        logging.error('Cannot Encode Deck Data - ' + str(e))
        return None
    card_dict = {}
    for card_code in deck:
        if card_code in card_dict.keys():
            card_dict[card_code]+=1
        else:
            card_dict[card_code] = 1
    deck_list = []
    for card in card_dict:
        deck_list.append(str(card_dict[card])+':'+card)

    return LoRDeck(deck_list).encode()

def get_card_image(url, card_code):
    response = requests.get(url, stream=True)
    logging.info('get_card_image:card_code Status code: ' + str(response.status_code))
    while response.status_code != 200:
        logging.error('get_card_image:card_code - Endpoint Unavailable')
        sleep(5)
        response = requests.get(url, stream=True)        
    with open(check_cache("\\LOR_VAULT") + '\\img\\' + card_code + '.png', 'wb') as f:
        f.write(response.content)
    del response

def get_card_data(deck):
    card_data = []
    if deck:
        for card in deck:
            x = get_card_info(card)
            card_data.append(x)
        return card_data
    return None

def get_champions_index(card_data):
    count = 0
    results = {}
    if card_data:
        for card in card_data:
            if not card:
                continue
            if card.rarity == 'Champion':
                results[card.cardCode] = count
            count+=1
        return results
    return None