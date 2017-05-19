import json
import sys
import time
import threading

from foursquare import Foursquare
from watson_developer_cloud import ConversationV1

class HealthBot():

    def __init__(self, user_store, dialog_store, conversation_username, conversation_password, conversation_workspace_id, foursquare_client_id, foursquare_client_secret):
        """
        Creates a new instance of HealthBot.
        Parameters
        ----------
        user_store - Instance of CloudantUserStore used to store and retrieve users from Cloudant
        dialog_store - Instance of CloudantDialogStore used to store conversation history
        conversation_username - The Watson Conversation username
        conversation_password - The Watson Converation password
        conversation_workspace_id - The Watson Conversation workspace ID
        foursquare_client_id - The Foursquare Client ID
        foursquare_client_secret - The Foursquare Client Secret
        """
        self.user_store = user_store
        self.dialog_store = dialog_store
        self.dialog_queue = {}
        self.conversation_client = ConversationV1(
            username=conversation_username,
            password=conversation_password,
            version='2016-07-11'
        )
        self.conversation_workspace_id = conversation_workspace_id
        if foursquare_client_id is not None and foursquare_client_secret is not None:
            self.foursquare_client = Foursquare(client_id=foursquare_client_id, client_secret=foursquare_client_secret)
        else:
            self.foursquare_client = None
    
    def init(self):
        """
        Initializes the bot, including the required datastores.
        """
        self.user_store.init()
        self.dialog_store.init()

    def process_message(self, message_sender, message):
        """
        Process the message entered by the user.
        Parameters
        ----------
        message_sender - The User ID from the messaging platform (Slack ID, or unique ID associated with the WebSocket client) 
        message - The message entered by the user
        """
        conversation_response = None
        try:
            user = self.get_or_create_user(message_sender)
            conversation_response = self.send_request_to_watson_conversation(message, user['conversation_context'])
            reply = self.handle_response_from_watson_conversation(message, user, conversation_response)
            self.update_user_with_watson_conversation_context(user, conversation_response['context'])
            return {'conversation_response': conversation_response, 'text': reply}
        except Exception:
            print(sys.exc_info())
            # clear state and set response
            reply = "Sorry, something went wrong!"
            return {'conversation_response': conversation_response, 'text': reply}

    def send_request_to_watson_conversation(self, message, conversation_context):
        """
        Sends the message entered by the user to Watson Conversation
        along with the active Watson Conversation context that is used to keep track of the conversation.
        Parameters
        ----------
        message - The message entered by the user
        conversation_context - The active Watson Conversation context
        """
        return self.conversation_client.message(
            workspace_id=self.conversation_workspace_id,
            message_input={'text': message},
            context=conversation_context
        )

    def handle_response_from_watson_conversation(self, message, user, conversation_response):
        """ 
        Takes the response from Watson Conversation, performs any additional steps
        that may be required, and returns the reply that should be sent to the user.
        Parameters
        ----------
        message - The message sent by the user
        user - The active user stored in Cloudant
        conversation_response - The response from Watson Conversation
        """
        # get_or_create_active_conversation_id will retrieve the active conversation
        # for the current user from our Cloudant log database.
        # A new conversation doc is created anytime a new conversation is started.
        # The conversationDocId is store in the Watson Conversation context,
        # so we can access it every time a new message is received from a user.
        conversation_doc_id = self.get_or_create_active_conversation_id(user, conversation_response)
            
        # Every dialog in our workspace has been configured with a custom "action"
        # that is available in the Watson Conversation context.
        # In some cases we need to take special steps and return a customized response
        # for an action - for example, lookup and return a list of doctors (handleFindDoctorByLocationMessage). 
        # In other cases we'll just return the response configured in the Watson Conversation dialog (handleDefaultMessage).
        if 'context' in conversation_response.keys() and 'action' in conversation_response['context'].keys():
            action = conversation_response['context']['action']
        else:
            action = None
        if action == "findDoctorByLocation":
            reply = self.handle_find_doctor_by_location_message(conversation_response)
        else:
            reply = self.handle_default_message(conversation_response)

        # Finally, we log every action performed as part of the active conversation
        # in our Cloudant dialog database and return the reply to be sent to the user.
        if conversation_doc_id is not None and action is not None:
            self.log_dialog(conversation_doc_id, action, message, reply)
        
        # return reply to be sent to the user
        return reply

    def handle_default_message(self, conversation_response):
        """
        The default handler for any message from Watson Conversation that requires no additional steps.
        Returns the reply that was configured in the Watson Conversation dialog.
        Parameters
        ----------
        conversation_response - The response from Watson Conversation
        """
        reply = ''
        for text in conversation_response['output']['text']:
            reply += text + "\n"
        return reply

    def handle_find_doctor_by_location_message(self, conversation_response):
        """
        The handler for the findDoctorByLocation action defined in the Watson Conversation dialog.
        Queries Foursquare for doctors based on the speciality identified by Watson Conversation
        and the location entered by the user.
        Parameters
        ----------
        conversation_response - The response from Watson Conversation
        """
        if self.foursquare_client is None:
            return 'Please configure Foursquare.'
        # Get the specialty from the context to be used in the query to Foursquare
        query = ''
        if 'specialty' in conversation_response['context'].keys() and conversation_response['context']['specialty'] is not None:
            query = query + conversation_response['context']['specialty'] + ' '
        query = query + 'Doctor'
        # Get the location entered by the user to be used in the query
        location = ''
        if 'entities' in conversation_response.keys():
            for entity in conversation_response['entities']:
                if (entity['entity'] == 'sys-location'):
                    if len(location) > 0:
                        location = location + ' '
                location = location + entity['value']
        params = {
            'query': query,
            'near': location,
            'radius': 5000
        }
        venues = self.foursquare_client.venues.search(params=params)
        if venues is None or 'venues' not in venues.keys() or len(venues['venues']) == 0:
            reply = 'Sorry, I couldn\'t find any doctors near you.'
        else:
            reply = 'Here is what I found:\n';
            for venue in venues['venues']:
                if len(reply) > 0:
                    reply = reply + '\n'
                reply = reply + '* ' + venue['name']
        return reply

    def get_or_create_user(self, message_sender):
        """
        Retrieves the user doc stored in the Cloudant database associated with the current user interacting with the bot.
        First checks if the user is stored in Cloudant. If not, a new user is created in Cloudant.
        Parameters
        ----------
        message_sender - The User ID from the messaging platform (Slack ID, or unique ID associated with the WebSocket client) 
        """
        return self.user_store.add_user(message_sender)

    def update_user_with_watson_conversation_context(self, user, conversation_context):
        """
        Updates the user doc in Cloudant with the latest Watson Conversation context.
        Parameters
        ----------
        user - The user doc associated with the active user
        conversation_context - The Watson Conversation context
        """
        return self.user_store.update_user(user, conversation_context)

    def get_or_create_active_conversation_id(self, user, conversation_response):
        """
        Retrieves the ID of the active conversation doc in the Cloudant conversation log database for the current user.
        If this is the start of a new converation then a new document is created in Cloudant,
        and the ID of the document is associated with the Watson Conversation context.
        Parameters
        ----------
        user - The user doc associated with the active user
        conversation_response - The response from Watson Conversation
        """
        if 'newConversation' in conversation_response['context'].keys():
            new_conversation = conversation_response['context']['newConversation']
        else:
            new_conversation = False
        if new_conversation == True:
            conversation_response['context']['newConversation'] = False
            converation_doc = self.dialog_store.add_conversation(user['_id'])
            conversation_response['context']['conversationDocId'] = converation_doc['_id']
            return converation_doc['_id']
        elif 'conversationDocId' in conversation_response['context'].keys():
            return conversation_response['context']['conversationDocId']
        else:
            return None

    def log_dialog(self, conversation_doc_id, name, message, reply):
        """
        Logs the dialog traversed in Watson Conversation by the current user to the Cloudant log database.
        Parameters
        ----------
        conversation_doc_id - The ID of the active conversation doc in Cloudant 
        name - The name of the dialog (action)
        message - The message sent by the user
        reply - The reply sent to the user
        """
        dialog_doc = {
            'name': name,
            'message': message,
            'reply': reply,
            'date': int(time.time()*1000)
        }
        self.dialog_store.add_dialog(conversation_doc_id, dialog_doc)
