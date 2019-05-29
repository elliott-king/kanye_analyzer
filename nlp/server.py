from flask import Flask
from flask import request

import nlp
import nltk
import mongo_handler
import constants

import ast
import json

'''
export FLASK_APP=server.py
py -m flask run
'''

app = Flask(__name__)

positivity_test, positivity_train = nlp.get_test_train_sets_positivity()
category_test, category_train = nlp.get_test_train_sets_category()

positivity_classifier = nltk.NaiveBayesClassifier.train(positivity_train)
category_classifier = nltk.NaiveBayesClassifier.train(category_train)

# TODO: add both classifiers (currently only using positivity)

@app.route('/')
def hello_world():
    return 'Hello world!'

# response = requests.post('https://httpbin.org/post', json={'key':'value'})
@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if request.method == 'POST':
        comment = request.json
        print("Classifying comment:", comment['name'])

        cat = category_classifier.classify(comment)
        pos = positivity_classifier.classify(comment)

        print('Category:', cat)
        print('Is wavy:', pos)
        
        return json.dumps({
                'category': constants.CATEGORIES_TEXT[cat], 
                'is_wavy': constants.POSITIVITY_TEXT[pos]})

    return "Invalid request."

