import json
import time

from cloudant.query import Query
from cloudant.client import Cloudant


class CloudantDialogStore(object):

    def __init__(self, cloudant_dialogname, cloudant_password, cloudant_url, db_name):
        """
        Creates a new instance of CloudantDialogStore.
        Parameters
        ----------
        cloudant_dialogname - The dialogname for the cloudant instance
        cloudant_password - The password for the cloudant instance
        cloudant_url - The url of the of cloudant instance to connect to
        db_name - The name of the database to use
        """
        if cloudant_url.find('@') > 0:
            prefix = cloudant_url[0:cloudant_url.find('://')+3]
            suffix = cloudant_url[cloudant_url.find('@')+1:]
            cloudant_url = '{}{}'.format(prefix, suffix)
        self.client = Cloudant(cloudant_dialogname, cloudant_password, url=cloudant_url)
        self.db_name = db_name

    def init(self):
        """
        Creates and initializes the database.
        """
        try:
            self.client.connect()
            print('Getting dialog database...')
            if self.db_name not in self.client.all_dbs():
                print('Creating dialog database {}...'.format(self.db_name))
                self.client.create_database(self.db_name)
            else:
                print('Dialog database {} exists.'.format(self.db_name))
        finally:
            self.client.disconnect()

    def add_conversation(self, user_id):
        """
        Adds a new conversation to Cloudant.
        Parameters
        ----------
        user_id - The ID of the user
        """
        try:
            self.client.connect()
            db = self.client[self.db_name]
            conversation_doc = {
                'userId': user_id,
                'date': int(time.time()*1000),
                'dialogs': []
            }
            return db.create_document(conversation_doc)
        finally:
            self.client.disconnect()

    def add_dialog(self, conversation_id, dialog):
        """
        Adds a new dialog to the conversation.
        Parameters
        ----------
        conversation_id - The ID of the conversation in Cloudant
        dialog - The dialog to add to the conversation
        """
        try:
            self.client.connect()
            db = self.client[self.db_name]
            converation_doc = db[conversation_id]
            converation_doc['dialogs'].append(dialog)
            return converation_doc.save()
        finally:
            self.client.disconnect()