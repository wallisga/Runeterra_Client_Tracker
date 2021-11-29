from tkinter import *
import tkinter.font as font
from tkinter import ttk
from api_vault import get_card_image
from PIL import Image, ImageTk
import os

class Window:

    def __init__(self):
        #There are 4 valid states. (0: Loading data; 1: Menu not expedition_active; 2: Menu and expedition_active; 3: Game not expedition_active; 4: Game and expedition_active)        
        self.state = 0
        self.memory_dir = os.path.abspath(os.getenv('LOCALAPPDATA')+"\\LOR_VAULT\\")


        self.root = Tk()
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()       
        self.x = int(self.width*.745)
        self.y = int(self.height*.843)
        #self.frame = Frame(self.root, bg= '#a18484', width=int(self.width/4), height=int(self.height/8))
        self.create_tabs('Active Deck Info Loading...', 'Active Expedition Info Loading...')
        self.root.geometry('%dx%d+%d+%d' % (int(self.width/4), int(self.height/8), self.x, self.y))
        self.root.title('LORVAULT')
        self.root.iconbitmap('icon.ico')
        #self.main_string = Label(self.frame, text=str('Loading'), justify='left', font= font.Font(family='Adobe Song Std'), bg=self.frame['bg'], width=int(self.width/4), height=int(self.height/8)) 
        #self.frame.pack()
        #self.main_string.pack()  

        
    def update(self):
        self.root.update()

    def redraw_mainframe(self, tab1, tab2, data):
        self.tabControl.destroy()
        self.create_tabs(tab1, tab2, data)       

    def create_tabs(self, tab1, tab2, data=None):
        self.tabControl = ttk.Notebook(self.root)
        self.style = ttk.Style()
        self.style.configure('Tab.TFrame', background='#909383')
        self.deck_tab = ttk.Frame(self.tabControl, style='Tab.TFrame')
        self.exp_tab = ttk.Frame(self.tabControl, style='Tab.TFrame')
        self.tabControl.add(self.deck_tab, text='Deck')
        self.tabControl.add(self.exp_tab, text='Expedition')
        self.tabControl.pack(expand=1, fill="both")
        if data:
            count=0
            for champ in data.expedition.champions_index:
                count +=1
                get_card_image(data.expedition.card_data[data.expedition.champions_index[champ]-1].assets[0]['fullAbsolutePath'], champ)
                image = Image.open(self.memory_dir + '\\img\\' + champ + '.png')
                pixels_x, pixels_y = tuple([int(x)  for x in image.size])
                img = ImageTk.PhotoImage(image.resize((int(pixels_x/16), int(pixels_y/16)))) 
                label = Label(self.exp_tab, image=img, background='#909383')
                label.image = img
                label.grid(column=count, row=1, padx=5, pady=5)
            print(data.expedition.record)
            ttk.Label(self.exp_tab, text=data.expedition.record, justify='left', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=0, row=1, padx=20, pady=5)
        ttk.Label(self.deck_tab, text=tab1, justify='left', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=0, row=0, padx=20, pady=5)
        ttk.Label(self.exp_tab, text=tab2, justify='left', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=0, row=0, padx=20, pady=5)
        ttk.Label(self.exp_tab, text='Champions', justify='center', font= font.Font(family='Adobe Song Std'), background='#909383').grid(column=1, row=0, padx=20, pady=5)             


    def display_state(self, state, data):
        if self.state == state:
            return None
        self.state = state
        if self.state == 0:
            self.redraw_mainframe(data.username, data.username, data=data)
        elif self.state == 1:
            self.redraw_mainframe(data.username, data.username, data=data)
        elif self.state == 2:
            self.redraw_mainframe(data.username, data.username, data=data)
        elif self.state == 3:
            self.redraw_mainframe(data.username, data.username, data=data)
        elif self.state == 4:
            self.redraw_mainframe(data.username, data.username, data=data)           
        #data = Label(self.root, text=str(data.record))
        #self.main_string.pack()
        #data.pack()

    def loop(self,state,data):
        while True:
            self.display_state(state,data)
            self.update()