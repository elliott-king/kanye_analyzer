const http = require('http');
const redditSnooper = require('reddit-snooper');
const socketio = require('socket.io');
const express = require('express');
const mongoHandler = require('./mongo_handler.js');
const request = require('request');
const _ = require('lodash');

const app = express();
const server = http.createServer(app);
const io = socketio(server);
app.use(express.static(__dirname + '/../../dist/client'));

var args = require('minimist')(process.argv.slice(2));
const {serverPort = 8080, dbname = 'kanye'} = args;

var lastStatisticsTime = 0
    , cachedStats = {};

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
        if (!body) {
            body = "Unable to create estimate for comment.";
        }
        callback(body);
    });
};

function get_statistics(callback) {
    if (Date.now() < lastStatisticsTime + 6*60*60*1000 && !_.isEmpty(cachedStats)) {
        console.log("Returning cached stats");
        callback(cachedStats);
    } else {
        console.log("Requesting new statistics at:", Date.now());
        request({
            url: 'http://localhost:5000/statistics',
            method: "GET"
        }, function(error, response, body) {
            if(error) console.error('error:', error); 
            lastStatisticsTime = Date.now();
            cachedStats = body;
            console.log("Statistics fetched: ", body);
            callback(body);
        });
    }
}

// First connect to mongodb.
mongoHandler(dbname).then(function(export_fns) {

    // Express routing for statistics.
    app.get('/statistics/data.json', function(req, res) {
        get_statistics(function(body) { 
            res.send(body);
        });
    });

    // Handle websockets.
    io.on('connection', socket => {
        console.log(`Socket ${socket.id} connected.`);

        let retrieveRecent = function() {
    
            // Send five most recent (oldest first).
            export_fns.retrieveRecent(5).then(function(docsArray) {
                let commentsArray = [];
    
                // Need this as a callback to ensure order.
                // npm requests module does not handle promises.
                var estimate_last_value = function(arr) {
                    let comment = arr.pop();
    
                    get_estimate(comment, (classification) => {
                        if(classification) {
                            comment['is_wavy'] = classification['is_wavy'];
                            comment['category'] = classification['category'];
                        }
                        commentsArray.push(comment);
                        if(arr.length > 0) {
                            estimate_last_value(arr);
                        } else {
                            (async () => {
                                for (var i = 0; i < commentsArray.length; i++) {
                                    await socket.emit('comment', JSON.stringify(commentsArray[i]));
                                }
                            })();
                        }
                    });
                };
    
                estimate_last_value(docsArray);
            }).catch(err => {
                console.error(err);
                throw err;
            });
        };

        retrieveRecent();

        socket.on('user_classification', (classification, commentId) => {
            // x-real-ip header supplied by nginx setting. Needed to get user IP
            var ipaddr = socket.handshake.headers['x-real-ip'] || socket.handshake.address;
            request({
                url: 'http://localhost:5000/user_classification',
                method: "POST",
                json: {comment_name: commentId, ipaddr: ipaddr, classification: classification}
            }, function(error, response, body) {

                console.log('Updating user classification for comment:', commentId);
        
                if(error) { console.error('error:', error); }
                console.log('Status code:', response && response.statusCode, 'body:', body);
                if (!body) {
                    body = "Unable to create estimate for comment.";
                }
            });
        });

        socket.on('recent_comments', () => {
            retrieveRecent();
        });

        socket.on('random_comments', () => {
            export_fns.retrieveRandom(5).then(function(docsArray) {

                // We don't explicitly need them in order.
                for (i = 0; i < docsArray.length; i++) {
                    let comment = docsArray[i];
                    get_estimate(comment, (classification) => {
                        if(classification) {
                            comment['is_wavy'] = classification['is_wavy'];
                            comment['category'] = classification['category'];
                        }
                        socket.emit('comment', JSON.stringify(comment));
                    });
                }

            }).catch(err => {
                console.error(err); 
                throw err;
            });
        });
        
        socket.on('disconnect', socket => {
            console.log(`Socket ${socket.id} disconnected.`);
        });
    });

    // Get new comments from r/kanye in real time.
    snooper.watcher.getCommentWatcher('kanye')
	.on('comment', function(comment) {
        export_fns.insertIfValid(comment).then(function(b) {
            if(b) io.emit('comment', JSON.stringify(comment.data));
        });
    }).on('error', console.error);

    // Server startup
    server.listen(+serverPort, '127.0.0.1', (err) => {
    if (err) {
      console.error(err.stack);
    }
    console.log(`Kanye realtime node listening on http://127.0.0.1:${serverPort} started at: ${new Date()}.`);
  });
});
