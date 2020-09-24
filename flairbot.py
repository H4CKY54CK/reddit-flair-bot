import re
import sys
import json
import praw
import time
from urllib.request import urlopen
import logging

logging.basicConfig(format="(%(levelname)s) %(asctime)s: %(message)s", filename='/home/hacky/flairbot/userflairs.log', level=logging.INFO, datefmt="%D %r")

URL = 'https://raw.githubusercontent.com/H4CKY54CK/flair-selector/master/flairs.json'

def match(strg, search=re.compile(r'[^a-zA-Z0-9-_]').search):
    return not bool(search(strg))

def start():
    reddit = praw.Reddit('flairbot')
    subreddit = reddit.subreddit(reddit.config.custom['subreddit'])
    flairs = json.loads(urlopen(URL).read())
    marker = time.time()
    try:
        for msg in reddit.inbox.stream(pause_after=0):
            if time.time() - marker > 300:
                try:
                    flairs = json.loads(urlopen(URL).read())
                except Exception:
                    logging.warning("Failed to fetch flair data from Github repo. Continuing with old flair data. (Most likely a connection error. Occasionally, fine. If this happens a lot, then there's a problem.)")
                marker = time.time()
            if msg is None:
                continue
            author = msg.author.name
            valid_user = match(author)
            if msg.subject == 'flair' and valid_user:
                content = msg.body.split(',', 1)
                flair_id = content[0]
                if flair_id in flairs:
                    flair = flairs[flair_id]
                    addon = f":{flair}:"
                    ftext = addon
                    if len(content) > 1:
                        text = content[1].strip()
                        ftext = f"{addon}{text}" if len(addon) + len(text) <= 64 else text
                    subreddit.flair.set(author, ftext, flair)
                    msg.mark_read()
                    logging.info(f"User: {author} | Text: {ftext} | Flair: {flair}")
    except Exception:
        logging.warning(f"{sys.exc_info()}")

if __name__ == '__main__':
    start()
