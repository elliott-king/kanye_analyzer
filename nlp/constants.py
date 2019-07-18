# mongodb database names
DB_KANYE = 'kanye'
DB_TEST = 'test'

# collections for mongodb
# TODO change name of collections in mongodb
COMMENTS = 'wavy-comments'
TRAIN_CATEGORIES = 'wavy-categories'
USER_CLASSIFIED = 'user-classification'

# Names for fields
POSITIVITY = 'is_wavy'
CATEGORY = 'category'

# Python remembers order of insertion for 3.7+

# Positive or negative use
# Also can use both for one thing
POSITIVITY_TEXT = {
        'ambiguous': 'ambiguous',
        'wavy': 'wavy',
        'not_wavy': 'not wavy'
        }

# Categorization: who/what is being referred to as wavy?
CATEGORIES_TEXT = {
    'misc': 'misc/other',
    'poster': 'another poster on the subreddit',
    'op': 'the original poster of the thread',
    'link': 'the subject of the thread',

    # maybe merge this in with 'poster'
    'this_sub': 'r/kanye itself',
    'external_person': 'an external individual',

    # merged external_concepts into this
    'external_object': 'an external object',
    'self': 'themselves',
    'kanye': 'the man himself',
    'copypasta': 'nothing. It is a copypasta',
}

# It is useful to know if certain emoji or words are present
USEFUL_EMOJI = [
        ":no_entry_sign:",
        ":mountain:",
        ":fire:",
        ":negative_squared_cross_mark:",
        ":x:",
        ":no_good:",
]

USEFUL_WORDS = [
        'you',
        'op',
        'not',
        'unwavy',
        'Kanye',
        '/s'
]
