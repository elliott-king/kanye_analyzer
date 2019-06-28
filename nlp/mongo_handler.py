from collections import defaultdict
from pymongo import MongoClient
from bson.son import SON

import constants
import pymongo
import pprint
import operator
import nltk # natural language toolkit
import time

client = MongoClient()

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
    comments = client[constants.DB_KANYE][constants.COMMENTS]
    comment = comments.find_one({'name': comment_name})
    if not comment:
        raise ValueError('Could not find comment for name:', comment_name)
    comment = short_comment(comment) if pretty else comment
    return comment

# gets <limit> most recent comments.
def get_recent_comments(limit=10, pretty=True):
    comments = client[constants.DB_KANYE][constants.COMMENTS]
    ret = []
    for comment in comments.find().sort('created_utc', pymongo.DESCENDING).limit(limit):
        ret.append(comment if not pretty else short_comment(comment))
    return ret

### The following handle comment categories

def is_updated(comment_name):
    categories = client[constants.DB_KANYE][constants.TRAIN_CATEGORIES]
    comment = categories.find_one({'name': comment_name})
    return bool(comment)

def update_comment_category(comment_name, category=None, is_wavy=None):
    categories = client[constants.DB_KANYE][constants.TRAIN_CATEGORIES]
    # TODO: compress into one statement?
    # TODO: make this ACID compliant (both should fail or succeed together)
    # TODO: verify that category & is_wavy are correct.
    if category:
        categories.find_one_and_update(
                {'name': comment_name},
                {'$set': {constants.CATEGORY: category}},
                upsert=True)
    if is_wavy:
        categories.find_one_and_update(
                {'name': comment_name},
                {'$set': {constants.POSITIVITY: is_wavy}},
                upsert=True)

# returns command cursor
def get_noncategorized_comments(limit=10):
    comments = client[constants.DB_KANYE][constants.COMMENTS]
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
def get_categorized_classified_comments():
    categories = client[constants.DB_KANYE][constants.TRAIN_CATEGORIES]
    return categories.find({constants.CATEGORY: {'$exists': True}})

def get_positivity_classified_comments():
    categories = client[constants.DB_KANYE][constants.TRAIN_CATEGORIES]
    return categories.find({constants.POSITIVITY: {'$exists': True}})

def update_user_classification(comment_name, classification):
    user_classified = client[constants.DB_KANYE][constants.USER_CLASSIFIED]
    doc = user_classified.find_one({'name': comment_name})
    if doc:
        if constants.POSITIVITY in classification:
            user_classified.find_one_and_update(
                {'name': comment_name}, 
                {'$inc': { constants.POSITIVITY + '.' + classification[constants.POSITIVITY] : 1 } }
            )

        if constants.CATEGORY in classification:
            user_classified.find_one_and_update(
                {'name': comment_name}, 
                {'$inc': { constants.CATEGORY + '.' + classification[constants.CATEGORY] : 1 } }
            )
    else:
        doc = { 
            'name': comment_name,
            constants.POSITIVITY: {},
            constants.CATEGORY: {}
        }
        for key in constants.POSITIVITY_TEXT:
            doc[constants.POSITIVITY][key] = 0
        for key in constants.CATEGORIES_TEXT:
            doc[constants.CATEGORY][key] = 0

        if constants.POSITIVITY in classification:
            doc[constants.POSITIVITY][classification[constants.POSITIVITY]] += 1
        if constants.CATEGORY in classification:
            doc[constants.CATEGORY][classification[constants.CATEGORY]] += 1

        user_classified.insert_one(doc).acknowledged

def get_single_comment_classification_totals(comment_name):
    user_classified = client[constants.DB_KANYE][constants.USER_CLASSIFIED]
    totals =  user_classified.find_one({'name': comment_name})
    if not totals: 
        raise ValueError('Comment ' + comment_name + ' has not been classified by a user.')
    return totals

