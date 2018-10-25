// Shamelessly stolen from 
// https://www.codementor.io/tamizhvendan/beginner-guide-setup-reactjs-environment-npm-babel-6-webpack-du107r9zr

var webpack = require('webpack')
var path = require('path')

var BUILD_DIR = (path.resolve(__dirname, 'src/client/public'));
var APP_DIR = (path.resolve(__dirname, 'src/client/app'));

var config = {
	entry: APP_DIR + '/kanye-client.js',
	// entry: APP_DIR + '/index.jsx', TODO
	output: {
		path: BUILD_DIR,
		filename: 'bundle.js'
	}
};
module.exports = config;
