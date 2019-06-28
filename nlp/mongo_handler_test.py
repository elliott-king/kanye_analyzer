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
    {'name': 'dupe_to_user_classified', 'category': 'link', 'is_wavy': 'wavy'}
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
        'name': 'dupe_to_user_classified',
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
        comment = mongo_handler.get_comment('t1_e8z9okx', pretty=False)
        self.assertEqual(comment['author'], 'HangTheDJHoldTheMayo')

        with self.assertRaises(ValueError):
            mongo_handler.get_comment('comment_dne')

    def testShortener(self):
        comment = mongo_handler.get_comment('t1_e6oq65l')
        self.assertEqual(len(comment), 4)

    def testBodyOnly(self):
        comment = mongo_handler.body_only(mongo_handler.get_comment('t1_e8z9okx'))
        self.assertEqual(comment, basic_comment['body'])

    def testGetRecent(self):
        comments = mongo_handler.get_recent_comments(limit=2)
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
        self.assertFalse(mongo_handler.is_updated('zarglbargl'))
        self.assertTrue(mongo_handler.is_updated('in_db'))

    def testGetNoncategorized(self):
        command_cursor = mongo_handler.get_noncategorized_comments()
        self.assertEqual(sum(1 for _ in command_cursor), 5)

    def testGetCategorized(self):
        command_cursor = mongo_handler.get_categorized_classified_comments()
        self.assertEqual(sum(1 for _ in command_cursor), 2)

        command_cursor = mongo_handler.get_positivity_classified_comments()
        self.assertEqual(sum(1 for _ in command_cursor), 1)

    # TODO: test statistics

class UserClassificationTest(unittest.TestCase):

    def setUp(self):
        for uc in user_classifications:
            mongo_handler.update_user_classification(uc['name'], uc['classification'])
        
    def tearDown(self):
        client = MongoClient()
        user_categorized_collection = client.test[constants.USER_CLASSIFIED]
        user_categorized_collection.delete_many({})

    def testInsert(self):
        many = mongo_handler.get_single_comment_classification_totals('has_many_user_classifications')
        self.assertEqual(many[constants.POSITIVITY]['wavy'], 2)
        self.assertEqual(many[constants.POSITIVITY]['not_wavy'], 1)
        self.assertDictEqual(many[constants.CATEGORY], 
            {'misc': 0, 'poster': 2, 'op': 0, 'link': 0, 
            'this_sub': 0, 'external_person': 0, 'external_object': 0, 
            'self': 0, 'kanye': 1, 'copypasta': 0}
        )

        few = mongo_handler.get_single_comment_classification_totals('only_classified_category')
        self.assertDictEqual(few[constants.CATEGORY],
            {'misc': 0, 'poster': 0, 'op': 0, 'link': 1,
            'this_sub': 0, 'external_person': 0, 'external_object': 0, 
            'self': 0, 'kanye': 0, 'copypasta': 0}
        )
        self.assertDictEqual(few[constants.POSITIVITY],
            {'ambiguous': 0, 'wavy': 0, 'not_wavy': 0}
        )

    def testCommentWithClassification(self):
        comment = mongo_handler.get_single_user_classification('has_many_user_classifications')
        self.assertEqual(comment[constants.POSITIVITY], 'wavy')
        self.assertEqual(comment[constants.CATEGORY], 'poster')

        comment = mongo_handler.get_single_user_classification('only_classified_category')
        self.assertEqual(comment[constants.CATEGORY], 'link')
        self.assertNotIn(constants.POSITIVITY, comment)
    
    def testAllClassifiedComments(self):
        self.assertEqual(3, len(mongo_handler.get_all_user_classified_comments()))
        for comment in mongo_handler.get_all_user_classified_comments():
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
        metrics = mongo_handler.categories_counts()

        total_pct = 0
        total_count = 0

        for category in metrics:
            count, pct = metrics[category]
            total_count += count 
            total_pct += pct 
        self.assertEqual(total_count, 12)
        self.assertGreaterEqual(total_pct, 98)
        self.assertLessEqual(total_pct, 100)

class CombineCommentsWithClassification(unittest.TestCase):

    def setUp(self):

        for comment in classified_comments:
            positivity = comment['is_wavy'] if 'is_wavy' in comment else None
            mongo_handler.update_comment_category(comment['name'], category=comment['category'], is_wavy=positivity)

        client = MongoClient()
        comments_collection = client.test[constants.COMMENTS]
        for comment in classified_comments:
            c = {'body': 'some body', 'name': comment['name']}
            comments_collection.insert_one(c)

    def tearDown(self):
        client = MongoClient()

        categories_collection = client.test[constants.TRAIN_CATEGORIES]
        categories_collection.delete_many({})

        comments_collection = client.test[constants.COMMENTS]
        comments_collection.delete_many({})

        user_classifications = client.test[constants.USER_CLASSIFIED]
        user_classifications.delete_many({})

    def testOnlyOfficialComments(self):

        categorized = mongo_handler.classified_comments_with_category()
        positivized = mongo_handler.classified_comments_with_positivity()

        self.assertEqual(len(categorized), len(classified_comments))
        self.assertEqual(len(positivized), len(classified_comments) - 7)

        for comment, category in categorized:
            self.assertIn(category, constants.CATEGORIES_TEXT)
            self.assertIn('body', comment)
            self.assertIn('name', comment)
        
        for comment, positivity in positivized:
            self.assertIn(positivity, constants.POSITIVITY_TEXT)
            self.assertIn('body', comment)
            self.assertIn('name', comment)

    # then add some user-classified comments
    def testWithUserClassification(self):
        client = MongoClient()
        comments_collection = client.test[constants.COMMENTS]

        for uc in user_classifications:
            mongo_handler.update_user_classification(uc['name'], uc['classification'])
            # creates dupe for the 'dupe_to_user_classified' but that is not important.
            c = {'body': 'different body for the user classifications', 'name': uc['name']}
            comments_collection.insert_one(c)
        
        categorized = mongo_handler.classified_comments_with_category()
        positivized = mongo_handler.classified_comments_with_positivity()

        self.assertEqual(len(categorized), len(classified_comments) + len(user_classifications) - 1 - 2)
        self.assertEqual(len(positivized), len(user_classifications) + len(classified_comments) - 7 - 1 - 2 - 1)

        for comment, category in categorized:
            self.assertIn(category, constants.CATEGORIES_TEXT)
            self.assertIn('body', comment)
            self.assertIn('name', comment)
        
        for comment, positivity in positivized:
            self.assertIn(positivity, constants.POSITIVITY_TEXT)
            self.assertIn('body', comment)
            self.assertIn('name', comment)

    def testMetricsWithUserClassification(self):
        for uc in user_classifications:
            mongo_handler.update_user_classification(uc['name'], uc['classification'])
        
        metrics = mongo_handler.categories_counts()

        total_pct = 0
        total_count = 0

        for category in metrics:
            count, pct = metrics[category]
            total_count += count 
            total_pct += pct 
        self.assertEqual(total_count, 14)
        self.assertGreaterEqual(total_pct, 98)
        self.assertLessEqual(total_pct, 100)
        
        metrics = mongo_handler.positivity_counts()

        total_pct = 0
        total_count = 0

        for positivity in metrics:
            count, pct = metrics[positivity]
            total_count += count 
            total_pct += pct 
        self.assertEqual(total_count, 6)
        self.assertGreaterEqual(total_pct, 98)
        self.assertLessEqual(total_pct, 100)


        


if __name__ == '__main__':
    constants.DB_KANYE = constants.DB_TEST
    unittest.main()
