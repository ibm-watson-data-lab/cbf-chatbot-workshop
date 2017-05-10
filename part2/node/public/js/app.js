require(['vue'], function(Vue) {
    var app = new Vue({
        el: '#app',
        data: {
            botName: 'bot',
            userId: null,
            webSocketProtocol: webSocketProtocol,
            webSocket: null,
            webSocketConnected: false,
            webSocketPingTimer: null,
            message: '',
            messages: [],
            awaitingResponse: false,
            markdownConverter: new showdown.Converter()
        },
        methods: {
            submitMessage: function() {
                if (app.message.length == 0) {
                    return;
                }
                app.addMessage({
                    isBot: false,
                    user: 'Me',
                    ts: new Date(),
                    msg: app.markdownConverter.makeHtml(app.message)
                });
                if (! app.webSocketConnected) {
                    app.showOfflineMessage();
                }
                else {
                    app.webSocket.send(JSON.stringify({type: 'msg', text: app.message, userId: app.userId}));
                    app.awaitingResponse = true;
                }
                app.message = '';
            },
            addMessage(message) {
                app.messages.push(message);
                setTimeout(function() {
                    app.scrollMessagesToBottom()
                }, 100);
            },
            addOfflineMessage: function() {
                app.addMessage({
                    isBot: true,
                    user: app.botName,
                    ts: new Date(),
                    msg: app.markdownConverter.makeHtml('Sorry, you are not connected! I can\'t help you right now :(')
                });
            },
            scrollMessagesToBottom() {
                setTimeout(function() {
                    app.resizeMessageContainer();
                    var e = document.getElementById("chat-message-container");
                    e.scrollTop = e.scrollHeight;
                }, 100);
            },
            resizeMessageContainer() {
                var e = document.getElementById("chat-message-container");
                var rect = e.getBoundingClientRect();
                if (rect.top <= 20) {
                    e.style.maxHeight = rect.height + rect.top + 'px';
                }
                else {
                    e.style.maxHeight = null;
                }
            },
            generateUniqueId(len) {
                var ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
                var id = '';
                for (var i = 0; i<len; i++) {
                    id += ALPHABET.charAt(Math.floor(Math.random() * ALPHABET.length));
                }
                return id;
            },
            init() {
                // get userId
                if (typeof(Storage) !== "undefined") {
                    app.userId = localStorage.getItem("userId");
                }
                if (! app.userId) {
                    app.userId = app.generateUniqueId(8);
                    if (typeof(Storage) !== "undefined") {
                        localStorage.setItem("userId", app.userId);
                    }
                }
                // configure markdown->html converter
                app.markdownConverter.setOption('simpleLineBreaks', true);
                // set timer to periodically check the web socket connection
                setTimeout(app.onTimer, 1);
                // register with window onresize event
                window.onresize = function() {
                    app.resizeMessageContainer();
                }
            },
            onTimer() {
                if (! app.webSocketConnected) {
                    app.connect();
                }
                else {
                    app.webSocket.send(JSON.stringify({type: 'ping'}));
                }
                setTimeout(app.onTimer, 5000);
            },
            connect() {
                if ("WebSocket" in window) {
                    let webSocketUrl = app.webSocketProtocol + window.location.host;
                    app.webSocket = new WebSocket(webSocketUrl);
                    app.webSocket.onopen = function() {
                        console.log('Web socket connected.');
                        app.webSocketConnected = true;
                    };
                    app.webSocket.onmessage = function(evt)  {
                        app.awaitingResponse = false;
                        app.webSocketConnected = true;
                        var data = JSON.parse(evt.data);
                        if (data.type == 'msg') {
                            console.log('Received message.');
                            app.addMessage({
                                isBot: true,
                                user: app.botName,
                                ts: new Date(),
                                msg: app.markdownConverter.makeHtml(data.text)
                            });
                            editor.setValue(JSON.stringify(data.watsonData,null,3));
                        }
                        else if (data.type == 'ping') {
                            console.log('Received ping.');
                        }
                    };
                    app.webSocket.onclose = function() {
                        console.log('Websocket closed.');
                        if (app.webSocketConnected) {
                            app.offlineStep = 0;
                        }
                        if (app.awaitingResponse) {
                            app.awaitingResponse = false;
                            app.showOfflineMessage();
                        }
                        app.webSocketConnected = false;
                        app.webSocket = null;
                    };
                }
                else {
                    alert("WebSocket not supported browser.");
                }
            }
        }
    });

    (function() {
        // Initialize vue app
        app.init();
    })();
});