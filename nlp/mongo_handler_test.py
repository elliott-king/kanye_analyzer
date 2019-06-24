import unittest
import mongo_handler
import constants

from pymongo import MongoClient

long_comment = {
    "subreddit_id" : "t5_2r78l", 
    "created_utc": 34,
    "approved_at_utc" : None, 
    "edited" : False, 
    "link_id" : "t3_9j0m3i",
    "name" : "t1_e6oq65l", 
    "author" : "Dr_Wombo_Combo", 
    "parent_id" : "t1_e6o655y", 
    "score" : 1, 
    "body" : "Wavy baby 🌊", 
    "link_title" : "So, there's this girl and..", 
}

basic_comment =  {
    'author': 'HangTheDJHoldTheMayo',
    'body': 'Shits so wavy he can read the sound waves homie ',
    'created_utc': 1541259203,
    'name': 't1_e8z9okx'}

not_wavy = {
    'author': 'test_author_for_node',
    'name': 'not_wavy_comment',
    'body': 'does not contain the \'w\' word',
    'created_utc': 3020
}

exists_in_db = {
    'author': 'test_author_for_node',
    'name': 'exists_in_db_wavy_comment',
    'body': 'does contain \'wavy\'',
    'created_utc': 4455
}

is_wavy = {
    'author': 'test_author_for_node',
    'name': 'test_comment_new_in_db',
    'body': 'does contain wavy',
    'created_utc': 10
}

# my (official) classifications
classified_comments = [
    {'name': 't1_e6oq65l', 'category': 'poster'},
    {'name': 't1_e6or8v7', 'category': 'op'},
    {'name': 't1_e6os2j5', 'category': 'link', 'is_wavy': 'wavy'},
    {'name': 't1_e6oukv2', 'category': 'external_object', 'is_wavy': 'not_wavy'},
    {'name': 't1_e6pri2s', 'category': 'poster'},
    {'name': 't1_e6pt2xg', 'category': 'external_person'},
    {'name': 't1_e6pwf43', 'category': 'external_person'},
    {'name': 't1_e6pwj5r', 'category': 'kanye'},
    {'name': 't1_e6px1gk', 'category': 'misc'},
    {'name': 't1_e6px4pt', 'category': 'link', 'is_wavy': 'wavy'},
    {'name': 't1_enmx6kt', 'category': 'poster', 'is_wavy': 'wavy'},
    {'name': 'new_to_db', 'category': 'link', 'is_wavy': 'wavy'}
]

# User classifications.
user_classifications = [
    {
        'name': 'has_many_user_classifications',
        'ip': 'testip1',
        'classification': {
            constants.POSITIVITY: 'wavy',
            constants.CATEGORY: 'poster' 
        }
    },{
        'name': 'has_many_user_classifications',
        'ip': 'testip2',
        'classification': {
            constants.POSITIVITY: 'not_wavy',
            constants.CATEGORY: 'poster' 
        }
    },{
        'name': 'has_many_user_classifications',
        'ip': 'testip3',
        'classification': {
            constants.POSITIVITY: 'wavy',
            constants.CATEGORY: 'kanye' 
        }
    },{
        'name': 'has_one_classification',
        'ip': 'testip4',
        'classification': {
            constants.POSITIVITY: 'wavy',
            constants.CATEGORY: 'poster' 
        }
    },{
        'name': 'only_classified_category',
        'ip': 'testip5',
        'classification': {
            constants.CATEGORY: 'link' 
        }
    }
]

db = constants.DB_TEST

class CommentsDBTest(unittest.TestCase):
    def setUp(self):
        client = MongoClient()
        comments_collection = client.test[constants.COMMENTS]
        comments_collection.insert_many([ long_comment, basic_comment, not_wavy, exists_in_db, is_wavy ])
    
    def tearDown(self):
        client = MongoClient()
        comments_collection = client.test[constants.COMMENTS]
        comments_collection.delete_many({})

    def testSimple(self):
        comment = mongo_handler.get_comment('t1_e8z9okx', pretty=False, db=db)
        self.assertEqual(comment['author'], 'HangTheDJHoldTheMayo')

        with self.assertRaises(ValueError):
            mongo_handler.get_comment('comment_dne', db=db)

    def testShortener(self):
        comment = mongo_handler.get_comment('t1_e6oq65l', db=db)
        self.assertEqual(len(comment), 4)

    def testBodyOnly(self):
        comment = mongo_handler.body_only(mongo_handler.get_comment('t1_e8z9okx', db=db))
        self.assertEqual(comment, basic_comment['body'])

    def testGetRecent(self):
        comments = mongo_handler.get_recent_comments(limit=2, db=db)
        self.assertEqual(comments[0]['author'], basic_comment['author'])
        self.assertEqual(comments[1]['author'], exists_in_db['author'])

