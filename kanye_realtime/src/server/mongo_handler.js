const emoji = require('node-emoji');
const _ = require('lodash');
var test = require('assert');
var MongoClient = require('mongodb').MongoClient
    , mongoPort = '27017'
    , client
    , db;

const COMMENTS = 'wavy-comments'
    , CATEGORIES = 'wavy-categories';
    
function isWavy(commentBody) {
	const waves = [emoji.get('ocean'), 'wavy', 'wavey'];
	var isWavy = false;

	for (var i = 0; i < waves.length; i++) {
		isWavy = ((commentBody.includes(waves[i])) ? true : isWavy);
	}
	return isWavy;
};

const export_fns = {

	getPositivityStatistics: function(callback) {
        let collection = db.collection(CATEGORIES);
        var cursor = collection.find({'is_wavy': {'$exists': true}});
        ret = {
            'wavy': 0,
            'not wavy': 0
        };
        cursor.forEach(function(doc) {
            test.ok(doc != null);
            if (doc.is_wavy == 'wavy') {
                ret['wavy'] += 1;
            } else {
                ret['not wavy'] += 1;
            }
        }, function(err) {
            test.equal(null, err);
            console.log('Generated new positivity stats at', Date.now());
            lastPositivityTime = Date.now();
            cachedPositivityStats = ret;
            callback(ret);
        });
    },
    
	getCategoryStatistics: function(callback) {
        let collection = db.collection(CATEGORIES);
        var cursor = collection.find({'category': {'$exists': true}});
        ret = {};
        cursor.forEach(function(doc) {
            test.ok(doc != null);
            if(ret.hasOwnProperty([doc.category])) {
                ret[doc.category] += 1;
            } else {
                ret[doc.category] = 1;
            }

        }, function(err) {
            test.equal(null, err);
            console.log('Generated new category stats at', Date.now());
            lastCategoryTime = Date.now();
            cachedCategoryStats = ret;
            callback(ret);
        });
	},

	// Expects a json-parsed object
	insertIfValid: function(comment) {
        let collection = db.collection(COMMENTS);
		var contents = comment.data.body;
		// var user = comment.data.author;
		var comment_name = comment.data.name
		//if (!contents || !user) {
		//	throw new // TODO: error, problem w/ comment json, include comment in err
		//}


		// first, check if contains wavyness
		if (!isWavy(contents)) {
			return new Promise(function(resolve) { resolve(false);});
		}

        // second, check if comment exists in db        
	    return collection.find({ name: comment_name}).hasNext().then( function(b) {
			if (b) {
				console.log('Already in db: ', comment.data.body, '\nWith id: ', comment.data.name);
				return false;
			}
			return collection.insertOne(comment.data).then(function(insert) {
				console.log('Inserted: ', comment.data.body, ' with id: ', comment.data.name, ' at time: ', new Date());
				return true;
			}, function(err) {
				console.error('Error with collection insertion: ',err);
				return false;
			});
		});
	},

	retrieveRecent: function(limit=1) {
		if (limit > 10) {
            return Promise.reject(new Error('Cannot retrieve more than 10 objects at a time.'));
        }
        
        // Will be ordered new -> old
        let collection = db.collection(COMMENTS);
		return collection.find().sort({created: -1}).limit(limit).toArray()
    },
    
    // Returns a promise.
    close: function() {
        return client.close(false);
    }
};

var url = `mongodb://127.0.0.1:${mongoPort}`;
module.exports = function(dbName='test') {
	var promise = MongoClient.connect(url, {useNewUrlParser: true}).then(
		function(c) {
            client = c;
            db = client.db(dbName);
			console.log(`Connected to db ${dbName} on port ${mongoPort} at ${(new Date).getTime()}`);
			return export_fns;
		});
	return promise;
}