def get_single_user_classification(comment_name):
    totals = get_single_comment_classification_totals(comment_name)
    comment = { 'name': comment_name }
    
    # Not gonna worry about ties.
    # Finding key for max value taken from:
    # https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
    positivity = max(totals[constants.POSITIVITY].items(), key=operator.itemgetter(1))[0]
    category = max(totals[constants.CATEGORY].items(), key=operator.itemgetter(1))[0]

    if totals[constants.POSITIVITY][positivity] > 0:
        comment[constants.POSITIVITY] = positivity
    if totals[constants.CATEGORY][category] > 0:
        comment[constants.CATEGORY] = category

    return comment

# Much copy paste. Wow reuse code. Def refactor.
# Returns list of comments with their category and positivity (if they exist)
def get_all_user_classified_comments():
    user_classified = client[constants.DB_KANYE][constants.USER_CLASSIFIED]
    user_classified_totals = user_classified.find({})

    ret = []
    for totals in user_classified_totals:
        comment = { 'name': totals['name'] }
        
        # Not gonna worry about ties.
        # Finding key for max value taken from:
        # https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
        positivity = max(totals[constants.POSITIVITY].items(), key=operator.itemgetter(1))[0]
        category = max(totals[constants.CATEGORY].items(), key=operator.itemgetter(1))[0]

        if totals[constants.POSITIVITY][positivity] > 0:
            comment[constants.POSITIVITY] = positivity
        if totals[constants.CATEGORY][category] > 0:
            comment[constants.CATEGORY] = category
        ret.append(comment)

    print("Applied user classification to", len(ret), "comments")
    return ret

# NOTE: if a user refers to an external object, we are considering it external 
# (even if the user is sort of referring to the link)
def get_link_comments():
    categories = client[constants.DB_KANYE][constants.TRAIN_CATEGORIES]
    cursor = categories.find({"category": "link"})
    return cursor

def _combine_official_and_user_classified_comments(function, field):
    pairs = []
    used_names = set() # In case the users classify a comment that I did myself.

    # comments that I have classified
    cursor = function()
    for classified_comment in cursor:
        full_comment = get_comment(classified_comment['name'], pretty=False)
        pairs.append((full_comment, classified_comment[field]))
        used_names.add(classified_comment['name'])

    # Comments that users have classified.
    user_classified = get_all_user_classified_comments()
    for user_classified_comment in user_classified:
    # A labeled comment may not always be labeled for both 'is_wavy' and 'category'
        if field in user_classified_comment and user_classified_comment['name'] not in used_names:
            full_comment = get_comment(user_classified_comment ['name'], pretty=False)
            pairs.append((full_comment, user_classified_comment[field]))
            used_names.add(user_classified_comment['name'])
    
    return pairs

def get_count(category):
    categories = client[constants.DB_KANYE][constants.TRAIN_CATEGORIES]
    return categories.find({"category": category}).count()

# Maps each category to (total, pct) comments in that category.
def categories_counts():
    count = defaultdict(int)
    used_names =  set()
    total = 0

    categorized_comments = get_categorized_classified_comments()
    user_classified_comments = get_all_user_classified_comments()

    for comment in categorized_comments:
        count[comment[constants.CATEGORY]] += 1
        used_names.add(comment['name'])
        total += 1
    
    for comment in user_classified_comments:
        if constants.CATEGORY in comment and comment['name'] not in used_names:
            count[comment[constants.CATEGORY]] += 1
            total += 1
    
    for category in count:
        val = count[category]
        count[category] = (val, int(float(val)/float(total) * 100))
    return count

def classified_comments_with_category():
    return _combine_official_and_user_classified_comments(get_categorized_classified_comments, constants.CATEGORY)

def classified_comments_with_positivity():
    return _combine_official_and_user_classified_comments(get_positivity_classified_comments, constants.POSITIVITY)

if __name__ == "__main__":
    pprint.pprint(get_recent_comments())
