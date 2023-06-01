const CopyWebpackPlugin = require('copy-webpack-plugin')
const HtmlWebpackIncludeAssetsPlugin = require('html-webpack-include-assets-plugin')

module.exports = {
  devServer: {
    port: process.env.SERVER_PORT || 8080
  },
  chainWebpack: config => {
    config.plugin('add-config').use(HtmlWebpackIncludeAssetsPlugin, [{ assets: ['js/config.js'], append: false }])
    config.plugin('config').use(CopyWebpackPlugin, [[{ from: './src/config.js', to: 'js/config.js' }]])
    return config
  }
}
