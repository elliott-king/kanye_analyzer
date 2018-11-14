import unittest
import mongo_handler

OUR_TEST_COMMENT =  {
        'author': 'HangTheDJHoldTheMayo',
        'body': 'Shits so wavy he can read the sound waves homie ',
        'created_utc': 1541259203,
        'name': 't1_e8z9okx'}


class CommentsDBTest(unittest.TestCase):

    def testSimple(self):
        comment = mongo_handler.get_comment('t1_e8zrokv', pretty=False)
        self.assertEqual(comment['author'], 'KnotMoses')

    def testShortener(self):
        comment = mongo_handler.get_comment('t1_e8zrokv')
        self.assertEqual(len(comment), 4)

    def testBodyOnly(self):
        comment = mongo_handler.body_only(mongo_handler.get_comment('t1_e8z9okx'))
        self.assertEqual(comment, OUR_TEST_COMMENT['body'])

class CategoriesDBTest(unittest.TestCase):
    
    def testIn(self):
        # TODO: include comment existing in database
        self.assertFalse(mongo_handler.is_updated('zarglbargl'))

if __name__ == '__main__':
    unittest.main()
