'use strict'

const randomInt = require('random-int')
const request = require('request');
const mongoHandler = require('../kanye_realtime/src/server/mongo_handler.js');

const args = require('minimist')(process.argv.slice(2));
const {dbname = 'kanye', collectionName = 'wavy-comments'} = args;

var mongoHandlerPromise = mongoHandler(dbname);
const subreddit = 'https://www.reddit.com/r/kanye';
var url = subreddit + '/comments.json?limit=100';
var after = '';

function queryReddit(callback) {
	request(url + '&after=' + after, function(error, response, body) {
		body = JSON.parse(body);
		
		body.data.children.forEach(function(comment) {
			mongoHandlerPromise.then(function(export_fns) {
				export_fns.insertIfValid(comment);
			}, console.error);
		});

		after = body.data.after;
		console.log('\nafter: ', after);
		if(after != null) callback();
	});
}


function waitRandomTime() {
	setTimeout(function() {
		queryReddit(waitRandomTime);		
	}, randomInt(10, 15) * 1000);
}

queryReddit(waitRandomTime);


