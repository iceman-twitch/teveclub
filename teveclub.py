#-------------------------------------------------------------------------------
# Name:        TEVECLUB TEST
# Purpose:
#
# Author:      ICEMAN
#
# Created:     10.01.2020
# Copyright:   (c) ICEMAN 2020
# Licence:     <ICEMAN>
#-------------------------------------------------------------------------------

#IMPORTS
import requests
from bs4 import BeautifulSoup
import time
import random
import sys

if len(sys.argv) > 1:
    print(f"Argument 1: {sys.argv[1]}, Argument 2: {sys.argv[2]}")
else:
    print("No arguments provided")
    sys.exit(1)
#CONSTRAINTS
USER = str(sys.argv[1])
PASSW = str(sys.argv[2])
LOGIN_URL = "https://teveclub.hu/"
MYTEVE_URL = "https://teveclub.hu/myteve.pet"
TANIT_URL = "https://teveclub.hu/tanit.pet"
TIPP_URL = "https://teveclub.hu/egyszam.pet"
#VARS
s = None
# ADD TUDOMANY TO POST
"""
Origin https://teveclub.hu
Upgrade-Insecure-Requests 1
Content-Type application/x-www-form-urlencoded
User-Agent Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36
Accept text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
DNT 1
Referer https://teveclub.hu/egyszam.pet
Accept-Encoding gzip, deflate, br
Accept-Language hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7
FORM DATA:
honnan 409
tipp Ez a tippem!
"""

"""
Host: teveclub.hu
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br, zstd
Content-Type: application/x-www-form-urlencoded
Content-Length: 57
Origin: https://teveclub.hu
Connection: keep-alive
Referer: https://teveclub.hu/
Cookie: SESSION_ID=XXX
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1

tevenev=XXX&pass=XXX&x=38&y=42&login=Gyere!
"""
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
        self.LOGIN_URL=LOGIN_URL
        self.MYTEVE_URL = MYTEVE_URL
        self.TANIT_URL = TANIT_URL
        self.TIPP_URL = TIPP_URL
        # self.bot()

    def dosleep(self):
        time.sleep(min(random.expovariate(0.6), 15.0))
        
    def Login(self):
        usera = get_new_user_agent()
        self.s.headers.update({ "User-Agent": usera })
        data = {}
        data['tevenev'] = self.a
        data['pass'] = self.b
        data['x'] = '38'
        data['y'] = '42'
        data['login'] = 'Gyere!'

        r = self.s.post(LOGIN_URL , data=data)
        self.dosleep()
        r = self.s.get(self.MYTEVE_URL)
        self.dosleep()
        login=False
        if ('Teve Legyen Veled!' in r.text):
            print('Sikeres Bejelentkezés')
            login=True
        return login
        
    def Learn(self):
        self.s.get(self.MYTEVE_URL)
        self.dosleep()
        r= self.s.get(self.TANIT_URL)
        self.dosleep()
        if ('Nincs több olyan trükk, amit a tevéd meg tud tanulni!' in r.text):
            print('Nincs több olyan trükk, amit a tevéd meg tud tanulni!')
            return
        else:
            if ('Válaszd ki, hogy mit tanuljon a tevéd:' in r.text):
                print('Van Mit Tanulni!')
                soup = BeautifulSoup(r.text,"html.parser")
                data = {}
                i=0
                for option in soup.find_all('option'):
                    #print( 'value: {}, text: {}'.format(option['value'], option.text) )
                    data[i] = option['value']
                    #print(data[i])
                    i = i + 1
                print("Tanulás azonosítója: ", random.choice(data))
                val = random.choice(data)
                data = {
                    'learn': 'Tanulj teve!',
                    'tudomany': val
                }
                self.s.post(TANIT_URL , data=data)
                self.dosleep()
                print('Tanítás Vége')
            else:
                data = {
                    'farmdoit': 'tanit',
                    'learn': 'Tanulj teve!'
                }
                #r = self.s.get(TANIT_URL)
                self.s.post(TANIT_URL , data=data)
                self.dosleep()
                print('Tanítás Vége')
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
        print('Etetés Vége')
    def Guess(self):
        self.s.post('https://teveclub.hu/egyszam.pet',data={'honnan':'403','tipp':'Ez a tippem!'})
        self.dosleep()
        print('Egyszám! játék Vége')

    def Bot(self):
        if self.Login():
            try:
                self.Food()
            except:
                print("Etetés sikertelen!")
            try:
                self.Learn()
            except:
                print("Tanítás sikertelen!")
            try:
                self.Guess()
            except:
                print("EgySzám! Játék sikertelen!")
            


teve = teveclub(USER, PASSW)
teve.Bot()
