from pymongo import MongoClient
from bson.son import SON
import constants
import pymongo
import pprint
import nltk # natural language toolkit
import time

client = MongoClient()
db = client.kanye
comments = db[constants.COMMENTS]
categories = db[constants.TRAIN_CATEGORIES]

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
    if not comment:
        raise ValueError('Could not find comment for name:', comment_name)
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

def update_comment_category(comment_name, category=None, is_wavy=None):
    # TODO: compress into one statement?
    # TODO: make this ACID compliant (both should fail or succeed together)
    if category:
        categories.find_one_and_update(
                {'name': comment_name},
                {'$set': {'category': category}},
                upsert=True)
    if is_wavy:
        categories.find_one_and_update(
                {'name': comment_name},
                {'$set': {'is_wavy': is_wavy}},
                upsert=True)

# returns command cursor
def get_noncategorized_comments(limit=10):
    # join logic taken from: https://stackoverflow.com/questions/8772936
    pipeline = [
        {'$lookup' : {
            'from': constants.TRAIN_CATEGORIES,
            'localField': 'name',
            'foreignField': 'name',
            'as': 'matched_docs',
        }},
        {'$match': {'matched_docs': {'$eq': []}}},
        {'$sort': SON([('created_utc', -1)])},
        {'$limit': limit}
    ]
    command_cursor = comments.aggregate(pipeline)
    return command_cursor

# all categorized comments, and their categories
def get_categorized_comments():
    return categories.find({})
#    pipeline = [
#            {'$lookup': {
#                'from': constants.TRAIN_CATEGORIES,
#                'localField': 'name',
#                'foreignField': 'name',
#                'as': 'matched_docs',
#            }}
#    ]
#    command_cursor = comments.aggregate(pipeline)
#    return command_cursor

def get_positivity_categorized_comments():
    return categories.find({'is_wavy': {'$exists': True}})

# NOTE: if a user refers to an external object, we are considering it external 
# (even if the user is sort of referring to the link)
def get_link_comments():
    cursor = categories.find({"category": "link"})
    return cursor

def get_count(category):
    return categories.find({"category": category}).count()

def categories_counts():
    metrics = {}
    running_sum = 0
    for category in constants.CATEGORIES:
        count = get_count(category)
        metrics[category] = count
        running_sum += count
    
    for category in metrics:
        val = metrics[category]
        metrics[category] = (val, int(float(val)/float(running_sum) * 100))
    return metrics
        

if __name__ == "__main__":
    pprint.pprint(get_recent_comments())
