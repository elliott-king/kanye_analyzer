import emoji
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
    "is_submitter": False,
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

class FeatureExtractorTest(unittest.TestCase):

    def testEmptyCommentExtractor(self):
        with self.assertRaises(ValueError):
            comment = {}
            _ = nlp.get_features(comment)

        # TODO: make the error more useful in nlp.py, consider:
        # https://stackoverflow.com/questions/39905390/how-to-auto-wrap-function-call-in-try-catch
        with self.assertRaises(KeyError):
            comment = basic_comment
            _ = nlp.get_features(comment)

    def testCommentExtractor(self):
        comment = long_comment
        features = nlp.get_features(comment)
        
        for e in constants.USEFUL_EMOJI:
            s = 'emoji ({})'.format(emoji.emojize(e, use_aliases=True))
            self.assertIn(s, features)
        for w in constants.USEFUL_WORDS:
            s = 'contains \'{}\''.format(w)
            self.assertIn(s, features)

        # TODO: kinda wack.
        expected_keys = ['one ne', 'is OP', 'mentions user', 'mid-length']
        for k in expected_keys:
            self.assertIn(k , features)

if __name__ == '__main__':
    unittest.main()
