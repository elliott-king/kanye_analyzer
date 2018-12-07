import emoji
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
    # TODO: this does not break apart multiple emojis (😭🌊 will not be broken up)
    tokens = nltk.word_tokenize(body)
    tagged = nltk.pos_tag(tokens) # list of tuples
    # https://stackoverflow.com/questions/48660547
    entities = nltk.chunk.ne_chunk(tagged) 

    features = {}
    features['length'] = len(tokens) # TODO: also counts punctuation
    features['top level comment'] = comment['link_id'] == comment['parent_id']
    features['is submitter'] = comment['is_submitter']
    features['num ne'] = 0 # number of named entities
    features['mentions user'] = 'u/' in body

    unique_token_count = 0
    for word in tokens:
        # mongo cannot handle 'contains(.)', or anything with a period, as a field
        if '.' not in word:
            
            # nltk will not split up emojis that have no space between them
            emoji_list = emoji.emoji_lis(word)
            if emoji_list:
                for d in emoji_list:
                    emoji_s = 'emoji ({})'.format(d['emoji'])
                    features[emoji_s] = True

            s = 'contains ({})'.format(word.lower())
            if s not in features:
                # No need to worry about individual emoji count for this.
                unique_token_count += 1
                features[s] = True

    features['pcnt unique'] = int(float(unique_token_count) 
            / float(len(tokens)) * 100)

    # It is useful to know if the 🚫 emoji is present
    features['emoji ({})'.format(emoji.emojize(
        "no_entry_sign", use_aliases=True))] = emoji.emojize(
            "no_entry_sign", use_aliases=True) in comment['body']

    for chunk in entities:
        if hasattr(chunk, 'label'):
            features['num ne'] += 1
    features['ne ratio'] = features['num ne'] / len(tokens)
    # TODO: consider also using neighbor words around 'wavy'

    return features

def comments_with_category():
    cursor = mongo_handler.get_categorized_comments()
    pairs = [
        (
            # mongo_handler.get_comment(category['name']),
            mongo_handler.get_comment(category['name'], pretty=False),
            category['category']
        ) for category in cursor]
    return pairs

def comments_with_positivity():
    cursor = mongo_handler.get_positivity_categorized_comments()
    pairs = [
        (
            # mongo_handler.get_comment(category['name']),
            mongo_handler.get_comment(category['name'], pretty=False),
            category['is_wavy']
        ) for category in cursor]
    return pairs

def featureset(categorized_comments):
    # Note that 'category' can be either positivity, or one of the subject
    # categories
    return [(get_features(comment), category) 
            for (comment, category) in categorized_comments]

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

    mongo_handler.update_comment_category(
            name, category=category, is_wavy=positivity)


# generate train data by hand
if __name__ == '__main__':

    categories = constants.CATEGORIES
    positivity_options = constants.POSITIVITY

    command_cursor = mongo_handler.get_noncategorized_comments(limit=50)
    for comment in command_cursor:
        request_input_on_cursor(comment)

    # not actually a command cursor
#    command_cursor = mongo_handler.get_link_comments() 
#    for category in command_cursor:
#        comment = mongo_handler.get_comment(category['name'], pretty=False)
#        request_input_on_cursor(comment)

