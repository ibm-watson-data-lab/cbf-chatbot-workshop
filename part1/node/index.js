'use strict';

const dotenv = require('dotenv');
const prompt = require('prompt');

const MyBot = require('./MyBot');

// load environment variables
dotenv.config();
const myBot = new MyBot(
    process.env.CONVERSATION_USERNAME,
    process.env.CONVERSATION_PASSWORD,
    process.env.CONVERSATION_WORKSPACE_ID
);

prompt.start();
promptUser();

function promptUser() {
    prompt.get([{name: 'message', message: 'Enter your message'}], (err, result) => {
        if (err || result.message == 'quit') {
            process.exit();
        }
        // The user's message is in result.message
        // Here we pass it to the processMessage function which will ultimately return a Promise
        // that when fulfilled contains the reply to send to the user.
        myBot.processMessage(result.message)
            .then((reply) => {
                console.log('MyBot: ' + reply);
                promptUser();
            });
    });
} 