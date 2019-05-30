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
const {serverPort = 8080, dbname = 'kanye', collName = 'wavy-comments'} = args;

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

// First connect to mongodb.
mongoHandler(dbname).then(function(export_fns) {

    // Express routing for statistics.
    app.get('/statistics/data.json', function(req, res) {
        if (Date.now() < lastStatisticsTime + 6*60*60*1000 && !_.isEmpty(cachedStats)) {
            res.send(JSON.stringify(cachedStats));
        } else {
            export_fns.getPositivityStatistics(function(posStats) {
                export_fns.getCategoryStatistics(function(catStats) {
                    cachedStats = {
                        "positivity_statistics": posStats,
                        "category_statistics": catStats
                    }
                    lastStatisticsTime = Date.now();
                    res.send(JSON.stringify(cachedStats));
                }, e => console.error('Unable to get category stats:', e));
            });
        }
    });

    // Handle websockets.
    io.on('connection', socket => {
        console.log(`Socket ${socket.id} connected.`);
    
        // Send five most recent (oldest first).
        export_fns.retrieveRecent(5).then( function(docsArray) {
            for (var i = docsArray.length - 1; i >= 0; i--) {

                let comment = docsArray[i];
                get_estimate(comment, function(classification) {
                    comment['is_wavy'] = classification['is_wavy'];
                    comment['category'] = classification['category'];
                    socket.emit('comment', JSON.stringify(comment));
                });
                

            }
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

// app.get('/statistics/data.json', function(req, res) {
//     if (Date.now() < lastStatisticsTime + 6*60*60*1000 && !_.isEmpty(cachedStats)) {
//         res.send(JSON.stringify(cachedStats));
//     } else {
//         mongoHandler(dbname).then(function(export_fns) {
//             export_fns.getPositivityStatistics(function(posStats) {
//                 export_fns.getCategoryStatistics(function(catStats) {
//                     cachedStats = {
//                         "positivity_statistics": posStats,
//                         "category_statistics": catStats
//                     }
//                     lastStatisticsTime = Date.now();
//                     res.send(JSON.stringify(cachedStats));
//                 }, e => console.error('Unable to get category stats:', e));
//             });
//         });
//     }
// });

// var mongoHandlerPromise = mongoHandler(dbname);

// io.on('connection', socket => {
//     console.log(`Socket ${socket.id} connected.`);

//     // Send five most recent (oldest first).
//     mongoHandlerPromise.then(function(export_fns) {
//         export_fns.retrieveRecent(5).then( function(docsArray) {
//             for (var i = docsArray.length - 1; i >= 0; i--) {

//                 let comment = docsArray[i];
//                 get_estimate(comment, function(classification) {
//                     comment['is_wavy'] = classification['is_wavy'];
//                     comment['category'] = classification['category'];
//                     socket.emit('comment', JSON.stringify(comment));
//                 });
                

//             }
//        });
//     }, console.error);


//     socket.on('disconnect', socket => {
//             console.log(`Socket ${socket.id} disconnected.`);
//     });
// });

// snooper.watcher.getCommentWatcher('kanye')
// 	.on('comment', function(comment) {

// 		mongoHandlerPromise.then(function(export_fns) {
// 			export_fns.insertIfValid(comment).then(function(b) {
// 				if(b) io.emit('comment', JSON.stringify(comment.data));
// 			});
// 		});

// 	})
// 	.on('error', console.error);

// Server startup
// server.listen(+serverPort, '127.0.0.1', (err) => {
//   if (err) {
//     console.log(err.stack);
//     return;
//   }

//   console.log(`Kanye realtime node listening on http://127.0.0.1:${serverPort} started at: ${new Date()}.`);
// });
