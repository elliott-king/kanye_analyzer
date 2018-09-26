const redditSnooper = require('reddit-snooper');
const mongoHandler = require('./utils/mongo_handler.js');

const dbname = 'kanye'
	, collectionName = 'wavy-comments';

var snooper = new redditSnooper({
	automatic_retries: true,
	api_requests_per_minute: 60
});

var mongoHandlerPromise = mongoHandler(dbname, collectionName);

snooper.watcher.getCommentWatcher('kanye')
	.on('comment', function(comment) {
		mongoHandlerPromise.then(function(export_fns) {
			export_fns.insertIfValid(comment).then(function(b) {
				if (b) console.log('Inserted: ', comment.data.body);
			});
		});
	})
	.on('error', console.error);
