const webpack = require('webpack');
const config = {
    entry:  __dirname + '/js/index.jsx',
    output: {
        path: __dirname + '/assets',
        filename: 'bundle.js',
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css']
    },
    module: {
        rules: [
            {
                // rule for jsx files.
                test: /\.jsx?/,
                exclude: /node_modules/,
                use: [
                    {
                        // These are configs that help convert antd import
                        // statements to a less-heavy version.
                        loader: 'babel-loader',
                        options: {
                            // presets: ['@babel/preset-env'],
                            "plugins": [
                                [
                                    "import",
                                    {
                                        "libraryName": "antd",
                                        "style": 'css',   // or 'css'
                                    },
                                ]
                            ]
                        }
                    }
                ],
            },
            {
                // rules for scss files.
                test: /\.(scss|sass|css)$/,
                use: [

                    {
                        loader: 'style-loader'
                    },
                    {
                        loader: 'css-loader'
                    },
                    {
                        loader: 'sass-loader'
                    }
                ]
            },
            {
                // rules for scss files.
                test: /\.less$/,
                use: [{
                        loader: "style-loader" // creates style nodes from JS strings
                    }, {
                        loader: "css-loader" // translates CSS into CommonJS
                    }, {
                        loader: "less-loader", // compiles Less to CSS
                        options: {
                            javascriptEnabled: true
                        }
                    }
                ]
            }
        ]
    }
};
module.exports = config;
