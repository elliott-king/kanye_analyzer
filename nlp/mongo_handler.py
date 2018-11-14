from pymongo import MongoClient
import pymongo
import pprint
import nltk # natural language toolkit
import time

client = MongoClient()
db = client.kanye
comments = db['wavy-comments']
categories = db['wavy-categories']

def short_comment(comment):
    ret = {}
    ret['author'] = comment['author']
    ret['name'] = comment['name']
    ret['created_utc'] = comment['created_utc']
    # TODO: limit to fewer characters
    # TODO: limit to only relevant sentence
    ret['body'] = comment['body']
    return ret

def body_only(comment):
    return comment['body']

def get_comment(comment_name, pretty=True):
    comment = comments.find_one({'name': comment_name})
    comment = short_comment(comment) if pretty else comment
    return comment

def get_recent_comments(limit=10, pretty=True):
    # print("Current epoch time: " + str(int(time.time())))
    ret = []
    cursor = comments.find().sort('created_utc', pymongo.DESCENDING).limit(limit)
    for comment in comments.find().sort('created_utc', pymongo.DESCENDING).limit(limit):
        ret.append(comment if not pretty else short_comment(comment))
    return ret

### Following handle comment categories

def is_updated(comment_name):
    comment = categories.find_one({'name': comment_name})
    return bool(comment)

def update_comment_category(comment_name, category, features):
    # TODO: should overwrite old one
    categories.find_one_and_update(
            {'name': comment_name},
            {
                'name': comment_name,
                'category': category,
                'features': features
            },
            upsert=True)


if __name__ == "__main__":
    pprint.pprint(get_recent_comments())
