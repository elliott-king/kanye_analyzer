import unittest
import mongo_handler

class MongoHandlerTest(unittest.TestCase):

    def testSimple(self):
        comment = mongo_handler.get_comment('t1_e8zrokv', pretty=False)
        self.assertEqual(comment['author'], 'KnotMoses')

    def testShortener(self):
        comment = mongo_handler.get_comment('t1_e8zrokv')
        self.assertEqual(len(comment), 4)

if __name__ == '__main__':
    unittest.main()
