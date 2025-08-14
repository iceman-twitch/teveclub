#-------------------------------------------------------------------------------
# Name:        TEVECLUB BOT
# Purpose:     Testing request capabilities in a webgame
#
# Author:      ICEMAN
#
# Created:     10.01.2020
# Copyright:   (c) ICEMAN 2025
# Licence:     <ICEMAN>
#-------------------------------------------------------------------------------

#IMPORTS
import requests
from bs4 import BeautifulSoup
import time
import random
import sys
import os
import json

#USERAGENT
def get_new_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    ]
    return random.choice(user_agents)
    
#MAIN CLASS
class teveclub():
    def __init__(self, a, b):
        self.s = requests.Session()
        self.a=a
        self.b=b
        self.LOGIN_URL="https://teveclub.hu/"
        self.MYTEVE_URL = "https://teveclub.hu/myteve.pet"
        self.TANIT_URL = "https://teveclub.hu/tanit.pet"
        self.TIPP_URL = "https://teveclub.hu/egyszam.pet"
        self.ua = None

    def useragent(self):
        # Default user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
        ]
        
        # Try to load from JSON file if it exists
        json_file = "user_agents.json"
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    # Check if loaded data is a list of strings
                    if isinstance(data, list) and all(isinstance(x, str) for x in data):
                        user_agents = data
                    # Alternatively check if it's a dict with 'user_agents' key
                    elif isinstance(data, dict) and 'user_agents' in data and isinstance(data['user_agents'], list):
                        user_agents = data['user_agents']
            except (json.JSONDecodeError, PermissionError):
                pass  # Fall back to default if there's any error
        
        return random.choice(user_agents)
    
    def dosleep(self):
        time.sleep(min(random.expovariate(1.6), 3.0))
    
    def GetSession(self):
        return self.s
    
    def Login(self):
        usera = get_new_user_agent()
        self.s.headers.update({ "User-Agent": usera })
        data = {}
        data['tevenev'] = self.a
        data['pass'] = self.b
        data['x'] = '38'
        data['y'] = '42'
        data['login'] = 'Gyere!'

        r = self.s.post(self.LOGIN_URL , data=data)
        self.dosleep()
        r = self.s.get(self.MYTEVE_URL)
        self.dosleep()
        login=False
        if ('Teve Legyen Veled!' in r.text):
            print('Login success!!')
            login=True
        return login
        
    def Learn(self):
        self.s.get(self.MYTEVE_URL)
        self.dosleep()
        r = self.s.get(self.TANIT_URL)
        self.dosleep()
        if ('Nincs több olyan trükk, amit a tevéd meg tud tanulni!' in r.text):
            print('No new trick to learn!!!')
            return False
        else:
            if ('Válaszd ki, hogy mit tanuljon a tevéd:' in r.text):
                print('There is to learn!')
                soup = BeautifulSoup(r.text,"html.parser")
                data = {}
                i=0
                for option in soup.find_all('option'):
                    #print( 'value: {}, text: {}'.format(option['value'], option.text) )
                    data[i] = option['value']
                    #print(data[i])
                    i = i + 1
                print("Lesson id: ", random.choice(data))
                val = random.choice(data)
                data = {
                    'learn': 'Tanulj teve!',
                    'tudomany': val
                }
                self.s.post(TANIT_URL , data=data)
                print('Tanítás Vége')
                self.dosleep()
            else:
                data = {
                    'farmdoit': 'tanit',
                    'learn': 'Tanulj teve!'
                }
                self.s.post(TANIT_URL , data=data)
                print('Learning success!!!')
                self.dosleep()
            return True
                
    def Food(self):
        r = self.s.get(self.MYTEVE_URL)
        self.dosleep()
        etet = 0
        if ('Mehet!' in r.text != True):
                etet = False
        while (etet < 10):
            data = {
                'kaja': '1',
                'pia': '1',
                'etet': 'Mehet!',
            }
            r = self.s.post(self.MYTEVE_URL , data=data)
            etet = etet + 1
            self.dosleep()
        print('Feeding success!!!')
        self.dosleep()
        return True
        
    def Guess(self):
        self.s.post('https://teveclub.hu/egyszam.pet',data={'honnan':'403','tipp':'Ez a tippem!'})
        print('Guess Game success!!!')
        self.dosleep()
        return True

    def Bot(self):
        if self.Login():
            try:
                self.Food()
            except:
                print("Feeding failed!!!")
            try:
                self.Learn()
            except:
                print("Learning failed!!!")
            try:
                self.Guess()
            except:
                print("Guess Game failed!!")
            time.sleep(3)
        else:
            print("Login failed!!!")
            

def test_teveclub():
    #ARGUMENTS
    if len(sys.argv) > 1:
        print(f"Argument 1: {sys.argv[1]}, Argument 2: {sys.argv[2]}")
    else:
        print("No arguments provided")
        sys.exit(1)
        
    #CONSTRAINTS
    USER = str(sys.argv[1])
    PASSW = str(sys.argv[2])

    #VARS
    s = None
    
    #STARTBOTCLASS
    teve = teveclub(USER, PASSW)
    teve.Bot()

if __name__ == "__main__":
    test_teveclub()