var redditSnooper = require('reddit-snooper');
var emoji = require('node-emoji');
var WebSocket = require('ws');
// var express = require('express');
// var server = express();

// server.use(express.static(__dirname));
var serverPort = 8081;
// server.listen(serverPort);
var wss = new WebSocket.Server({port:serverPort});
console.log("Kanye realtime running on port " + serverPort + " started at: " + new Date());

snooper = new redditSnooper(
	{
		automatic_retries: true,
		api_requests_per_minute: 60
	});

// Broadcast to all.
wss.broadcast = function broadcast(data) {
  wss.clients.forEach(function each(client) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(data);
    }
  });
};

wss.on('connection', function(ws) {

	console.log("Connected to websocket: " + ws);


	var introComment = JSON.stringify({
		user: "Welcome!",
		data: {
			body: "Welcome to the r/Kanye realtime feed!",
			name: "realtime-intro-connection-messaage",
		},

	});
	ws.send(introComment);
});

snooper.watcher.getCommentWatcher('kanye')
	.on('comment', function(comment) {
		var contents = comment.data.body;
		var user = comment.user;
		var wave = emoji.get('ocean');

			console.log("Comment posted by: " + comment.data.author);
			console.log("contents: " + comment.data.body);

		wss.broadcast(JSON.stringify(comment));

	//if(contents.indexOf(wave) > -1){
		// wave exists in comment
	//}

	})
	.on('error', console.error);

// module.exports = server;
