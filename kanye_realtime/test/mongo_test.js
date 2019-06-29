var mongoHandler = require('../src/server/mongo_handler.js')
var assert = require('assert');
var _ = require('lodash');

const not_wavy = {
	data: {
		author: 'test_author_for_node',
		name: 'not_wavy_comment',
		body: 'does not contain the \'w\' word'
	}
};

const exists_in_db = {
	data: {
		author: 'test_author_for_node',
		name: 'exists_in_db_wavy_comment',
		body: 'does contain \'wavy\''
	}
};
const is_wavy = {
	data: {
		author: 'test_author_for_node',
		name: 'test_comment_new_in_db',
		body: 'does contain wavy'
	}
};

const category_docs = [
    {
        name: 'a',
        is_wavy: 'wavy',
        category: 'poster'
    },{
        name: 'b',
        is_wavy: 'not_wavy',
        category: 'external_person'
    },{
        name: 'c', 
        is_wavy: 'wavy',
        category: 'op'
    },{
        name: 'd',
        is_wavy: 'wavy',
        category: 'external_person'
    }
    
];
const extra_category_doc = {
    name: 'e',
    is_wavy: 'not_wavy',
    category: 'external_person'
}
	
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
		, mongoPort = '27017'
        , commentCollection = 'wavy-comments'
        , categoryCollection = 'wavy-categories'
        , dbname = 'test';

	beforeEach('setup', function(done) {
		MongoClient.connect(`mongodb://127.0.0.1:${mongoPort}`, {useNewUrlParser: true}, function(err, client) {
			if(err) throw err;
			var collection = client.db(dbname).collection(commentCollection);
			console.log(`Connected to db ${dbname} on port ${mongoPort} for before()`);

			collection.insertOne(exists_in_db.data, function(err, result) {
                assert.equal(null, err);
            
                var categories = client.db(dbname).collection(categoryCollection);
                categories.insertMany(category_docs, (err, result) => {
                    assert.equal(null, err);
                    client.close();
                    done();
                });
            });
		});

	});

	afterEach('teardown', function(done) {
		MongoClient.connect(`mongodb://127.0.0.1:${mongoPort}`, {useNewUrlParser: true}, function(err, client) {
			if(err) throw err;
			var collection = client.db(dbname).collection(commentCollection);
			console.log(`Connected to db ${dbname} on port ${mongoPort} for after().`);
            collection.deleteMany({}, (err, result) => {
                assert.equal(null, err);

                var categories = client.db(dbname).collection(categoryCollection);
                categories.deleteMany({}, (err, result) => {
                    client.close();
                    assert.equal(null, err);
                    done();
                });
			});
		});
	});



	describe('#insertIfValid()', function() {
		it('should return false when comment does not contain wavy emoji', function(done) {
			mongoHandler().then(function(export_fns) {
                assert.ok(true);
				export_fns.insertIfValid(not_wavy).then( function(b) {
                    export_fns.close();
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
                    export_fns.close();
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
                    export_fns.close();
                    assert.ok(b);
                    done();
				});
			}, function(err) {
				console.error("error: ", err);
			});
		});
	});

	describe('#retrieveRecent()', function() {
		it('return the document in the \'test\' collection', function(done) {
			mongoHandler().then(function(export_fns) {
				export_fns.retrieveRecent().then(function(recentArray){
                    export_fns.close();
                    assert.ok(recentArray.length == 1);
                    done();
				});
			});
        });
        
        it('should fail if limit > 10', function(done) {
            mongoHandler().then(function(export_fns) {
                export_fns.retrieveRecent(limit=11).then(function(recentArray) {
                    export_fns.close();
                    console.error('This should fail because the limit is greater than 10.');
                    assert.ok(false);
                    done();
                }, function(err) {
                    export_fns.close();
                    assert.ok(true);
                    done();
                });
            });
        });
    });
});
