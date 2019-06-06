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

db = mongo_handler.DB_TEST

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
            {'name': 'in_db', 'category': 'poster'},
            {'name': 'also_in_db', 'category': 'kanye', 'is_wavy': 'wavy'}
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
        command_cursor = mongo_handler.get_categorized_comments(db=db)
        self.assertEqual(sum(1 for _ in command_cursor), 2)

        command_cursor = mongo_handler.get_positivity_categorized_comments(db=db)
        self.assertEqual(sum(1 for _ in command_cursor), 1)

    # TODO: test statistics

if __name__ == '__main__':
    unittest.main()
