const emoji = require('node-emoji');
var MongoClient = require('mongodb').MongoClient
	,format = require('util').format
	, mongoPort = '27017'
	, collectionName = 'test'
	, dbName = 'test'
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
			if (b) return false;
			return collection.insertOne(comment.data).then(function(insert) {
				return true;
			}, function(err) {
				if (err) {
					console.error('Error with collection insertion: ',err);
					return collection.find().toArray()
					.then( function (array) { 
						console.log("array: ", array);
						return false;
					});
				}
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

//TODO: should take in dbname & collectionName
module.exports = function() {
	var promise = MongoClient.connect(url).then(
		function(client) {
			collection = client.db(dbName).collection(collectionName);
			console.log(`Connected to db ${dbName} on port ${mongoPort}.`);
			return export_fns;
		});
	return promise;
}
