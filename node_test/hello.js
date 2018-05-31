#!/usr/bin/env nodejs
//var http = require('http');
//http.createServer(function (req, res) {
//  res.writeHead(200, {'Content-Type': 'text/plain'});
//  res.end('Hello World\n');
//}).listen(8080, 'localhost');
//console.log('Server running at http://localhost:8080/');

var express = require('express');
var cors = require("cors");
var app = express();

app.use(express.static("./public"));
var port = 8060;
app.listen(port);
console.log("Express app running on port " + port);
module.exports = app;
