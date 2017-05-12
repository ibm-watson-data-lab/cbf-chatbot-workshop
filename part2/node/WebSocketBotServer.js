'use strict';

const http = require('http');
const WebSocketBotClient = require('./WebSocketBotClient');
const WebSocketServer = require('websocket').server;
const EventEmitter = require('events');

class WebSocketBotServer extends EventEmitter {

    /**
     * Creates a new instance of WebSocketBotServer.
     */
    constructor() {
        super();
        this.clients = [];
    }

    /**
     * Starts the WebSocketServer.
     * @param httpServer - The httpServer to bind to.
     */
    start(httpServer) {
        this.webSocketServer = new WebSocketServer({httpServer: httpServer, autoAcceptConnections: false});
        this.webSocketServer.on('request', (request) => {
            this.onWebSocketConnection(request);
        });
    }

    /**
     * This function is called when a new client is connected to the WebSocketServer.
     * @param {object} request - The connection request
     */
    onWebSocketConnection(request) {
        console.log(`${new Date()} WebSocket connection accepted.`);
        const connection = request.accept(null, request.origin);
        const client = new WebSocketBotClient(connection);
        this.clients.push(client);
        this.onClientConnected(client);
        connection.on('message', (message) => {
            if (message.type === 'utf8') {
                console.log(`${new Date()} WebSocket server received message: ${message.utf8Data}`);
                const data = JSON.parse(message.utf8Data);
                client.onMessage(data);
            }
        });
        connection.on('close', () => {
            const index = this.clients.indexOf(client);
            if (index >=0 ) {
                this.clients.splice(index, 1);
                console.log(`${new Date()} WebSocket client ${connection.remoteAddress} disconnected.`);
            }
            this.onClientDisconnected(client);
        });
    }

    onClientConnected(client) {
        this.emit('connected', client);
    }

    onClientDisconnected(client) {
        this.emit('disconnected', client);
    }
}

module.exports = WebSocketBotServer;