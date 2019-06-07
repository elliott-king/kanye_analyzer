from pymongo import MongoClient
from bson.son import SON
import constants
import pymongo
import pprint
import nltk # natural language toolkit
import time

client = MongoClient()
DB_KANYE = 'kanye'
DB_TEST = 'test'

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

def get_comment(comment_name, pretty=True, db=DB_KANYE):
    comments = client[db][constants.COMMENTS]
    comment = comments.find_one({'name': comment_name})
    if not comment:
        raise ValueError('Could not find comment for name:', comment_name)
    comment = short_comment(comment) if pretty else comment
    return comment

# gets <limit> most recent comments.
def get_recent_comments(limit=10, pretty=True, db=DB_KANYE):
    comments = client[db][constants.COMMENTS]
    ret = []
    for comment in comments.find().sort('created_utc', pymongo.DESCENDING).limit(limit):
        ret.append(comment if not pretty else short_comment(comment))
    return ret

### The following handle comment categories

def is_updated(comment_name, db=DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    comment = categories.find_one({'name': comment_name})
    return bool(comment)

def update_comment_category(comment_name, category=None, is_wavy=None, db=DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    # TODO: compress into one statement?
    # TODO: make this ACID compliant (both should fail or succeed together)
    # TODO: verify that category & is_wavy are correct.
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
def get_noncategorized_comments(limit=10, db=DB_KANYE):
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
def get_categorized_comments(db=DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    return categories.find({'category': {'$exists': True}})

def get_positivity_categorized_comments(db=DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    return categories.find({'is_wavy': {'$exists': True}})

def identify_most_common_user_classification(all_user_input):

    user_categorized_comments = {}
    # First retrieve user input, and map the total inputs to each individual comment
    for user_input in all_user_input:
        if user_input['name'] not in user_categorized_comments:
            user_categorized_comments[user_input['name']] = {
                'is_wavy': [],
                'category': [],
            }

        user_categorized_comments[user_input['name']]['is_wavy'].append(user_input.get('is_wavy'))
        user_categorized_comments[user_input['name']]['category'].append(user_input.get('category'))

    # Find the mode (most frequent) of each classification for each comment.
    ret = []
    for comment_name in user_categorized_comments:
        comment = {'name': comment_name}
        if 'is_wavy' in user_categorized_comments[comment_name]:
            w =  max(user_categorized_comments[comment_name]['is_wavy'], key=user_categorized_comments[comment_name]['is_wavy'].count)
            if w:
                comment['is_wavy'] = w
        if 'category' in user_categorized_comments[comment_name]:
            w =  max(user_categorized_comments[comment_name]['category'], key=user_categorized_comments[comment_name]['category'].count)
            if w:
                comment['category'] = w
        ret.append(comment)
    
    return ret


def get_user_categorized_comments(db=DB_KANYE):
    user_classified = client[db][constants.USER_CLASSIFIED]
    all_user_input = user_classified.find({'category': {'$exists': True}})
    return identify_most_common_user_classification(all_user_input)

def get_user_positivity_categorized_comments(db=DB_KANYE):
    user_classified = client[db][constants.USER_CLASSIFIED]
    all_user_input = user_classified.find({'is_wavy': {'$exists': True}})
    return identify_most_common_user_classification(all_user_input)


# NOTE: if a user refers to an external object, we are considering it external 
# (even if the user is sort of referring to the link)
def get_link_comments(db=DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    cursor = categories.find({"category": "link"})
    return cursor

def get_count(category, db=DB_KANYE):
    categories = client[db][constants.TRAIN_CATEGORIES]
    return categories.find({"category": category}).count()

def categories_counts(db=DB_KANYE):
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
