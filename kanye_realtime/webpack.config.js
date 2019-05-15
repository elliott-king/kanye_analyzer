// Shamelessly stolen from 
// https://www.codementor.io/tamizhvendan/beginner-guide-setup-reactjs-environment-npm-babel-6-webpack-du107r9zr

// TODO: handle production mode

const CopyWebpackPlugin = require('copy-webpack-plugin');
const webpack = require('webpack')
const path = require('path')

var BUILD_DIR = (path.resolve(__dirname, 'dist/client'));
var APP_DIR = (path.resolve(__dirname, 'src/client'));

var config = {
    mode: 'development',
    entry: {
        index: APP_DIR + '/index.jsx',
        statistics: APP_DIR + '/statistics.jsx',
    },

    output: {
        path: BUILD_DIR,
        filename: '[name].bundle.js'
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
    },
    plugins: [
        new CopyWebpackPlugin([
            APP_DIR + '/static',
        ])
    ]
};
module.exports = config;
