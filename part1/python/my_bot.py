import sys

from watson_developer_cloud import ConversationV1

class MyBot():

    def __init__(self, conversation_username, conversation_password, conversation_workspace_id):
        """
        Creates a new instance of MyBot.
        Parameters
        ----------
        conversation_username - The Watson Conversation username
        conversation_password - The Watson Converation password
        conversation_workspace_id - The Watson Conversation workspace ID
        """
        self.conversation_client = ConversationV1(
            username=conversation_username,
            password=conversation_password,
            version='2016-07-11'
        )
        self.conversation_workspace_id = conversation_workspace_id
        self.conversation_context = None

    def process_message(self, message):
        """
        Process the message entered by the user.
        Parameters
        ----------
        message - The message entered by the user
        """
        conversation_response = None
        try:
            conversation_response = self.send_request_to_watson_conversation(message, self.conversation_context)
            reply = self.handle_response_from_watson_conversation(message, conversation_response)
            self.conversation_context = conversation_response['context']
            return reply
        except Exception:
            print(sys.exc_info())
            # clear state and set response
            reply = "Sorry, something went wrong!"
            return reply

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

    def handle_response_from_watson_conversation(self, message, conversation_response):
        """ 
        Takes the response from Watson Conversation, performs any additional steps
        that may be required, and returns the reply that should be sent to the user.
        Parameters
        ----------
        message - The message sent by the user
        conversation_response - The response from Watson Conversation
        """
            
        # In some cases we just return the response defined in Watson Conversation (handled by handleDefaultMessage).
        # In others we need to take special steps to return a customized response.
        # For example, we may need to return the results of a databse lookup or 3rd party API call.
        # Here we look to see if a custom "action" has been configured in Watson Conversation and if we
        # need to return a custom response based on the action. 
        if 'context' in conversation_response.keys() and 'action' in conversation_response['context'].keys():
            action = conversation_response['context']['action']
        else:
            action = None
        if action == "xxx":
            return self.handle_xxx_message(conversation_response)
        else:
            return self.handle_default_message(conversation_response)
        
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

    def handle_xxx_message(self, conversation_response):
        """
        Returns a custom response to the user.
        Parameters
        ----------
        conversation_response - The response from Watson Conversation
        """
        # entity = conversation_response['entities'][0]['value']
        # contextVar = conversation_response['context']['var']
        reply = 'TBD'
        return reply