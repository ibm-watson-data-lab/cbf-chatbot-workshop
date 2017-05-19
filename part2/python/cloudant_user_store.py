import time

from cloudant.client import Cloudant
from cloudant.query import Query


class CloudantUserStore(object):

    def __init__(self, cloudant_username, cloudant_password, cloudant_url, db_name):
        """
        Creates a new instance of CloudantUserStore.
        Parameters
        ----------
        cloudant_username - The username for the cloudant instance
        cloudant_password - The password for the cloudant instance
        cloudant_url - The url of the of cloudant instance to connect to
        db_name - The name of the database to use
        """
        if cloudant_url.find('@') > 0:
            prefix = cloudant_url[0:cloudant_url.find('://')+3]
            suffix = cloudant_url[cloudant_url.find('@')+1:]
            cloudant_url = '{}{}'.format(prefix, suffix)
        self.client = Cloudant(cloudant_username, cloudant_password, url=cloudant_url)
        self.db_name = db_name

    def init(self):
        """
        Creates and initializes the database.
        """
        try:
            self.client.connect()
            print('Getting user database...')
            if self.db_name not in self.client.all_dbs():
                print('Creating user database {}...'.format(self.db_name))
                self.client.create_database(self.db_name)
            else:
                print('User database {} exists.'.format(self.db_name))
        finally:
            self.client.disconnect()

    # User

    def add_user(self, user_id):
        """
        Adds a new user to Cloudant if a user with the specified ID does not already exist.
        Parameters
        ----------
        user_id - The ID of the user (typically the ID returned from Slack)
        """
        try:
            self.client.connect()
            return self.client[self.db_name][user_id]
        except KeyError:
            db = self.client[self.db_name]
            doc = {
                '_id': user_id,
                'conversation_context': {}
            }
            return db.create_document(doc)
        finally:
            self.client.disconnect()

    def update_user(self, user, context):
        """
        Updates the user in Cloudant with the latest Watson Conversation context.
        Parameters
        ----------
        userId - The user doc stored in Cloudant
        context - The Watson Conversation context
        """
        try:
            self.client.connect()
            db = self.client[self.db_name]
            doc = db[user['_id']]
            doc['conversation_context'] = context
            return doc.save()
        finally:
            self.client.disconnect()