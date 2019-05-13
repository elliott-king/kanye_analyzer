// Shamelessly stolen from 
// https://www.codementor.io/tamizhvendan/beginner-guide-setup-reactjs-environment-npm-babel-6-webpack-du107r9zr

// Command to run: 
// npx webpack -d
// Runs webpack in dev mode
// TODO: handle production mode

var webpack = require('webpack')
var path = require('path')

var BUILD_DIR = (path.resolve(__dirname, 'src/client/public'));
var APP_DIR = (path.resolve(__dirname, 'src/client/app'));

var config = {
	// entry: APP_DIR + '/kanye-client.js',
	entry: APP_DIR + '/index.jsx', 
	output: {
		path: BUILD_DIR,
		filename: 'bundle.js'
	},
	module: {
		rules: [
			{
				test: /\.jsx?/,
				include: APP_DIR,
				loader: "babel-loader",
				query : {
					presets: ["@babel/preset-env", "@babel/preset-react"]
				}

			},
			{
				test: /\.css$/,
				use: ['style-loader', 'css-loader']
			}
		]
	}
};
module.exports = config;
