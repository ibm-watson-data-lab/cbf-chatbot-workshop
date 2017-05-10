'use strict';

const EventEmitter = require('events');

class WebSocketBotClient extends EventEmitter {

    constructor(connection) {
        super();
        this.connection = connection;
    }

    /**
     * Sends a message to the connected web socket client.
     * @param {Object} message
     * @param {string} message.type
     * @param {string} message.text
     */
    send(message) {
        this.connection.sendUTF(JSON.stringify(message));
    }

    onMessage(message) {
        this.emit('message', message);
    }
}

module.exports = WebSocketBotClient;