var webpack = require('webpack');
var version = require('./package.json').version;
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var prodConfig = require('./webpack.config.js');

var devConfig = Object.assign({}, prodConfig);

devConfig.devtool = 'eval-cheap-module-source-map';
devConfig.plugins = [
  new webpack.DefinePlugin({
    'process.env': {
      'NODE_ENV': JSON.stringify('development')
    }
  }),
  new ExtractTextPlugin('main-' + version + '.css')
];

module.exports = devConfig;
