"""
Teveclub Bot Core Module
Contains the main bot class with all game actions
"""
import requests
from bs4 import BeautifulSoup
import random
import time
from src.config import LOGIN_URL, MYTEVE_URL, TANIT_URL, TIPP_URL
from src.utils import get_user_agent, do_sleep


class TeveClub:
    """Main bot class for interacting with Teveclub website"""
    
    def __init__(self, username, password):
        """
        Initialize the TeveClub bot
        
        Args:
            username (str): User's teveclub username
            password (str): User's teveclub password
        """
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.user_agent = None
        
    def get_session(self):
        """
        Get the current session object
        
        Returns:
            requests.Session: The current session
        """
        return self.session
    
    def login(self):
        """
        Login to the Teveclub website
        
        Returns:
            bool: True if login successful, False otherwise
        """
        self.user_agent = get_user_agent()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        data = {
            'tevenev': self.username,
            'pass': self.password,
            'x': '38',
            'y': '42',
            'login': 'Gyere!'
        }

        r = self.session.post(LOGIN_URL, data=data)
        do_sleep()
        
        r = self.session.get(MYTEVE_URL)
        do_sleep()
        
        login_success = 'Teve Legyen Veled!' in r.text
        if login_success:
            print('Login success!!')
        
        return login_success
        
    def learn(self):
        """
        Learn a new trick for the pet
        
        Returns:
            bool: True if learning successful, False otherwise
        """
        self.session.get(MYTEVE_URL)
        do_sleep()
        
        r = self.session.get(TANIT_URL)
        do_sleep()
        
        if 'Nincs több olyan trükk, amit a tevéd meg tud tanulni!' in r.text:
            print('No new trick to learn!!!')
            return False
        
        if 'Válaszd ki, hogy mit tanuljon a tevéd:' in r.text:
            print('There is to learn!')
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Get available learning options
            options = {}
            i = 0
            for option in soup.find_all('option'):
                options[i] = option['value']
                i += 1
            
            val = random.choice(list(options.values()))
            print(f"Lesson id: {val}")
            
            data = {
                'learn': 'Tanulj teve!',
                'tudomany': val
            }
            self.session.post(TANIT_URL, data=data)
            print('Tanítás Vége')
            do_sleep()
        else:
            data = {
                'farmdoit': 'tanit',
                'learn': 'Tanulj teve!'
            }
            self.session.post(TANIT_URL, data=data)
            print('Learning success!!!')
            do_sleep()
        
        return True
                
    def feed(self):
        """
        Feed the pet intelligently - checks if feeding is needed before feeding
        
        Returns:
            bool: True if feeding successful, False otherwise
        """
        r = self.session.get(MYTEVE_URL)
        do_sleep()
        
        # Check if feeding button is available
        if 'Mehet!' not in r.text:
            print('Pet does not need feeding right now!')
            return False
        
        # Parse the page to check current food/water levels
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Feed until the pet is satisfied or max attempts reached
        feed_count = 0
        max_attempts = 10
        
        while feed_count < max_attempts:
            # Check if we can still feed
            r = self.session.get(MYTEVE_URL)
            do_sleep()
            
            if 'Mehet!' not in r.text:
                print(f'Pet is full after {feed_count} feeding(s)!')
                break
            
            # Feed the pet
            data = {
                'kaja': '1',
                'pia': '1',
                'etet': 'Mehet!',
            }
            r = self.session.post(MYTEVE_URL, data=data)
            feed_count += 1
            do_sleep()
            
            # Check response for success
            if 'elég jóllakott' in r.text or 'tele a hasa' in r.text:
                print(f'Pet is satisfied after {feed_count} feeding(s)!')
                break
        
        print(f'Feeding complete! Fed {feed_count} time(s).')
        return True
        
    def guess(self):
        """
        Play the guess game
        
        Returns:
            bool: True if guess successful, False otherwise
        """
        self.session.post(TIPP_URL, data={'honnan': '403', 'tipp': 'Ez a tippem!'})
        print('Guess Game success!!!')
        do_sleep()
        return True

    def run_bot(self):
        """
        Run all bot actions in sequence
        
        Returns:
            bool: True if bot ran successfully, False otherwise
        """
        if not self.login():
            print("Login failed!!!")
            return False
        
        # Feed the pet
        try:
            self.feed()
        except Exception as e:
            print(f"Feeding failed!!! Error: {e}")
        
        # Learn tricks
        try:
            self.learn()
        except Exception as e:
            print(f"Learning failed!!! Error: {e}")
        
        # Play guess game
        try:
            self.guess()
        except Exception as e:
            print(f"Guess Game failed!! Error: {e}")
        
        time.sleep(3)
        return True
