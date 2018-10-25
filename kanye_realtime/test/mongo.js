var mongoHandler = require('../src/server/mongo_handler.js')
var assert = require('assert');

const not_wavy = {
	data: {
		author: 'test_author_for_node',
		name: 'test_name_for_node',
		body: 'does not contain the \'w\' word'
	}
};

const exists_in_db = {
	data: {
		author: 'test_author_for_node',
		name: 'test_name_for_node',
		body: 'does contain \'wavy\''
	}
};
const is_wavy = {
	data: {
		author: 'test_author_for_node',
		name: 'test_name_new_in_db',
		body: 'does contain wavy'
	}
};
	
// first time using mocha
describe('Array', function() {
	describe('#indexOf()', function() {
		it('should return -1 when the value is not present', function() {
			assert.equal([1,2,3].indexOf(4), -1);
		});
	});
});

describe('MongoHandler', function() {
	var MongoClient = require('mongodb').MongoClient
		, format = require('util').format
		, mongoPort = '27017'
		, collectionName = 'test'
		, dbname = 'test';

	before('add wavy comment to db', function(done) {
		MongoClient.connect(`mongodb://127.0.0.1:${mongoPort}`, function(err, client) {
			if(err) throw err;
			var collection = client.db(dbname).collection(collectionName);
			console.log(`Connected to db ${dbname} on port ${mongoPort} for before()`);

			collection.insertOne(exists_in_db.data, function(err, result) {
				assert.equal(null, err);
				client.close();
				done();
			});
		});

	});

	after('remove wavy comment from db', function(done) {
		MongoClient.connect(`mongodb://127.0.0.1:${mongoPort}`, function(err, client) {
			if(err) throw err;
			var collection = client.db(dbname).collection(collectionName);
			console.log(`Connected to db ${dbname} on port ${mongoPort} for after().`);

			collection.deleteOne({ name: exists_in_db.data.name}, function(err, result) {
				assert.equal(err, null);
				//assert.equal(1, result.result.n); // TODO may not always hold?	
				collection.deleteMany({ name: is_wavy.data.name}, function(err, result) {
					assert.equal(err, null);
					//assert.equal(1, result.result.n); // TODO may not always hold?
					client.close();
					done();
				});
			});
		});
	});



	describe('#insertIfValid()', function() {
		it('should return false when comment does not contain wavy emoji', function(done) {
			mongoHandler().then(function(export_fns) {
				export_fns.insertIfValid(not_wavy).then( function(b) {
					assert.ok(!b)
					done();
				});
			}, function(err) {
				console.log(err);
		    });
		});
		it('should return false because comment exists in db', function(done) {
			mongoHandler().then(function(export_fns) {
				var insert_promise = export_fns.insertIfValid(exists_in_db);
				insert_promise.then(function(b) {
					assert.ok(!b);
					done();
				});
			}, function(err) {
				console.log(err);
			});
		});
		it('should add comment when it did not previously exist in db', function(done) {
			mongoHandler().then(function(export_fns) {
				
				export_fns.insertIfValid(is_wavy).then(function(b) {
					assert.ok(b);
					done();
				});
			}, function(err) {
				console.error("error: ", err);
			});
		});
	});

	describe('#retrieveRecent()', function(done) {
		it('return the document in the \'test\' collection', function(done) {
			mongoHandler().then(function(export_fns) {
				export_fns.retrieveRecent().then(function(recentArray){
					assert.ok(recentArray.length == 1);
					done();
				});
			});
		});
	});
});
