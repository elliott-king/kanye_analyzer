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

def get_comment(comment_name, pretty=True, db=constants.DB_KANYE):
    comments = client[db][constants.COMMENTS]
    comment = comments.find_one({'name': comment_name})
    if not comment:
        raise ValueError('Could not find comment for name:', comment_name)
    comment = short_comment(comment) if pretty else comment
    return comment

# gets <limit> most recent comments.
def get_recent_comments(limit=10, pretty=True, db=constants.DB_KANYE):
    comments = client[db][constants.COMMENTS]
    ret = []
    for comment in comments.find().sort('created_utc', pymongo.DESCENDING).limit(limit):
        ret.append(comment if not pretty else short_comment(comment))
    return ret

### The following handle comment categories

def is_updated(comment_name, db=constants.DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    comment = categories.find_one({'name': comment_name})
    return bool(comment)

def update_comment_category(comment_name, category=None, is_wavy=None, db=constants.DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
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
def get_noncategorized_comments(limit=10, db=constants.DB_KANYE):
    comments = client[db][constants.COMMENTS]
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
def get_categorized_classified_comments(db=constants.DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    return categories.find({constants.CATEGORY: {'$exists': True}})

def get_positivity_classified_comments(db=constants.DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    return categories.find({constants.POSITIVITY: {'$exists': True}})

def update_user_classification(comment_name, classification, db=constants.DB_KANYE):
    user_classified = client[db][constants.USER_CLASSIFIED]
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

def get_single_comment_classification_totals(comment_name, db=constants.DB_KANYE):
    user_classified = client[db][constants.USER_CLASSIFIED]
    totals =  user_classified.find_one({'name': comment_name})
    if not totals: 
        raise ValueError('Comment ' + comment_name + ' has not been classified by a user.')
    return totals

def get_single_user_classification(comment_name, db=constants.DB_KANYE):
    totals = get_single_comment_classification_totals(comment_name, db=db)
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
def get_all_user_classified_comments(db=constants.DB_KANYE):
    user_classified = client[db][constants.USER_CLASSIFIED]
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

    return ret

# NOTE: if a user refers to an external object, we are considering it external 
# (even if the user is sort of referring to the link)
def get_link_comments(db=constants.DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    cursor = categories.find({"category": "link"})
    return cursor

def get_count(category, db=constants.DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    return categories.find({"category": category}).count()

def categories_counts(db=constants.DB_KANYE):
    metrics = {}
    running_sum = 0
    for category in constants.CATEGORIES_TEXT:
        count = get_count(category, db=db)
        metrics[category] = count
        running_sum += count
    
    for category in metrics:
        val = metrics[category]
        metrics[category] = (val, int(float(val)/float(running_sum) * 100))
    return metrics
        

if __name__ == "__main__":
    pprint.pprint(get_recent_comments())
