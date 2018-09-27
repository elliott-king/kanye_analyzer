const http = require('http');
const redditSnooper = require('reddit-snooper');
const emoji = require('node-emoji');
const path = require('path');
const socketio = require('socket.io');
const express = require('express');
const assert = require('assert');
const mongoHandler = require('../comment_collector/utils/mongo_handler.js');

const app = express();
const server = http.createServer(app);
const io = socketio(server);
app.use(express.static(__dirname + '/public'));

var args = require('minimist')(process.argv.slice(2));
const {serverPort = 8080, dbname = 'kanye', collName = 'wavy-comments'} = args;

var snooper = new redditSnooper({
		automatic_retries: true,
		api_requests_per_minute: 60
});

var mongoHandlerPromise = mongoHandler(dbname, collName);

io.on('connection', socket => {
	console.log(`Socket ${socket.id} connected.`);

	socket.emit('comment', JSON.stringify({
		author: "Welcome!",
		body: "Welcome to the r/Kanye realtime wavy feed!",
		name: "realtime-intro-connection-message",
		created: (new Date).getTime()/1000,
	}));

	// Send four most recent (oldest first)
	// TODO: order may be out of whack
	mongoHandlerPromise.then(function(export_fns) {
		export_fns.retrieveRecent(4).then( function(docsArray) {
			for (var i = docsArray.length - 1; i >= 0; i--) {
				socket.emit('comment', JSON.stringify(docsArray[i]));
			}
		}, console.error);

	});

	socket.on('disconnect', socket => {
		console.log(`Socket ${socket.id} disconnected.`);
	});
});

snooper.watcher.getCommentWatcher('kanye')
	.on('comment', function(comment) {

		mongoHandlerPromise.then(function(export_fns) {
			export_fns.insertIfValid(comment).then(function(b) {
				if(b){
					console.log('Inserted: ', comment.data.body);
					io.emit('comment', JSON.stringify(comment.data));
				}
			});
		});

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
