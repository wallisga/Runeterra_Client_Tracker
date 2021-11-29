# Import Module
from tkinter import Tk, Variable, Label, Frame, Button, ttk
import tkinter.font as font
from PIL import Image, ImageTk
from time import sleep, time
from sys import exit
import logging

from mem2 import Mem
from api_vault import get_card_image, decode_deck, get_card_data, get_champions_index
from cache import check_cache


def build_root():
    root = Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()       
    x = int(width*.661)
    y = int(height*.843)
    #frame = Frame(root, bg= '#a18484', width=int(width/4), height=int(height/8))
    root.geometry('%dx%d+%d+%d' % (int(width/3), int(height/8), x, y))
    root.title('LORVAULT')
    root.iconbitmap('icon.ico')
    return root    

def build_frame(container, memory, state):
    frame = Frame(container)
    frame.pack()
    create_tabs(frame,memory,state)
    return frame

def create_tabs(frame, memory, state):
    tabControl = ttk.Notebook(frame)
    style = ttk.Style()
    style.configure('Tab.TFrame', background='#909383')
    deck_tab = ttk.Frame(tabControl, style='Tab.TFrame')
    exp_tab = ttk.Frame(tabControl, style='Tab.TFrame')
    tabControl.add(deck_tab, text='Deck')
    tabControl.add(exp_tab, text='Expedition')
    tabControl.pack(expand=1, fill="both")
    update_tab(memory,deck_tab, decode_deck(memory.data.active_deck['DeckCode']), 'record')
    update_tab(memory,exp_tab, decode_deck(memory.data.expedition_state['Deck']), memory.data.expedition_state['Record'])
    ttk.Label(deck_tab, text=memory.data.cache_data['username'], justify='left', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=0, row=0, padx=20, pady=5)
    ttk.Label(deck_tab, text='Champions', justify='center', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=1, row=0, padx=20, pady=5)    
    ttk.Label(exp_tab, text=memory.data.cache_data['username'], justify='left', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=0, row=0, padx=20, pady=5)
    ttk.Label(exp_tab, text='Champions', justify='center', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=1, row=0, padx=20, pady=5)      

def update_tab(memory,tab,deck,record):
    card_data = get_card_data(deck)
    if card_data:
        index = get_champions_index(card_data)
        count=0
        for champ in index:
            count +=1
            get_card_image(card_data[index[champ]].assets[0]['fullAbsolutePath'], champ)
            image = Image.open(check_cache("\\LOR_VAULT") + '\\img\\' + champ + '.png')
            pixels_x, pixels_y = tuple([int(x)  for x in image.size])
            img = ImageTk.PhotoImage(image.resize((int(pixels_x/20), int(pixels_y/20)))) 
            label = Label(tab, image=img, background='#909383')
            label.image = img
            label.grid(column=count, row=1, padx=5, pady=5)
        #ttk.Label(tab, text=record, justify='left', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=0, row=1, padx=20, pady=5)            


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='data\\logs\\treasure.log', filemode='w', level=logging.INFO)
    logging.info('Session logging started')
    root = build_root() 
    memory = Mem()
    container = Frame(root)
    container.pack()
    state = memory.state
    frame = build_frame(container, memory, state)
    while True:
        if memory.thread_count < 3:
            memory.threading(state)
        sleep(0.1)
        if memory.state != state:
            logging.info('State change from '+str(state)+' to '+str(memory.state))
            state = memory.state
            frame.destroy()
            frame = build_frame(container, memory, state)
        root.update()

if __name__ == '__main__':
    exit(main())