from pymongo import MongoClient
import pprint # not really necessary because we're using beautiful soup

import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

# Requests sends and recieves HTTP requests.
import requests

# Beautiful Soup parses HTML documents in python.
from bs4 import BeautifulSoup

import json
import time
import copy 
from bson import ObjectId
import pprint

import praw
from pymongo import MongoClient
import datetime
import pymongo
import datetime
import configparser


# Read Scraper and Reddit Bot Configuration
# See https://github.com/reddit-archive/reddit/wiki/API
#
config = configparser.ConfigParser()
config.read('scrape.config')
version = config['reddit']['version']
appname = config['reddit']['appname']
client_id = config['reddit']['client_id']
client_secret = config['reddit']['client_secret']
password = config['reddit']['password']
username = config['reddit']['username']
platform = config['reddit']['platform']
user_agent = f'{platform}:{appname}:version={version} (script by {username})'


# Connect to the database
#
client = MongoClient('localhost', 27017)
db = client[f'{appname}db']
wsb_submissions = db['wsb_submissions']
wsb_submissions.create_index([('created_utc', pymongo.DESCENDING), ('id', pymongo.DESCENDING), ('author',1)], unique=True)


# Connect to reddit
# https://praw.readthedocs.io/en/latest/getting_started/authentication.html
#
reddit = praw.Reddit(
    client_id = client_id,
    client_secret = client_secret,
    password = password,
    user_agent = user_agent,
    username = username
)
print(reddit.user.me())


# Pick our subreddit
#
wsb = reddit.subreddit('wallstreetbets')

def submission_to_dict(sub):
    '''
    Converts a PRAW submission object to a dictionary suitable for insertion
    into mongodb

    Parameters
    ----------
    sub -- PRAW submission object

    ReturnsReturns
    -------
    Dictionary of a reddit submission
    '''
    dct = dict()
    dct['id'] = sub.id
    dct['fullname'] = sub.fullname
    dct['selftext'] = sub.selftext
    dct['created_utc'] = str(datetime.datetime.fromtimestamp(sub.created_utc))
    dct['num_comments'] = sub.num_comments
    dct['score'] = sub.score
    dct['upvote_ratio'] = sub.upvote_ratio
    dct['is_original_content'] = sub.is_original_content
    dct['permalink'] = sub.permalink
    dct['title'] = sub.title
    dct['author'] = str(sub.author)
    dct['firstseen'] = str(datetime.datetime.utcnow())
    return dct

def insert_sub(collection, sub):
    '''
    Inserts a dictionary-formatted submission into a mongodb

    Parameters
    ----------
    collection -- mongodb collection to store the submission
    sub -- dictionary-formatted submission

    Returns
    -------
    1 -- if successful
    0 -- if not
    '''
    try:
        collection.insert_one(submission_to_dict(sub))
        return 1
    except:
        return 0

def get_new_submissions(limit=100):
    '''
    Query reddit API and insert new submissions into mongodb

    Parameters
    ----------
    limit -- the number of submissions to query, default is 100
             None will attempt to pull up to 1,000
    '''
    num_new = 0
    num_total = 0
    for submission in wsb.new(limit=limit):
        num_new += insert_sub(wsb_submissions, submission)
        num_total += 1
    fract = round(num_new / num_total * 100,0)
    print(f'Found {num_new} new submissions out of {num_total}, {fract}%')

get_new_submissions(500)