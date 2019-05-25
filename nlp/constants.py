# collections for mongodb
# TODO change name of collections in mongodb
COMMENTS = 'wavy-comments'
TRAIN_CATEGORIES = 'wavy-categories'

# Positive or negative use
# Also can use both for one thing
POSITIVITY = [
        'ambiguous',
        'wavy',
        'not_wavy',
]

POSITIVITY_TEXT = {
        'ambiguous': 'ambiguous',
        'wavy': 'wavy',
        'not_wavy': 'not wavy'
        }

# Categorization: who/what is being referred to as wavy?
CATEGORIES = [
    'misc',
    'poster', 
    'op',
    'link',
    'this_sub', # maybe merge in with 'poster'
    'external_person', # external person
    'external_object', # merged external_concepts into this
    'self',
    'kanye',
    'copypasta',
]

CATEGORIES_TEXT = {
    'misc': 'misc/other',
    'poster': 'another poster on the subreddit',
    'op': 'the original poster of the thread',
    'link': 'the subject of the thread',
    'this_sub': 'r/kanye itself',
    'external_person': 'an external individual',
    'external_object': 'an external object',
    'self': 'themselves',
    'kanye': 'the man himself',
    'copypasta': 'nothing. It is a copypasta',
}
