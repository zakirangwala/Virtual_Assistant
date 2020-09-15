# Import Libraries
from bs4 import BeautifulSoup
from googlesearch import search
from json.decoder import JSONDecodeError
from urllib.parse import urlencode
from PyDictionary import PyDictionary
import pyttsx3
import datetime
import speech_recognition as sr
import speedtest
import wikipedia as w
import pandas as pd
import requests
import webbrowser
from playsound import playsound
import config
import smtplib
import wolframalpha
import base64
import sports
import imdb

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
        print("Good Morning!")
    elif hour > 12 and hour < 16:
        speak("Good Afternoon!")
        print("Good Afternoon!")
    elif hour > 16 and hour < 20:
        speak("Good Evening!")
        print("Good Evening!")
    else:
        speak("Good Night!")
        print("Good Night!")
    print("Hi, I am your virtual assistant. Please tell me how to help you")
    speak("Hi, I am your virtual assistant. Please tell me how to help you")

# Listen to user input


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        playsound('sound.mp3')
        print("Listening...")
        #speak("I'm Listening")
        r.pause_threshold = 1
        # audio = r.listen(source, timeout=1, phrase_time_limit=5)
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        print("Recognizing...")
        speak('Recognizing')
        query = r.recognize_google(audio, language='en-CA')
        print("User said: {}".format(query))
    except Exception as e:
        print("Say that again please")
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


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
            # return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']  # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')

    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')

    def base_search(self, query_params):  # type
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def search(self, query=None, operator=None, operator_query=None, search_type='artist'):
        try:
            if query == None:
                raise Exception("A query is required")
            if isinstance(query, dict):
                query = " ".join([f"{k}:{v}" for k, v in query.items()])
            if operator != None and operator_query != None:
                if operator.lower() == "or" or operator.lower() == "not":
                    operator = operator.upper()
                    if isinstance(operator_query, str):
                        query = f"{query} {operator} {operator_query}"
            query_params = urlencode({"q": query, "type": search_type.lower()})
        except Exception as e:
            return False
        return self.base_search(query_params)

# Spotify Search Method


def song_credits(song):
    try:
        client_id = config.client_id
        client_secret = config.client_secret
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
        print('Testing...')
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
        print(f'IP address : {client[0]}\nService Provider : {client[1]}')
        print(
            f'Connected to {server[2]} server\nLocation : {server[0]}, {server[1]}')
        print(
            f'Download speed  : {speed[0]} mpbs\nUpload speed : {speed[1]} mpbs\nPing : {speed[2]} ms ')
        speak(
            f'Download speed is {speed[0]} megabytes per second  upload speed is {speed[1]} megabytes per second, ping is {speed[2]} milliseconds ')
    except Exception as e:
        print("Could not execute speedtest")
        speak("Could not execute speedtest")

# Get Location


def get_location():
    try:
        URL = 'https://iplocation.com/'
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        city = soup.find(class_='city').get_text()
        country = soup.find(class_='country_name').get_text()
        latitude = soup.find(class_='lat').get_text()
        longitude = soup.find(class_='lng').get_text()
        return city, country, latitude, longitude
    except Exception as e:
        print('Error, location could not be retrieved')
        speak('Error, location could not be retrieved')

# Check Weather


def weather(latitude, longitude):
    try:
        api_key = config.api_key
        base_url = 'http://api.openweathermap.org/data/2.5/weather?'
        complete_url = base_url + "lat=" + \
            str(latitude) + "&lon=" + str(longitude) + "&appid=" + api_key
        response = requests.get(complete_url)
        x = response.json()
    except Exception as e:
        print("An error occurred while retrieving weather information")
        speak("An error occurred while retrieving weather information")
    if x["cod"] != "404":
        return x
    else:
        return False

# Send email


def send_mail(subject, body, reciever):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(config.email, config.password)
    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail(config.email, reciever, msg)
    server.quit()

# Rotten Tomatoes Score


def rotten_tomatoes_score(query):
    try:
        query += query + " Rotten Tomatoes"
        URL = google_query(query)[0]
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        res = soup.find(class_='mop-ratings-wrap__percentage').get_text()
        check = res.split(' ')
        for i in check:
            if len(i) > 1:
                return i
    except Exception as e:
        print('Could not retrieve tomatometer score')
        speak('Could not retrieve tomatometer score')

# Fetch Definition


