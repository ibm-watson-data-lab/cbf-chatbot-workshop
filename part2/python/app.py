
from cloudant_dialog_store import CloudantDialogStore
from cloudant_user_store import CloudantUserStore
from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from health_bot import HealthBot
from slack_bot_controller import SlackBotController
from web_socket_bot_controller import WebSocketBotController
import os

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='$$',
        block_end_string='$$',
        variable_start_string='$',
        variable_end_string='$',
        comment_start_string='$#',
        comment_end_string='#$',
    )
)

# global vars
app = CustomFlask(__name__)
sockets = Sockets(app)
port = int(os.getenv('PORT', 8080))
web_socket_bot_controller = None
web_socket_protocol = 'ws://'

@app.route('/<path:path>')
def send_file(path):
    return send_from_directory('public', path)

@app.route('/')
def index():
    return render_template('index.html', web_socket_protocol=web_socket_protocol)

@sockets.route('/')
def process_websocket_message(ws):
    while not ws.closed:
        message = ws.receive()
        web_socket_bot_controller.process_message(ws, message)

if __name__ == '__main__':
    try:
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        user_store = CloudantUserStore(
            os.environ.get('CLOUDANT_USERNAME'),
            os.environ.get('CLOUDANT_PASSWORD'),
            os.environ.get('CLOUDANT_URL'),
            os.environ.get('CLOUDANT_USER_DB_NAME')
        )
        dialog_store = CloudantDialogStore(
            os.environ.get('CLOUDANT_USERNAME'),
            os.environ.get('CLOUDANT_PASSWORD'),
            os.environ.get('CLOUDANT_URL'),
            os.environ.get('CLOUDANT_DIALOG_DB_NAME')
        )
        healthBot = HealthBot(
            user_store,
            dialog_store,
            os.environ.get('CONVERSATION_USERNAME'),
            os.environ.get('CONVERSATION_PASSWORD'),
            os.environ.get('CONVERSATION_WORKSPACE_ID'),
            os.environ.get('FOURSQUARE_CLIENT_ID'),
            os.environ.get('FOURSQUARE_CLIENT_SECRET')
        )
        healthBot.init()
        # Start Slackbot Controller
        slackBotController = SlackBotController(
            healthBot,
            os.environ.get('SLACK_BOT_TOKEN')
        )
        slackBotController.start()
        # State WebSocket Controller
        web_socket_bot_controller = WebSocketBotController(healthBot)
        web_socket_bot_controller.start()
        # Start HTTP/WebSocket server
        server = pywsgi.WSGIServer(('', port), app, handler_class=WebSocketHandler)
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        # Stop Controllers
        slackBotController.stop()
        web_socket_bot_controller.stop()