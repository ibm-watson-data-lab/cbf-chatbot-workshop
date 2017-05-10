'use strict';

const SlackBot = require('slackbots');

class SlackBotController {

    constructor(healthBot, slackToken) {
        this.healthBot = healthBot;
        this.slackToken = slackToken;
    }

    /**
     * Starts the Slack Bot
     */
    start() {
        const slackBot = new SlackBot({
            token: this.slackToken,
            name: 'bot'
        });
        slackBot.on('start', () => {
            console.log('Slackbot running.')
        });
        slackBot.on('message', (data) => {
            if (data.type == 'message' && data.channel.startsWith('D')) {
                if (!data.bot_id) {
                    let messageSender = data.user;
                    let message = data.text;
                    this.healthBot.processMessage(messageSender, message)
                        .then((reply) => {
                            slackBot.postMessage(data.channel, reply.text, {});
                        });
                }
                else {
                    // ignore messages from the bot (messages we sent)
                }
            }
        });       
    }
}

module.exports = SlackBotController;