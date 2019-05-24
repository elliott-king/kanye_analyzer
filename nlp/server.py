from flask import Flask
from flask import request

import nlp
import nltk
import mongo_handler

app = Flask(__name__)

positivity_test, positivity_train = nlp.get_test_train_sets_positivity()
category_test, category_train = nlp.get_test_train_sets_category()

positivity_classifier = nltk.NaiveBayesClassifier.train(positivity_train)
category_classifier = nltk.NaiveBayesClassifier.train(category_train)

@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/classify', methods=['GET'])
def classify():
    name = request.args.get('name')
    print('Pretty comment:', mongo_handler.get_comment(name))
    comment = mongo_handler.get_comment(name, pretty=False)
    return positivity_classifier.classify(comment) + '\n'
