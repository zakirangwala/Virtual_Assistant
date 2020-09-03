"""
Things to add :
Bus/Subway Times
What,Where,How,Why : Google Search
Spotify Music
Read Inbox and Emails : https://www.youtube.com/watch?v=6DD4IOHhNYo&list=PLEsfXFp6DpzQjDBvhNy5YbaBx9j-ZsUe6&index=9
Maps API : https://www.youtube.com/watch?v=ckPEY2KppHc&list=PLEsfXFp6DpzQjDBvhNy5YbaBx9j-ZsUe6&index=20
Twitter API : https://www.youtube.com/watch?v=dvAurfBB6Jk&list=PLEsfXFp6DpzQjDBvhNy5YbaBx9j-ZsUe6&index=21
"""

# Import Libraries
from bs4 import BeautifulSoup
from googlesearch import search
from json.decoder import JSONDecodeError
import pyttsx3
import datetime
import speech_recognition as sr
import speedtest
import wikipedia as w
import requests
import webbrowser
from playsound import playsound
from Spotify import SpotifyAPI

# Initialize Text to Speech
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Speak Function


def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Greeing Function


def greet():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour <= 12:
        speak("Good Morning!")
    elif hour > 12 and hour < 16:
        speak("Good Afternoon!")
    elif hour > 16 and hour < 20:
        speak("Good Evening!")
    else:
        speak("Good Night!")
    speak("Hi, I am your virtual assistant. Please tell me how to help you")

# Listen to user input


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # print("Listening...")
        speak("I'm Listening")
        r.pause_threshold = 1
        audio = r.listen(source, timeout=1, phrase_time_limit=5)
    try:
        # print("Recognizing...")
        # speak("Recognizing...")
        playsound('sound.mp3')
        query = r.recognize_google(audio, language='en-CA')
        #print("User said: {}".format(query))
    except Exception as e:
        #print("Say that again please")
        speak("Say that again please")
        return "None"
    return query

# Internet Search


def google_query(query):
    link = []
    for j in search(query, tld="ca", num=10, stop=10, pause=2):
        link.append(j)
    return link

# Check Price of stock


def check_price():
    try:
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        price = soup.find(
            class_='Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)').get_text()
        title = soup.find(class_='D(ib) Fz(18px)').get_text()
        currency = soup.find(class_='C($tertiaryColor) Fz(12px)').get_text()
        currency = currency[-3:]
    except AttributeError as e:
        return False
    return currency, title, price


# Configure Browser Header and URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
URL = ''

# Spotify Integration


def song_credits(song):
    try:
        client_id = 'de870cc0e21c4975b52ba7b4e83e8dd2'
        client_secret = '1fbfbc7336984877840c8a0db020de38'
        spotify = SpotifyAPI(client_id, client_secret)
        spotify.get_access_token()
        data = spotify.search(song, search_type="track")
    except IndexError as e:
        return False
    return data

# Open Browser


def open_browser(url):
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open_new_tab(url)

# Internet Speedtest


def speed_check():
    try:
        # print('Testing...')
        speak('Testing...')
        s = speedtest.Speedtest()
        s.get_best_server()
        s.download()
        s.upload()
        res = s.results.dict()
        server = []
        server.append(res["server"]["name"])
        server.append(res["server"]["country"])
        server.append(res["server"]["sponsor"])
        client = []
        client.append(res["client"]["ip"])
        client.append(res["client"]["isp"])
        speed = []
        ONE_MB = 1000000
        speed.append((round((res["download"]/ONE_MB), 2)))
        speed.append((round((res["upload"]/ONE_MB), 2)))
        speed.append((round((res["ping"]), 2)))
        #print(f'IP address : {client[0]}\nService Provider : {client[1]}')
       # print(f'Connected to {server[2]} server\nLocation : {server[0]}, {server[1]}')
        #print(f'Download speed  : {speed[0]} mpbs\nUpload speed : {speed[1]} mpbs\nPing : {speed[2]} ms ')
        speak(
            f'Download speed is {speed[0]} megabytes per second  upload speed is {speed[1]} megabytes per second, ping is {speed[2]} milliseconds ')
    except Exception as e:
        #print("Say that again please")
        speak("Say that again please")

# Get Location


def get_location():
    URL = 'https://iplocation.com/'
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    city = soup.find(class_='city').get_text()
    country = soup.find(class_='country_name').get_text()
    latitude = soup.find(class_='lat').get_text()
    longitude = soup.find(class_='lng').get_text()
    return city, country, latitude, longitude

