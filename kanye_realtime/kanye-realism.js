const http = require('http');
const redditSnooper = require('reddit-snooper');
const emoji = require('node-emoji');
const path = require('path');
const socketio = require('socket.io');
const express = require('express');
const assert = require('assert');

const app = express();
const server = http.createServer(app);
const io = socketio(server);
app.use(express.static(__dirname + '/public'));

var args = require('minimist')(process.argv.slice(2));
const {serverPort = 8080, dbname = 'test', collName = 'test'} = args;

var snooper = new redditSnooper({
		automatic_retries: true,
		api_requests_per_minute: 60
});

var MongoClient = require('mongodb').MongoClient
        , format = require('util').format
        , mongoPort = '27017';

let mdb, collection; // Mongo database

MongoClient.connect(`mongodb://127.0.0.1:${mongoPort}`, function(err, client) {
	if (err) throw err;
	mdb = client.db(dbname);
	collection = mdb.collection(collName);
        console.log(`Connected to db ${dbname} on port ${mongoPort}.`);
	});


io.on('connection', socket => {
	console.log(`Socket ${socket.id} connected.`);

	socket.emit('comment', JSON.stringify({
		author: "Welcome!",
		body: "Welcome to the r/Kanye realtime wavy feed!",
		name: "realtime-intro-connection-message",
		created: (new Date).getTime()/1000,
	}));

	// Send four most recent (oldest first)
	collection.find().sort({created: -1}).limit(4).toArray(function(err, docs) {
		assert.equal(err, null);
		assert.equal(docs.length, 4);
		for (var i = docs.length - 1; i >= 0; i--) {
			socket.emit('comment', JSON.stringify(docs[i]));
		}
	});

	socket.on('disconnect', socket => {
		console.log(`Socket ${socket.id} disconnected.`);
	});
});

snooper.watcher.getCommentWatcher('kanye')
	.on('comment', function(comment) {
		var contents = comment.data.body;
		var user = comment.user;

		var wave = emoji.get('ocean');
		var waves = [wave, "wavy", "wavey"];

		for (var i = 0; i < waves.length; i++) {
			// https://stackoverflow.com/questions/1789945/how-to-check-whether-a-string-contains-a-substring-in-javascript
			if (contents.includes(waves[i])) {
				// wave emoji exists in comment
				console.log(`Comment posted by: ${comment.data.author} on: ${new Date(comment.data.created*1000)}`);
				console.log("contents: " + comment.data.body);
				io.emit('comment', JSON.stringify(comment.data));
				collection.insertOne(comment.data, 
						     function(err, result) {
					assert.equal(null, err);
					console.log("Result of insertion: " + result);
				}); 
				break;
			}
		}

	})
	.on('error', console.error);

// Server startup


server.listen(+serverPort, '127.0.0.1', (err) => {
  if (err) {
    console.log(err.stack);
    return;
  }

  console.log(`Kanye realtime node listening on http://127.0.0.1:${serverPort} started at: ${new Date()}.`);
});
