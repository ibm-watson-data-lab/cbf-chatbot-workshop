'use strict';

const dotenv = require('dotenv');
const program = require('commander');

const MyBot = require('./MyBot');

(function() {
    // load environment variables
    dotenv.config();
    let myBot = new MyBot(
        process.env.CONVERSATION_USERNAME,
        process.env.CONVERSATION_PASSWORD,
        process.env.CONVERSATION_WORKSPACE_ID
    );
    myBot.run();
})();