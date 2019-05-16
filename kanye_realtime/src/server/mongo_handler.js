const emoji = require('node-emoji');
var test = require('assert');
var MongoClient = require('mongodb').MongoClient
	, format = require('util').format
	, mongoPort = '27017'
    , collection;
    
function isWavy(commentBody) {
	const waves = [emoji.get('ocean'), 'wavy', 'wavey'];
	var isWavy = false;

	for (var i = 0; i < waves.length; i++) {
		isWavy = ((commentBody.includes(waves[i])) ? true : isWavy);
	}
	return isWavy;
};

function inDatabase(comment_name) {
	// TODO: replace find with some sort of exist() function? maybe index the db?
	return collection.find({ name: comment_name}).hasNext();
};

const export_fns = {

    // TODO: make a global cache so we don't query the db every time.
	getPositivityStatistics: function(callback) {
        var cursor = collection.find({'is_wavy': {'$exists': true}});
        ret = {
            'false': 0,
            'true': 0
        };
        cursor.forEach(function(doc) {
            test.ok(doc != null);
            if (doc.is_wavy == 'wavy') {
                ret.true += 1;
            } else {
                ret.false += 1;
            }
        }, function(err) {
            test.equal(null, err);
            callback(ret);
        });
    },
    
	getCategoryStatistics: function(callback) {
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
            callback(ret);
        });
	},

	// Expects a json-parsed object
	insertIfValid: function(comment) {
		var contents = comment.data.body;
		var user = comment.data.author;
		var comment_name = comment.data.name
		//if (!contents || !user) {
		//	throw new // TODO: error, problem w/ comment json, include comment in err
		//}


		// first, check if contains wavyness
		if (!isWavy(contents)) {
			// TODO: monitor & log this?
			return new Promise(function(resolve) { resolve(false);});
		}

		// second, check if comment exists in db
		return inDatabase(comment_name).then( function(b) {
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
		//if (limit > 10) {
		//	throw new // TODO: limit exceeded error?
		//}
		// Will be ordered new -> old
		return collection.find().sort({created: -1}).limit(limit).toArray()
	}
};

var url = `mongodb://127.0.0.1:${mongoPort}`;
module.exports = function(dbName='test', collectionName='test') {
	var promise = MongoClient.connect(url).then(
		function(client) {
			collection = client.db(dbName).collection(collectionName);
			console.log(`Connected to db ${dbName} and collection ${collectionName} on port ${mongoPort} at ${(new Date).getTime()}`);
			return export_fns;
		});
	return promise;
}
