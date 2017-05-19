import os
import sys

from dotenv import load_dotenv
from my_bot import MyBot

def prompt_user(my_bot):
    message = raw_input("Enter your message: ")
    if message == 'quit':
        pass
    else:
        reply = my_bot.process_message(message)
        print reply
        prompt_user(my_bot)

if __name__ == '__main__':
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    my_bot = MyBot(
        os.environ.get('CONVERSATION_USERNAME'),
        os.environ.get('CONVERSATION_PASSWORD'),
        os.environ.get('CONVERSATION_WORKSPACE_ID')
    )
    prompt_user(my_bot)