# Check Weather


def weather(latitude, longitude):
    try:
        api_key = '30542e6bdd35e42a27293aea86597947'
        base_url = 'http://api.openweathermap.org/data/2.5/weather?'
        complete_url = base_url + "lat=" + \
            str(latitude) + "&lon=" + str(longitude) + "&appid=" + api_key
        response = requests.get(complete_url)
        x = response.json()
    except Exception as e:
        #print("Say that again please")
        speak("Say that again please")
    if x["cod"] != "404":
        return x
    else:
        return False


# Main Method
if __name__ == "__main__":
    # greet()
    city, country, latitude, longitude = get_location()
    while True:
        query = listen().lower()
        if 'stop' in query or 'thank you' in query:
            speak('Have a wonderful day!')
            break
        elif 'hey' in query or 'hi' in query or 'hello' in query:
            speak('Hey there!')
        elif 'wikipedia' in query:
            #print('Searching...')
            speak('Searching...')
            query = query.replace('wikipedia', '')
            results = w.summary(query, sentences=1)
            speak("According to Wikipedia")
           # print("According to Wikipedia : {} ".format(results))
            speak(results)
        elif 'stock' in query:
            query += query + " Yahoo Finance"
           # print('Searching...')
            speak('Searching...')
            URL = google_query(query)[0]
            if check_price() == False:
                #print("Say that again please")
                speak("Say that again please")
            else:
                currency, title, price = check_price()
               # print("The price of {} is {} {}".format(title, price, currency))
                speak("The price of {} is {} {}".format(title, price, currency))
        elif 'open' in query:
            if 'google' in query:
                open_browser('google.ca')
            elif 'my website' in query:
                open_browser('https://zakirangwala.com/')
            else:
                query = query.replace('open', '')
                query += ' website '
                URL = google_query(query)[0]
                open_browser(URL)
        elif 'song' in query:
            try:
                index = query.find('song') + 5
                if index == 4:
                    #print("Say that again please")
                    speak("Say that again please")
                else:
                    song = query[index:]
                    data = song_credits(song)
                    artists = []
                    if data['tracks']['total'] == 0:
                       # print("Say that again please")
                        speak("Say that again please")
                    else:
                        # print(data)
                        for i in range(len(data['tracks']['items'][0]['artists'])):
                            artists.append(data['tracks']['items']
                                           [0]['artists'][i]['name'])
                        if artists == 1:
                           # print(  f'The artist who sang this song is {artists}')
                            speak(
                                f'The artist who sang this song is {artists}')
                        else:
                            #print(f'The artists who sang this song are {artists}')
                            speak(
                                f'The artists who sang this song are {artists}')
            except Exception as e:
                #print("Say that again please")
                speak("Say that again please")
        elif ('internet' in query and 'speed' in query) or 'speed test' in query:
            speed_check()
        elif 'weather' in query or 'temperature' in query:
            x = weather(latitude, longitude)
            if x == False:
                #print('Please try again')
                speak('Please try again')
            else:
                temp = (int)((x["main"]["temp"]) - 273.15)
                feel = (int)((x["main"]["feels_like"]) - 273.15)
                min_ = (int)((x["main"]["temp_min"]) - 273.15)
                max_ = (int)((x["main"]["temp_max"]) - 273.15)
                sunrise = x["sys"]["sunrise"]
                sunrise = datetime.datetime.fromtimestamp(
                    sunrise).strftime('%H:%M')
                sunset = x["sys"]["sunset"]
                sunset = datetime.datetime.fromtimestamp(
                    sunset).strftime('%H:%M')
                description = x["weather"][0]["description"]
                #print( f'The temperature is {temp}°C and it feels like {feel} °C\nThe low is {min_}°C and the high is {max_}°C\nThe predicted forecast is {description}')
                speak(
                    f'The temperature is {temp} degrees celsius. It feels like {feel} degrees celsius. The low is {min_} degrees celsius and the high is {max_} degrees celsius. The predicted forecast is {description}')
                now = int(datetime.datetime.now().hour)
                temp = sunrise[0:2]
                temp = int(temp)
                delta_og = int(sunset[0:2])
                if delta_og > 12:
                    delta = delta_og - 12
                if now > temp and now < delta_og:
                    minutes = sunset.find(":")
                    time = '' + str(delta) + ':' + sunset[minutes:]
                    speak(f"The sun will fall at {time} today")
                elif now < temp:
                    speak(f"The sun will rise at {sunrise} today")
