# Chatbots with Node.js and Watson Conversation
## Part 2

This is part 2 of the tutorial delivered at Cognitive Builder Faire.

To run:

1. Import the Watson Conversation workspace from conversation/workspace.json into your Watson Conversation service.

Node.js:

1. cd into the node directory
2. Rename .env.template to .env
3. Add your Watson Conversation credentials to .env
4. Add your Cloudant Database URL to .env
5. Add your Foursquare credentials to .env
6. Optionally, add your Slackbot token to .env
7. Run `npm install`
8. Run `npm start`

Python:

1. cd into the python directory
2. Rename .env.template to .env
3. Add your Watson Conversation credentials to .env
4. Add your Cloudant Database Username, Password, and URL to .env
5. Add your Foursquare credentials to .env
6. Optionally, add your Slackbot token to .env
7. Create a virtual environment by running `virtualenv venv`
8. Activate the virtual environment by running `source ./venv/bin/activate`
9. Install dependencies by running `pip install -r requirements.txt`
10. Run `python app.py`
11. Go to http://localhost:8080