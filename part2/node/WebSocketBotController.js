'use strict';

const http = require('http');
const WebSocketBotServer = require('./WebSocketBotServer');

class WebSocketBotController {

    /**
     * Creates a new instance of WebSocketBotController.
     * @param {object} healthBot - Instance of the HealthBot
     * @param {object} httpServer - The httpServer to bind the WebSocketServer to
     */
    constructor(healthBot, httpServer) {
        this.healthBot = healthBot;
        this.httpServer = httpServer;
    }

    /**
     * Starts the bot that will be used for clients connecting via WebSockets.
     */
    start() {
        this.webSocketBotServer = new WebSocketBotServer();
        this.webSocketBotServer.start(this.httpServer);
        this.webSocketBotServer.on('start', () => {
            console.log('WebSocketBotServer running.')
        });
        this.webSocketBotServer.on('connected', (client) => {
            client.on('disconnect', (message) => {
                // Clean up, if necessary
            });
            client.on('message', (message) => {
                this.onWebSocketClientMessage(client, message)
            });
        });
    }

    /**
     * This function is called when a new message is recieved from a client connecting via Websockets.
     * @param {object} client - Instance of WebSocketBotClient
     * @param {string} msg - The message entered by the user
     */
    onWebSocketClientMessage(client, msg) {
        if (msg.type == 'ping') {
            client.send({type: 'ping'});
        }
        else {
            let messageSender = msg.userId;
            let message = msg.text;
            this.healthBot.processMessage(messageSender, message)
                .then((reply) => {
                    var replyMsg = {
                        type: 'msg',
                        text: reply.text,
                        watsonData: reply.conversationResponse
                    };
                    client.send(replyMsg);
                });
        }
    }
}

module.exports = WebSocketBotController;