import unittest
from pymongo import MongoClient

import nlp
import constants
import mongo_handler

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

db = mongo_handler.DB_KANYE

class FeatureExtractorTest(unittest.TestCase):
    # def setUp(self):
    #     self.client = MongoClient()
    #     comments_collection = self.client.test[constants.COMMENTS]
    #     comments_collection.insert_many([ long_comment, basic_comment, not_wavy, exists_in_db, is_wavy ])

    # def tearDown(self):
    #     comments_collection = self.client.test[constants.COMMENTS]
    #     comments_collection.delete_many()

    def testEmptyCommentExtractor(self):
        with self.assertRaises(ValueError):
            comment = {}
            _ = nlp.get_features(comment)

if __name__ == '__main__':
    unittest.main()
