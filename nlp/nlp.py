import emoji
import nltk
import mongo_handler
import constants
import pprint
import random

# Taken from nltk book:
# http://www.nltk.org/book/ch05.html

'''
Usage:

Call from command line to classify 100 comments.

python3 cli:
    import nlp
    import nltk

    test, train = nlp.get_test_train_sets_positivity()
    classifier = nltk.NaiveBayesClassifier.train(train)
    nltk.classify.accuracy(classifier, test)
    classifier.show_most_informative_features()
'''

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
    body_lowercase = body.lower()

    # NOTE: does not break up multiple emojis without space between them
    tokens = nltk.word_tokenize(body)
    tagged = nltk.pos_tag(tokens) # list of tuples
    # https://stackoverflow.com/questions/48660547
    entities = nltk.chunk.ne_chunk(tagged) 

    features = {}
    # NaiveBayes cannot take non-binary values. Must be binned. Ch6 5.3
    l = len(tokens)
    if l < 3:
        features['short'] = True
    elif l < 15:
        features['mid-length'] = True
    else:
        features['long'] = True

    features['top level comment'] = comment['link_id'] == comment['parent_id']
    features['is OP'] = comment['is_submitter']
    features['mentions user'] = 'u/' in body

#    unique_token_count = 0
#    for word in tokens:
#        # mongo cannot handle 'contains(.)', or anything with a period, as a field
#        if '.' not in word:
#            
#            # nltk will not split up emojis that have no space between them
#            emoji_list = emoji.emoji_lis(word)
#            if emoji_list:
#                for d in emoji_list:
#                    emoji_s = 'emoji ({})'.format(d['emoji'])
#                    features[emoji_s] = True

#            s = 'contains ({})'.format(word.lower())
#            if s not in features:
#                # No need to worry about individual emoji count for this.
#                unique_token_count += 1
#                features[s] = True

#    features['pcnt unique'] = int(float(unique_token_count) 
#            / float(len(tokens)) * 100)

    # It is useful to know if certain emoji are present
    useful_emoji = [
            ":no_entry_sign:",
            ":mountain:",
            ":fire:",
            ":negative_squared_cross_mark:",
            ":x:",
            ":no_good:",
    ]
    for e in useful_emoji:
        features['emoji ({})'.format(emoji.emojize(e, use_aliases=True))] \
            = emoji.emojize(e, use_aliases=True) in comment['body']

    useful_words = [
            'you',
            'op',
            'not',
            'unwavy',
            'Kanye'
    ]
    for w in useful_words:
        features['contains \'{}\''.format(w)] = w in body_lowercase

    named_entities = 0
    for chunk in entities:
        if hasattr(chunk, 'label'):
            named_entities += 1
    if named_entities <= 0:
        features['no ne'] = True
    elif named_entities < 2:
        features['one ne'] = True
    else:
        features['multiple ne'] = True

    # classifier cannot handle nonbinary features
    # features['ne ratio'] = features['num ne'] / len(tokens)
    # TODO: consider also using neighbor words around 'wavy'

    return features

def comments_with_category():
    cursor = mongo_handler.get_categorized_comments()

    pairs = []
    # A labeled comment may not be labeled for both 'is_wavy' and 'category'
    for categorized_comment in cursor:
        if 'category' in categorized_comment:
            pairs.append((
                    mongo_handler.get_comment(
                        categorized_comment['name'], pretty=False),
                    categorized_comment['category']
            ))
    return pairs

def comments_with_positivity():
    cursor = mongo_handler.get_positivity_categorized_comments()

    pairs = []
    for categorized_comment in cursor:
        if 'is_wavy' in categorized_comment:
            pairs.append((
                    mongo_handler.get_comment(
                        categorized_comment['name'], pretty=False),
                    categorized_comment['is_wavy']
                    ))
    return pairs

def featureset(categorized_comments):
    return [(get_features(comment), category) 
            for (comment, category) in categorized_comments]

def get_test_train_sets_positivity():
    labeled_set = comments_with_positivity()
    random.shuffle(labeled_set)
    train_set = nltk.classify.apply_features(get_features, labeled_set[:500])
    test_set = nltk.classify.apply_features(get_features, labeled_set[500:])
    return test_set, train_set

def get_test_train_sets_category():
    labeled_set = comments_with_category()
    random.shuffle(labeled_set)
    train_set = nltk.classify.apply_features(get_features, labeled_set[:500])
    test_set = nltk.classify.apply_features(get_features, labeled_set[500:])
    return test_set, train_set

def category_metrics_display():
    metrics = mongo_handler.categories_counts()
    total = 0
    s = ""
    for category in metrics:
        count, pct = metrics[category]
        total += count
        count, pct = str(count), str(pct)

        category = category + ' ' * (15 - len(category))
        # Make 'count' three characters. TODO: does not scale
        count = ' ' * (3 - len(count)) + count
        if len(pct) < 2:
            pct = ' ' + pct
        
        s += 'CATEGORY: {}    COUNT: {}    PCT: {}\n'.format(
                category, count, pct)
    s += 'TOTAL: {}'.format(total)
    return s
        

def request_input_on_cursor(comment):
    s = '\nThe categories are:\n' + '\n'.join(
            ['{}: {}'.format(i, v) for i, v in enumerate(categories)])
    print(s + '\n')
    features = get_features(comment)
#    features_no_contains = {}
#    for feature in features:
#        if 'contains' not in feature:
#            features_no_contains[feature] = features[feature]
    print('==============================================================')
    print(comment['body'])
    print('Created (utc): ', comment['created_utc'])
    print('Fullname:', comment['name'])
    print('link: ' +  'reddit.com' + comment ['permalink'])
    pprint.pprint(features)
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

    mongo_handler.update_comment_category(
            name, category=category, is_wavy=positivity)


# generate train data by hand
if __name__ == '__main__':

    categories = constants.CATEGORIES
    positivity_options = constants.POSITIVITY

    command_cursor = mongo_handler.get_noncategorized_comments(limit=50)
    for comment in command_cursor:
        request_input_on_cursor(comment)

    # To edit ALL comments with category == 'link'
    # not actually a command cursor
#    command_cursor = mongo_handler.get_link_comments() 
#    for category in command_cursor:
#        comment = mongo_handler.get_comment(category['name'], pretty=False)
#        request_input_on_cursor(comment)