class CategoriesDBTest(unittest.TestCase):

    def setUp(self):
        self.client = MongoClient()
        categories_collection = self.client.test[constants.TRAIN_CATEGORIES]
        categories_collection.insert_many([
            {'name': 'in_db', constants.CATEGORY: 'poster'},
            {'name': 'also_in_db', constants.CATEGORY: 'kanye', constants.POSITIVITY: 'wavy'}
        ])

        comments_collection = self.client.test[constants.COMMENTS]
        comments_collection.insert_many([ long_comment, basic_comment, not_wavy, exists_in_db, is_wavy ])

    def tearDown(self):
        categories_collection = self.client.test[constants.TRAIN_CATEGORIES]
        categories_collection.delete_many({})

        comments_collection = self.client.test[constants.COMMENTS]
        comments_collection.delete_many({})
    
    def testIn(self):
        # TODO: include comment existing in database
        self.assertFalse(mongo_handler.is_updated('zarglbargl', db=db))
        self.assertTrue(mongo_handler.is_updated('in_db', db=db))

    def testGetNoncategorized(self):
        command_cursor = mongo_handler.get_noncategorized_comments(db=db)
        self.assertEqual(sum(1 for _ in command_cursor), 5)

    def testGetCategorized(self):
        command_cursor = mongo_handler.get_categorized_classified_comments(db=db)
        self.assertEqual(sum(1 for _ in command_cursor), 2)

        command_cursor = mongo_handler.get_positivity_classified_comments(db=db)
        self.assertEqual(sum(1 for _ in command_cursor), 1)

    # TODO: test statistics

class UserClassificationTest(unittest.TestCase):

    def setUp(self):
        for uc in user_classifications:
            mongo_handler.update_user_classification(uc['name'], uc['classification'], db=db)
        
    def tearDown(self):
        client = MongoClient()
        user_categorized_collection = client.test[constants.USER_CLASSIFIED]
        user_categorized_collection.delete_many({})

    def testInsert(self):
        many = mongo_handler.get_single_comment_classification_totals('has_many_user_classifications', db=db)
        self.assertEqual(many[constants.POSITIVITY]['wavy'], 2)
        self.assertEqual(many[constants.POSITIVITY]['not_wavy'], 1)
        self.assertDictEqual(many[constants.CATEGORY], 
            {'misc': 0, 'poster': 2, 'op': 0, 'link': 0, 
            'this_sub': 0, 'external_person': 0, 'external_object': 0, 
            'self': 0, 'kanye': 1, 'copypasta': 0}
        )

        few = mongo_handler.get_single_comment_classification_totals('only_classified_category', db=db)
        self.assertDictEqual(few[constants.CATEGORY],
            {'misc': 0, 'poster': 0, 'op': 0, 'link': 1,
            'this_sub': 0, 'external_person': 0, 'external_object': 0, 
            'self': 0, 'kanye': 0, 'copypasta': 0}
        )
        self.assertDictEqual(few[constants.POSITIVITY],
            {'ambiguous': 0, 'wavy': 0, 'not_wavy': 0}
        )

    def testCommentWithClassification(self):
        comment = mongo_handler.get_single_user_classification('has_many_user_classifications', db=db)
        self.assertEqual(comment[constants.POSITIVITY], 'wavy')
        self.assertEqual(comment[constants.CATEGORY], 'poster')

        comment = mongo_handler.get_single_user_classification('only_classified_category', db=db)
        self.assertEqual(comment[constants.CATEGORY], 'link')
        self.assertNotIn(constants.POSITIVITY, comment)
    
    def testAllClassifiedComments(self):
        self.assertEqual(3, len(mongo_handler.get_all_user_classified_comments(db=db)))
        for comment in mongo_handler.get_all_user_classified_comments(db=db):
            if comment['name'] == 'only_classified_category':
                self.assertDictEqual(comment, {'name': 'only_classified_category', 'category': 'link'})

class MetricsDisplay(unittest.TestCase):
    def setUp(self):
        self.client = MongoClient()
        classified_comments_collection = self.client.test[constants.TRAIN_CATEGORIES]
        classified_comments_collection.insert_many(classified_comments)

    def tearDown(self):
        self.client.test[constants.TRAIN_CATEGORIES].delete_many({})

    def testMetricsDisplay(self):
        metrics = mongo_handler.categories_counts(db=db)

        total_pct = 0
        total_count = 0

        for category in metrics:
            count, pct = metrics[category]
            total_count += count 
            total_pct += pct 
        self.assertEqual(total_count, 12)
        self.assertGreaterEqual(total_pct, 98)
        self.assertLessEqual(total_pct, 100)

if __name__ == '__main__':
    unittest.main()
