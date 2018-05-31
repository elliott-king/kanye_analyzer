const http = require('http');
const redditSnooper = require('reddit-snooper');
const emoji = require('node-emoji');
// var WebSocket = require('ws');
const path = require('path');
const socketio = require('socket.io');
const express = require('express');

const app = express();
const server = http.createServer(app);
const io = socketio(server);
app.use(express.static(path.join(__dirname, 'public')));
const serverPort = 8080;

snooper = new redditSnooper({
		automatic_retries: true,
		api_requests_per_minute: 60
});

io.on('connection', socket => {
	console.log(`Socket ${socket.id} connected.`);


	var introComment = JSON.stringify({
		data: {
			author: "Welcome!",
			body: "Welcome to the r/Kanye realtime feed!",
			name: "realtime-intro-connection-message",
		},

	});
	socket.emit('comment', introComment);

	socket.on('disconnect', socket => {
		console.log(`Socket ${socket.id} disconnected.`);
	});
});


console.log("Kanye realtime running on port " + serverPort + " started at: " + new Date());

snooper.watcher.getCommentWatcher('kanye')
	.on('comment', function(comment) {
		var contents = comment.data.body;
		var user = comment.user;
		var wave = emoji.get('ocean');

			console.log("Comment posted by: " + comment.data.author);
			console.log("contents: " + comment.data.body);

		io.emit('comment', JSON.stringify(comment));

	//if(contents.indexOf(wave) > -1){
		// wave exists in comment
	//}

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
