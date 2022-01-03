import json
import logging
import requests
import re
import time
from datetime import date
from twython import Twython
from bs4 import BeautifulSoup

# not uploading to github for obvious security reasons
from auth import (
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_SECRET,
    AI_API_KEY
    )

logging.basicConfig(filename='tweetbot.log', level=logging.INFO)

def get_word_of_the_day():
    res = requests.get('https://www.dictionary.com/e/word-of-the-day/')
    soup = BeautifulSoup(res.text,'html.parser')

    article_title = soup.title.string
    #print('article title:', article_title)

    res = re.findall('\- ([^$]*) \|', article_title)
    wotd= ''

    for character in res:
        if character.isalnum():
            wotd += character

    return wotd

def get_ai_image(wotd, api_key):
    r = requests.post(
    "https://api.deepai.org/api/text2img",
    data={
        'text':wotd,
        },
    headers={'api-key':api_key}
    )

    response = r.json()
    response = response['output_url']

    myfile = requests.get(response).content
    with open('output.jpg', 'wb') as handler:
        handler.write(myfile)
    
    return myfile

def post_tweet(image, todays_word):
    twitter = Twython(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_SECRET
        )
    
    message = "word of the day: " + todays_word
    post_media = open('output.jpg', 'rb')
    res = twitter.upload_media(media=post_media)
    media_id = [res['media_id']]

    logging.info('updating status')
    logging.info(message)
    logging.info('twitter media id:' + str(media_id))
    logging.info('date: ' + str(time.asctime()))
    
    try:
        #twitter.update_status(status=message, media_ids=media_id)
        logging.info("Update successful.")
    except:
        logging.info("failed to update status.. connection issues?")
              
if __name__ == "__main__":
    logging.info('---------------------------')
    logging.info('starting log')
    WOTD = get_word_of_the_day()
    AI_IMAGE = get_ai_image(WOTD, AI_API_KEY)
    post_tweet(AI_IMAGE, WOTD)
    logging.info('ending log')
    logging.info('---------------------------')
