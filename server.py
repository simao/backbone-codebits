# -*- coding: utf-8; -*-
import bottle
import tweepy
import logging
import json
import time
import yaml

from bottle import response, route, static_file

LOG_FORMAT = '[%(levelname).1s] [%(asctime)s] [%(name)s] %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

twitter_config = {}

def init_server():
    global twitter_config
    config = yaml.load(open('config.yaml'))
    twitter_config.update(config['twitter'])
init_server()


def get_new_access_token():
    auth = tweepy.OAuthHandler(twitter_config['consumer_key'], twitter_config['consumer_secret'])
    auth_url = auth.get_authorization_url()
    print 'Please authorize: ' + auth_url
    verifier = raw_input('PIN: ').strip()
    auth.get_access_token(verifier)
    print "ACCESS_KEY = '%s'" % auth.access_token.key
    print "ACCESS_SECRET = '%s'" % auth.access_token.secret


def get_results_for(t_client, search_q):
    """
    # will be added to the search query
    """
    results = t_client.search(q="#"+search_q)

    # This can be refactored
    return [
        {
            "author": "@%s" % t.from_user,
            "text": t.text,
            "id": t.id,
            "date_h": t.created_at.strftime("%H:%M:%S %d/%m/%Y"),
            "date": time.mktime(t.created_at.timetuple()),
        } for t in results
    ]



@route("/tweets/:query/:id")
def get_tweet(query, id):
    if int(id) == 42:
        return {
            "author": "@batráquio",
            "text": "KEEP CALM",
            "id": 42,
            "date_h": "",
            "date": "",
            }
    
    t = get_client().get_status(id)
    
    tweet = {
        "author": "@%s" % t.user.screen_name,
        "text": t.text,
        "id": t.id,
        "date_h": t.created_at.strftime("%H:%M:%S %d/%m/%Y"),
        "date": time.mktime(t.created_at.timetuple()),
    } 
    
    response.content_type = 'text/javascript; charset=utf8'
    return json.dumps(tweet, ensure_ascii=False, indent=4)

    
@route("/tweets/:query")
def get_tweets(query):
    tweets = get_results_for(get_client(), query)
    response.content_type = 'text/javascript; charset=utf8'
    return json.dumps(tweets, ensure_ascii=False, indent=4)
    

@route('/:path#.*#')
def server_static(path):
    if not path:
        path = "index.html"
    return static_file(path, root='./')

def make_client():
    cache = dict(api=None)
    log = logging.getLogger(__name__)

    def get_client():
        if cache["api"]:
            log.info("Returning twitter client from cache")
            return cache["api"]
        log.info("Creating new twitter client")
        auth = tweepy.OAuthHandler(twitter_config['consumer_key'], twitter_config['consumer_secret'])
        auth.set_access_token(twitter_config['access_key'], twitter_config['access_secret'])
        api = tweepy.API(auth)
        cache["api"] = api
        return api

    return get_client
    
get_client = make_client()
    



if __name__ == '__main__':
    log = logging.getLogger(__name__)

    bottle.debug()
    bottle.run(server="paste", reloader=True, host='localhost', port=9999)
