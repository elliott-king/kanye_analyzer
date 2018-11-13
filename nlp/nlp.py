import nltk

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
    features['no_parent_comments'] = comment['link_id'] == comment['parent_id']
    features['is_submitter'] = comment['is_submitter']
    features['num_ne'] = 0 # number of named entities
    for word in tokens:
        features['contains ({})'.format(word.lower())] = True

    for chunk in entities:
        if hasattr(chunk, 'label'):
            features['num_ne'] += 1
    features['ne_ratio'] = features['num_ne'] / len(tokens)

    return features
