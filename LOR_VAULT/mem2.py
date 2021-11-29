from threading import *
from time import time
import logging
from secrets import token_hex

from api_vault import hb, encode_deck, decode_deck, get_puuid, get_match_history, get_match
from cache import check_cache, read, write, get_username

class Mem():

    def __init__(self):
        self.state = 0
        self.data = hb()
        logging.info('Connected successfully to Runeterra Game Client')    
        username = get_username()
        try:
            self.cached = read()
            if username != self.cached['username']:
                raise FileNotFoundError
            logging.info('READ CACHE for user '+self.cached['username'])

        except FileNotFoundError:
            puuid = get_puuid(username)['puuid']
            matches = []
            decks = []
            for match in get_match_history(puuid):
                    count = 0
                    for player in get_match(match)['info']['players']:
                        if player['puuid'] == puuid and player['deck_code'] not in decks:
                            decks.append((player['deck_code']))
                        matches.append((match, count))
                        count += 1              
            self.cached = {'username': username, 'puuid': puuid, 'matches': matches, 'decks': decks}
            logging.info('WRITE CACHE for user '+self.cached['username'])                
            write(self.cached)

        self.state_calc(self.state)
        self.thread_count = active_count()


    def threading(self,previous):
        t1 = Thread(target=self.hb_worker, args=[previous])
        self.thread_count = active_count()
        t1.start()


    # work function
    def hb_worker(self,previous):
        self.data = hb()
        self.state_calc(previous)
        self.thread_count = active_count()
            

    def state_calc(self, previous):

        if self.data.active_deck['DeckCode'] and self.data.expedition_state['IsActive']:
            self.state = 4
            if self.state != previous:
                logging.info('Expedition game started see deck_code below')
                logging.info(self.data.active_deck['DeckCode'])
        elif self.data.active_deck['DeckCode']:
            self.state = 3
            if self.state != previous:
                logging.info('General game started see deck_code below')
                logging.info(self.data.active_deck['DeckCode'])
        elif self.data.expedition_state['IsActive']:
            self.state = 2
            if self.state != previous:
                logging.info('Expedition started')            
        else:
            self.state = 1
            if self.state != previous:
                logging.info('Browsing menus without expedition')