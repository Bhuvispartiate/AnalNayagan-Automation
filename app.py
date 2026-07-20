import requests
from bs4 import BeautifulSoup
import json
import telebot
import threading
import time
import os

TOKEN = '8824453563:AAG3SlczlIDlFT97X0p9JY4BU9nvnGieYbc'
bot = telebot.TeleBot(TOKEN)
SUBSCRIBERS_FILE = 'subscribers.json'

# Load subscribers
def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(subs, f)

# Maintain a set of subscribers in memory
subscribers = set(load_subscribers())

@bot.message_handler(commands=['start', 'subscribe'])
def subscribe_user(message):
    chat_id = message.chat.id
    if chat_id not in subscribers:
        subscribers.add(chat_id)
        save_subscribers(list(subscribers))
        bot.reply_to(message, "You have successfully subscribed to Theatre updates!")
        print(f"New subscriber: {chat_id}")
    else:
        bot.reply_to(message, "You are already subscribed.")

def get_theatres():
    url = "https://ticketnew.com/movies/jana-nayagan-movie-detail-188681"

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "referer": "https://ticketnew.com/movies",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"150\", \"Google Chrome\";v=\"150\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    }

    cookies = {
        "ak_bmsc": "9F632C09B357373DFAC6378B826B5F1E~000000000000000000000000000000~YAAQqKTBF4NWtHKfAQAAfLnSfQBMtya+qjuKJ5OJfa+2Qn5v1qj0nc4NkgsmwP/p+RXmnybyyaFtvhgwv4ygLcrJ3GZ1u/XyAN8SkM9sqrNF44tVViy6ezufZNWK/SD3PrbeV/IzXzmqlvJdSOMbzGBMlOtrKyS+33LKzLx2sz9XNpPn6vO8JXrRdmn3G+eJZG+We0LjOSTUvEuAYIQ2Gtr0mix6JawxrOkGtIH2jNV34F4Mqeq1VbHCXij6ueZkoZweTh1YJ67sQcaiRcHoOvbKiKLu9yoUlJ39emdLIdV+JmqHAxhiDSaZQxa1luWZkjsXGcZBX+B1EevtNV69LeWHK6ZfdWrFkU3c9oHR0HC5jVIC6XWakPU/aS+XZ/i863yW9StSfP9dJ2UPj+0ACz+9K9U=",
        "x-device-id": "151c5c87-00ea-479b-92b3-217a0dd101d3",
        "ext_name": "ojplmecpdpgccookcobabopnaifgidhf",
        "userProfile": "",
        "_ga": "GA1.1.1918744593.1784522389",
        "location": "%7B%22id%22%3A34%2C%22title%22%3A%22Chennai%22%2C%22lat%22%3A13.0827%2C%22long%22%3A80.2707%2C%22cityId%22%3A34%2C%22cityName%22%3A%22Chennai%22%2C%22pCityId%22%3A34%2C%22pCityKey%22%3A%22chennai%22%2C%22pCityName%22%3A%22Chennai%22%7D",
        "_gcl_au": "1.1.1397410787.1784522389.-.-.1784522389.1013316774.1784522389.1784522480",
        "bm_sv": "468404402B27C0722D06AA3D23A04557~YAAQBIzQFyYPaV2fAQAAbSfUfQCftnctNGGqzX+9j2BEh9g/w205iuV6I8B/3Yv9G1kU6RB7TwDbzRFyQxv2y/+5UxlrUr+JC9srTrIloKiBZUz32tVDLij6NViVF8y0thpxrahabueCDapPeXyqyVcXTsejtLstcKXYuehIEZSdt8CmBsr+rqp7+qoA+yqrwOWgmYsoXJvD0QlsOLdPGtcXkhLsvo5X/+97QsjoFLGI7Q/hdJ9xpIB6/eYdxZViKeW6GA==~1",
        "_ga_VZ0PCGWX4Z": "GS2.1.s1784522389$o1$g1$t1784522480$j60$l0$h0",
        "_dd_s": "rum=2&id=9175a63e-e983-404e-b6c5-6222a912782c&created=1784522388734&expire=1784523488721",
        "RT": "\"z=1&dm=ticketnew.com&si=89daec0a-98f5-44b9-9fff-9daa6ee20c5a&ss=mrsqjyut&sl=4&tt=1b7&obo=3&rl=1&ld=4b8a&r=4fnwytoz&ul=4b8b\""
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code != 200:
            print(f"Failed to fetch page, status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if not script_tag:
            print("Could not find __NEXT_DATA__ script tag.")
            return []
            
        data = json.loads(script_tag.string)
        movie_sessions = data['props']['pageProps']['initialState']['movies']['movieSessions']
        
        if not movie_sessions:
            print("No movie sessions found.")
            return []
            
        session_key = list(movie_sessions.keys())[0]
        session_data = movie_sessions[session_key]
        cinemas_map = session_data.get('cinemasMap', {})
        
        theatres = []
        for cinema_id, cinema_info in cinemas_map.items():
            theatre_name = cinema_info.get('name')
            if theatre_name:
                theatres.append(theatre_name)
            
        return theatres
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []

def monitor_theatres():
    print("Starting theatre monitor loop...")
    known_theatres = set(get_theatres())
    print(f"Initial theatres found: {len(known_theatres)}")
    
    while True:
        time.sleep(5) # Check every 5 seconds
        print("Checking for updates...")
        current_theatres = set(get_theatres())
        
        if not current_theatres:
            continue
            
        new_theatres = current_theatres - known_theatres
        if new_theatres:
            message = "New Theatres Added!\n\n"
            for t in new_theatres:
                message += f"- {t}\n"
                
            print(f"Found new theatres: {new_theatres}")
            
            # Notify subscribers
            for chat_id in subscribers:
                try:
                    bot.send_message(chat_id, message)
                except Exception as e:
                    print(f"Failed to send message to {chat_id}: {e}")
                    
            known_theatres = current_theatres

if __name__ == "__main__":
    # Start the monitor thread
    monitor_thread = threading.Thread(target=monitor_theatres, daemon=True)
    monitor_thread.start()
    
    # Start bot polling
    print("Bot is polling. Send /subscribe to it on Telegram!")
    bot.infinity_polling()
