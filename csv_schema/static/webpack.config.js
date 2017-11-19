var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  entry: ['./css/styles.scss'],
  // publicPath: "/",
  output: {
    filename: 'dist/bundle.js'
  },
  watch: true,
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
      }
    ]
  },
  plugins: [
    new ExtractTextPlugin({ // define where to save the file
      filename: 'css/styles.css',
    }),
  ],
};