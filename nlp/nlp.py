import nltk
import mongo_handler
import constants
import pprint

# Taken from nltk book:
# http://www.nltk.org/book/ch05.html



# tokenize string:           nltk.word_tokenize(s)
# show part of speech (pos): nltk.pos_tag(tokenized_string)
# view documentation of tag: nltk.help.upenn_tagset('TOKEN_NAME')


# TODO: identify dialogue act types: section 6.2.2
# TODO: how does pos_tag work? Is it a dict, or does it refer to the order of the tokens?


# Comment useful values:
# author, body, created, created_utc, parent_id, is_submitter
# name, id (identifier, identifier with t1_ prefix)
# permalink (does not include reddit.com)
# link_id, link_permalink (overall thread id & permalink, includes reddit.com)

def get_features(comment):
    body = comment['body']
    tokens = nltk.word_tokenize(body)
    tagged = nltk.pos_tag(tokens) # list of tuples
    # https://stackoverflow.com/questions/48660547
    entities = nltk.chunk.ne_chunk(tagged) 

    features = {}
    features['length'] = len(tokens) # TODO: also counts punctuation
    features['top_level_comment'] = comment['link_id'] == comment['parent_id']
    features['is_submitter'] = comment['is_submitter']
    features['num_ne'] = 0 # number of named entities
    for word in tokens:
        # mongo cannot handle 'contains(.)', or anything with a period, as a field
        if '.' not in word:
            features['contains ({})'.format(word.lower())] = True

    for chunk in entities:
        if hasattr(chunk, 'label'):
            features['num_ne'] += 1
    features['ne_ratio'] = features['num_ne'] / len(tokens)
    # TODO: use number of distinct words
    # TODO: consider also using neighbor words around 'wavy'

    return features

# generate train data by hand
if __name__ == '__main__':

    categories = constants.CATEGORIES
    positivity_options = constants.POSITIVITY

    command_cursor = mongo_handler.get_noncategorized_comments(limit=100)
    for comment in command_cursor:
        s = '\nThe categories are:\n' + '\n'.join(
                ['{}: {}'.format(i, v) for i, v in enumerate(categories)])
        print(s + '\n')
        features = get_features(comment)
        features_no_contains = {}
        for feature in features:
            if 'contains' not in feature:
                features_no_contains[feature] = features[feature]
        print('==============================================================')
        print(comment['body'])
        print('Created (utc): ', comment['created_utc'])
        print('Fullname:', comment['name'])
        print('link: ' +  'reddit.com' + comment ['permalink'])
        pprint.pprint(features_no_contains)
        category = input('Category? ')
        while not category or int(category) >= len(categories) or int(category) < 0:
            print(
                    'Invalid category selection.', 
                    'Please use a number between 0 and', 
                    len(categories) - 1)
            category = input('Category? ')

        print('Category chosen:', categories[int(category)])
        name = comment['name']
        category = categories[int(category)]

        p = '\nThe positivity options are:\n' + '\n'.join(
                ['{}: {}'.format(i, v) for i, v in enumerate(positivity_options)])
        print(p)
        positivity = input('Positivity? ')
        while (not positivity 
               or int(positivity) >= len(positivity_options) 
               or int(positivity) < 0):
            print(
                    'Invalid category selection.', 
                    'Please use a number between 0 and', 
                    len(positivity_options) - 1)
            positivity = input('Positivity?')
        print('This comment is:', positivity_options[int(positivity)])
        positivity = positivity_options[int(positivity)]

        mongo_handler.update_comment_category(name, category=category, 
                feature_dict=features, is_wavy=positivity)

