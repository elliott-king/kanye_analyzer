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

