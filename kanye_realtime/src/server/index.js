const http = require('http');
const redditSnooper = require('reddit-snooper');
const socketio = require('socket.io');
const express = require('express');
const mongoHandler = require('./mongo_handler.js');
const request = require('request');

const app = express();
const server = http.createServer(app);
const io = socketio(server);
app.use(express.static(__dirname + '/../../dist/client'));

var args = require('minimist')(process.argv.slice(2));
const {serverPort = 8080, dbname = 'kanye', collName = 'wavy-comments'} = args;

var snooper = new redditSnooper({
		automatic_retries: true,
		api_requests_per_minute: 60
});

// Remember that the '_id' field is not serializable.
function get_estimate(comment, callback) {
    request({
        url: 'http://localhost:5000/classify',
        method: "POST",
        json: comment
    }, function(error, response, body) {
        console.log('Getting estimate for comment:', comment['name']);

        if(error) { console.error('error:', error); }
        console.log('Status code:', response && response.statusCode, 'body:', body);
        
        callback(body);
    });
};

app.get('/statistics/data.json', function(req, res) {
    mongoHandler(dbname)
    .then(function(export_fns) {
        export_fns.getPositivityStatistics(function(posStats) {
            export_fns.getCategoryStatistics(function(catStats) {
                res.send(JSON.stringify({
                    "positivity_statistics": posStats,
                    "category_statistics": catStats
                }));
            }, e => console.error('Unable to get category stats:', e));
        });
    });
});

var mongoHandlerPromise = mongoHandler(dbname);

io.on('connection', socket => {
    console.log(`Socket ${socket.id} connected.`);

    // Send four most recent (oldest first), then send the welcome message.
    mongoHandlerPromise.then(function(export_fns) {
        export_fns.retrieveRecent(4).then( function(docsArray) {
            for (var i = docsArray.length - 1; i >= 0; i--) {

                let comment = docsArray[i];
                get_estimate(comment, function(classification) {
                    comment['is_wavy'] = classification;
                    socket.emit('comment', JSON.stringify(comment));
                });
                

            }
            socket.emit('comment', JSON.stringify({
                    author: "Welcome!",
                    body: "Welcome to the r/Kanye realtime wavy feed!",
                    name: "realtime-intro-connection-message",
                    created: (new Date).getTime()/1000,
                    created_utc: (new Date).getTime()/1000,
                    permalink: "/r/Kanye"
            }));
       });
    }, console.error);


    socket.on('disconnect', socket => {
            console.log(`Socket ${socket.id} disconnected.`);
    });
});

snooper.watcher.getCommentWatcher('kanye')
	.on('comment', function(comment) {

		mongoHandlerPromise.then(function(export_fns) {
			export_fns.insertIfValid(comment).then(function(b) {
				if(b) io.emit('comment', JSON.stringify(comment.data));
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
