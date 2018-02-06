var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  context: __dirname,
  entry: [
      'webpack-dev-server/client?http://localhost:3000',
      // 'webpack-dev-server/client?http://192.168.1.193:3000',
      'webpack/hot/only-dev-server',
      'es6-promise',
      'whatwg-fetch',
      './csv_schema/static/js/index'
  ],

  output: {
      path: path.resolve('./csv_schema/static/bundles/'),
      filename: '[name]-[hash].js',
      publicPath: 'http://localhost:3000/static/bundles/', // Tell django to use this URL to load packages and not use STATIC_URL + bundle_name
      // publicPath: 'http://192.168.1.193:3000/static/bundles/', // Tell django to use this URL to load packages and not use STATIC_URL + bundle_name
  },

  plugins: [
    // new webpack.ProvidePlugin({
    //     'Promise': 'es6-promise', // Thanks Aaron (https://gist.github.com/Couto/b29676dd1ab8714a818f#gistcomment-1584602)
    //     'fetch': 'imports?this=>global!exports?global.fetch!whatwg-fetch'
    // }),
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoErrorsPlugin(), // don't reload if there is an error
    new BundleTracker({filename: './webpack-stats.json'}),
    new ExtractTextPlugin({ // define where to save the file
      filename: 'css/styles.css',
    }),
  ],

  module: {
    rules: [
      /*
      your other rules for JavaScript transpiling go in here
      */
      {
        test: /\.svg$/, use: "ignore-loader"
      },
      { // regular css files
        test: /\.css$/,
        use: ExtractTextPlugin.extract({
          use: 'css-loader?importLoaders=1'
        })
      },
      { // sass / scss loader for webpack
        test: /\.(sass|scss)$/,
        use: ExtractTextPlugin.extract(['css-loader', 'sass-loader'])
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          loaders: {
            // Since sass-loader (weirdly) has SCSS as its default parse mode, we map
            // the "scss" and "sass" values for the lang attribute to the right configs here.
            // other preprocessors should work out of the box, no loader config like this nessessary.
            'scss': 'vue-style-loader!css-loader!sass-loader',
            'sass': 'vue-style-loader!css-loader!sass-loader?indentedSyntax'
          }
          // other vue-loader options go here
        }
      },
    ]
  },
  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.common.js'
    },
    extensions: ['.vue', '.js'],
  },
}