def fetch_definition(word):
    try:
        dict = PyDictionary()
        meaning = dict.meaning(word)
        return meaning
    except Exception as e:
        print('Word may not be present in the english dictionary')
        speak('Word may not be present in the english dictionary')


# Main Method
if __name__ == "__main__":
    # greet()
    city, country, latitude, longitude = get_location()
    # print(f"{city}, {country} : {latitude},{longitude}")
    while True:
        # query = listen().lower()
        query = input("Enter : ")
        if 'wikipedia' in query:
            try:
                print('Searching...')
                speak('Searching...')
                query = query.replace(' wikipedia', '')
                results = w.summary(query, sentences=1)
                speak("According to Wikipedia")
                print("According to Wikipedia : {} ".format(results))
                speak(results)
            except Exception as e:
                print("Could not search wikipedia")
                speak("Could not search wikipedia")
        elif 'stock' in query:
            query += query + " Yahoo Finance"
            print('Searching...')
            speak('Searching...')
            URL = google_query(query)[0]
            if check_price() == False:
                print("Stock Price could not be calculated")
                speak("Stock Price could not be calculated")
            else:
                currency, title, price = check_price()
                print("The price of {} is {} {}".format(title, price, currency))
                speak("The price of {} is {} {}".format(title, price, currency))
        elif 'open' in query:
            try:
                print('Opening..')
                speak('Opening')
                if 'google' in query:
                    open_browser('google.ca')
                elif 'my website' in query:
                    open_browser('https://zakirangwala.com/')
                else:
                    query = query.replace('open ', '')
                    query += ' website '
                    URL = google_query(query)[0]
                    open_browser(URL)
            except Exception as e:
                print("Browser could not be opened")
                speak("Browser could not be opened")
        elif 'song' in query:
            try:
                index = query.find('song') + 5
                if index == 4:
                    print("Please repeat your query")
                    speak("Please repeat your query")
                else:
                    song = query[index:]
                    data = song_credits(song)
                    artists = []
                    if data['tracks']['total'] == 0:
                        print("Song could not be found")
                        speak("Song could not be found")
                    else:
                        # print(data)
                        for i in range(len(data['tracks']['items'][0]['artists'])):
                            artists.append(data['tracks']['items']
                                           [0]['artists'][i]['name'])
                        if artists == 1:
                            print(
                                f'The artist who sang this song is {artists}')
                            speak(
                                f'The artist who sang this song is {artists}')
                        else:
                            print(
                                f'The artists who sang this song are {artists}')
                            speak(
                                f'The artists who sang this song are {artists}')
            except Exception as e:
                print("An error occured while fetching song data")
                speak("An error occured while fetching song data")
        elif ('internet' in query and 'speed' in query) or 'speed test' in query or 'speedtest' in query:
            speed_check()
        elif 'weather' in query or 'temperature' in query:
            if 'in' in query and query[query.find('in') + 2:query.find('in') + 3] == ' ':
                try:
                    city_name = query[query.find('in') + 3:]
                    api_key = config.api_key
                    base_url = 'http://api.openweathermap.org/data/2.5/weather?'
                    complete_url = base_url + "q=" + city_name + "&appid=" + api_key
                    response = requests.get(complete_url)
                    x = response.json()
                except Exception as e:
                    print("City could not be found")
                    speak("City could not be found")
                if x["cod"] == "404":
                    print('Please try again')
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
                    print(
                        f'The temperature is {temp}°C and it feels like {feel} °C\nThe low is {min_}°C and the high is {max_}°C\nThe predicted forecast is {description}')
                    speak(
                        f'The temperature is {temp} degrees celsius. It feels like {feel} degrees celsius. The low is {min_} degrees celsius and the high is {max_} degrees celsius. The predicted forecast is {description}')
            else:
                x = weather(latitude, longitude)
                if x == False:
                    print('Please try again')
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
                    print(
                        f'The temperature is {temp}°C and it feels like {feel} °C\nThe low is {min_}°C and the high is {max_}°C\nThe predicted forecast is {description}')
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
                        time = '' + str(delta) + sunset[minutes:]
                        print(f"The sun will fall at {time} pm today")
                        speak(f"The sun will fall at {time} pm today")
                    elif now < temp:
                        print(f"The sun will rise at {sunrise} am today")
                        speak(f"The sun will rise at {sunrise} am today")
        elif 'send' in query and 'email' in query:
            try:
                print('Who do you want to send the email to?')
                speak('Who do you want to send the email to?')
                # reciever = listen()
                reciever = input()
                print('What is the subject?')
                speak('What is the subject?')
                # subject = listen()
                subject = input()
                print('What is the message?')
                speak('What is the message?')
                # message = listen()
                message = input()
                print(
                    f'Send to : {reciever}\nSubject : {subject}\nMessage : {message}\nAre you sure you want to send the message?')
                speak(
                    f'Email is being sent to {reciever}. The subject is {subject}. The message says {message}. Are you sure you want to send the message?')
                # query = listen().lower()
                query = input()
                if 'yes' in query:
                    send_mail(subject, message, reciever)
                    print('Email successfully sent!')
                    speak('Email successfully sent!')
                else:
                    print('Cancelled!')
                    speak('Cancelled!')
            except Exception as e:
                print('An error occurred, email could not be sent!')
                speak('An error occurred, email could not be sent!')
        elif 'search' in query:
            query = query.replace('search ', '')
            if 'movie' in query or 'documentary' in query:
                try:
                    check = query.find(' movie')
                    if check == -1:
                        query = query.replace(' documentary', '')
                    else:
                        query = query.replace(' movie', '')
                    print(f'Searching for {query}...')
                    speak(f'Searching database for {query}')
                    moviesDB = imdb.IMDb()
                    movies = moviesDB.search_movie(query)
                    score = rotten_tomatoes_score(query)
                    id = movies[0].getID()
                    movie = moviesDB.get_movie(id)
                    title = movie['title']
                    year = movie['year']
                    rating = movie['rating']
                    directors = movie['directors']
                    casting = movie['cast']
                    this = ''
                    for i in range(8):
                        this += str(casting[i]) + ', '
                    if len(directors) != 1:
                        out = (f'Directed by {str(directors[0])} and ')
                        del directors[0]
                        for i in range(len(directors)):
                            if i != len(directors) - 1:
                                out += (f'{str(directors[i])} and ')
                            else:
                                out += (str(directors[i]))
                    else:
                        out = (f'Directed by : {str(directors[0])}')
                    print(
                        f'{title} ({year})\nIMDB - {rating}\nRotten Tomato - {score}')
                    print(out)
                    print(f'Cast includes : {this}')
                    speak(
                        f'{title} is a {year} movie with an IMDB rating of {rating} and a Rotten Tomato score of {score} {out}. Notable cast members include {this}')
                    print('Would you like to hear the synopsis?')
                    speak('Would you like to hear the synopsis?')
                    #query = listen().lower()
                    query = input()
                    keys = list(movie.keys())
                    if 'yes' in query:
                        if 'plot outline' not in keys:
                            synopsis = movie['plot'][0]
                        else:
                            synopsis = movie['plot outline']
                        print(synopsis)
                        speak(synopsis)
                except Exception as e:
                    print('Could not retrive movie title')
                    speak('Could not retrive movie title')
            elif 'actor' in query or 'actress' in query or 'producer' in query or 'writer' in query or 'director' in query:
                try:
                    check = {'actor': query.find('actor'), 'actress': query.find('actress'), 'producer': query.find(
                        'producer'), 'writer': query.find('writer'), 'director': query.find('director')}
                    keys = list(check.keys())
                    role = ''
                    for j in keys:
                        if check[j] != -1:
                            query = query.replace(f' {j}', '')
                            role = j
                            break
                    print(f'Searching for {query}...')
                    speak(f'Searching database for {query}')
                    peopleDB = imdb.IMDb()
                    people = peopleDB.search_person(query)
                    id = people[0].getID()
                    person = peopleDB.get_person(id)
                    name = person['name']
                    birth = person['birth date']
                    bio = str(person['mini biography'][0])
                    res = [i for i in range(
                        len(bio)) if bio.startswith('. ', i)]
                    for i in res:
                        if i >= 500:
                            bio = bio[0:i]
                            break
                    keys = list(person['filmography'][0].keys())
                    films = person['filmography'][0][keys[0]]
                    this = ''
                    for i in range(10):
                        this += str(films[i]) + ', '
                        this = this.replace(' ()', '')
                    print(f'{bio}\n{name} is known for {this}')
                    speak(f'{bio}\n{name} is known for {this}')
                except Exception as e:
                    print('Could not retrive requested information')
                    speak('Could not retrive requested information')
            elif 'series' in query or 'tv' in query:
                try:
                    check = query.find(' series')
                    if check == -1:
                        query = query.replace(' tv', '')
                    else:
                        query = query.replace(' series', '')
                    print(f'Searching for {query}...')
                    speak(f'Searching database for {query}')
                    seriesDB = imdb.IMDb()
                    score = rotten_tomatoes_score(query)
                    res = seriesDB.search_movie(query)
                    id = res[0].getID()
                    series = seriesDB.get_movie(id)
                    # seriesDB.update(series, 'episodes')
                    name = series['smart canonical title']
                    kind = series['kind']
                    length = series['series years']
                    keys = list(series.keys())
                    if 'seasons' in keys:
                        seasons = series['seasons']
                    else:
                        seasons = ''
                    # eps = series['number of episodes']
                    rating = series['rating']
                    if 'plot outline' not in keys:
                        synopsis = series['plot'][0]
                    else:
                        synopsis = series['plot outline']
                    casting = series['cast']
                    if seasons != '':
                        print(
                            f'{name} is a {kind} that has an IMDB rating of {rating} and a Rotten Tomato score of {score} with {seasons} seasons. The series has been ongoing from {length}')
                        speak(
                            f'{name} is a {kind} that has an IMDB rating of {rating} and a Rotten Tomato score of {score}with {seasons} seasons. The series has been ongoing from {length}')
                    else:
                        print(
                            f'{name} is a {kind} that has an IMDB rating of {rating} and a Rotten Tomato score of {score}. The series has been ongoing from {length}')
                        speak(
                            f'{name} is a {kind} that has an IMDB rating of {rating} and a Rotten Tomato score of {score}. The series has been ongoing from {length}')
                    this = ''
                    for i in range(8):
                        this += str(casting[i]) + ', '
                    print(f'Cast includes : {this}')
                    speak(f'Cast includes : {this}')
                    print('Would you like to hear the synopsis?')
                    speak('Would you like to hear the synopsis?')
                    #query = listen().lower()
                    query = input()
                    if 'yes' in query:
                        print(f'{synopsis}')
                        speak(synopsis)
                except Exception as e:
                    print('Could not retrive requested information')
                    speak('Could not retrive requested information')
            else:
                try:
                    client = wolframalpha.Client(config.app_id)
                    res = client.query(query)
                    output = next(res.results).text
                    print(output)
                    speak(output)
                except Exception as e:
                    print('An error occurred,could not search the internet')
                    speak('An error occurred,could not search the internet')
        elif 'score' in query:
            try:
                result = []
                query = query.replace(' score', '')
                all_matches = sports.all_matches()
                keys = list(all_matches.keys())
                for j in range(len(keys)):
                    temp = all_matches[keys[j]]
                    matches = []
                    for i in range(len(temp)):
                        matches.append((str(temp[i])).lower())
                    for text in matches:
                        if query in text:
                            result.append(True)
                            print(
                                f'{keys[j]} : The last updated score was {text}')
                            speak(
                                f'The last updated score was {text} : {keys[j]}')
                        else:
                            result.append(False)
                if True not in result:
                    print('Could not retrieve game scores')
                    speak('Could not retrieve game scores')
            except Exception as e:
                print('An error occurred, please try again')
                speak('An error occurred, please try again')
        elif 'define' in query:
            try:
                query = query.replace('define ', '')
                definition = fetch_definition(query)
                print('Fetching...')
                speak('Fetching')
                keys = list(definition.keys())
                if len(keys) > 1:
                    print(f'There are {len(keys)} definitions')
                    speak(f'There are {len(keys)} definitions')
                    for i in range(len(keys)):
                        if len(definition[keys[i]]) > 1:
                            for j in range(1):
                                print(f'{keys[i]} : {definition[keys[i]][j]}')
                                speak(f'{keys[i]} : {definition[keys[i]][j]}')
                        else:
                            print(f'{keys[i]} : {definition[keys[i]]}')
                            speak(f'{keys[i]} : {definition[keys[i]]}')
                else:
                    if len(definition[keys[0]]) > 1:
                        for j in range(1):
                            print(f'{keys[0]} : {definition[keys[0]][j]}')
                            speak(f'{keys[0]} : {definition[keys[0]][j]}')
                    else:
                        print(f'{keys[0]} : {definition[keys[0]]}')
                        speak(f'{keys[0]} : {definition[keys[0]]}')
            except Exception as e:
                print('An error occured while fetching word definition')
                speak('An error occured while fetching word definition')
        elif 'synonym' in query:
            try:
                dictionary = PyDictionary()
                query = query.replace(' synonym', '')
                print(
                    f'The synonyms for {query} are : {dictionary.synonym(query)}')
                speak(
                    f'The synonyms for {query} are : {dictionary.synonym(query)}')
            except Exception as e:
                print('Synonyms could not be retrieved')
                speak('synonyms could not be retrieved')
        elif 'antonym' in query:
            try:
                dictionary = PyDictionary()
                query = query.replace(' antonym', '')
                print(
                    f'The antonyms for {query} are : {dictionary.antonym(query)}')
                speak(
                    f'The antonyms for {query} are : {dictionary.antonym(query)}')
            except Exception as e:
                print('Antonyms could not be retrieved')
                speak('antonyms could not be retrieved')
        elif 'translate':
            word = query.replace('translate ','')
            print('What language would you like to translate to?')
            speak('What language would you like to translate to?')
            # query = listen().lower()
            query = input('Language : ')
            codes = {'Amharic': 'am', 'Arabic': 'ar', 'Basque': 'eu', 'Bengali': 'bn', 'English (UK)': 'en-GB', 'Portuguese (Brazil)': 'pt-BR', 'Bulgarian': 'bg', 'Catalan': 'ca', 'Cherokee': 'chr', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English (US)': 'en', 'Estonian': 'et', 'Filipino': 'fil', 'Finnish': 'fi', 'French': 'fr', 'German': 'de', 'Greek': 'el', 'Gujarati': 'gu', 'Hebrew': 'iw', 'Hindi': 'hi', 'Hungarian': 'hu', 'Icelandic': 'is', 'Indonesian': 'id', 'Italian': 'it', 'Japanese': 'ja',
                     'Kannada': 'kn', 'Korean': 'ko', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Malay': 'ms', 'Malayalam': 'ml', 'Marathi': 'mr', 'Norwegian': 'no', 'Polish': 'pl', 'Portuguese (Portugal)': 'pt-PT', 'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr', 'Chinese (PRC)': 'zh-CN', 'Slovak': 'sk', 'Slovenian': 'sl', 'Spanish': 'es', 'Swahili': 'sw', 'Swedish': 'sv', 'Tamil': 'ta', 'Telugu': 'te', 'Thai': 'th', 'Chinese (Taiwan)': 'zh-TW', 'Turkish': 'tr', 'Urdu': 'ur', 'Ukrainian': 'uk', 'Vietnamese': 'vi', 'Welsh': 'cy'}
            keys = list(codes.keys())
            values = list(codes.values())
            location = -1
            for i in range(len(codes)):
                if query.lower() == keys[i].lower() or query.lower() == values[i].lower():
                    location = i
            if location == -1:
                print('Language entered is not supported')
                speak('Language is not supported')
            else:
                print(f'{word} translated to {keys[location]} is {PyDictionary(query).translateTo(values[i])}')
                speak(f'{word} translated to {keys[location]} is {PyDictionary(query).translateTo(values[i])}')
        elif "my name" in query:
            print('Zaki')
            speak('Zaki')
        elif 'the time' in query:
            time = datetime.datetime.now().strftime("%H:%M")
            now = int(datetime.datetime.now().hour)
            if now < 12:
                print(f"It is {time} am now")
                speak(f"It is {time} am now")
            else:
                if now > 12:
                    now = now - 12
                minutes = int(datetime.datetime.now().minute)
                print(f"It is {now}:{minutes} pm now")
                speak(f"It is {now}:{minutes} pm now")
        elif ('hey' in query and query[query.find('hey') + 3:query.find('hey') + 4] == '' or query[query.find('hey') + 3:query.find('hey') + 4] == ' ') or ('hi' in query and query[query.find('hi') + 2:query.find('hi') + 3] == '' or query[query.find('hi') + 2:query.find('hi') + 3] == ' ') or ('hello' in query and query[query.find('hello') + 5:query.find('hello') + 6] == '' or query[query.find('hello') + 5:query.find('hello') + 6] == ' '):
            print('Hey there')
            speak('Hey there!')
        elif ('stop' in query and query[query.find('stop') + 4:query.find('stop') + 5] == '') or ('thank you' in query and query[query.find('thank you') + 9:query.find('thank you') + 10] == ''):
            print('Have a wonderful day!')
            speak('Have a wonderful day!')
            break
