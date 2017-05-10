'use strict';

const cloudant = require('cloudant');

/**
 * This class is used to store conversation history in Cloudant.
 */
class CloudantDialogStore {

    /**
     * Creates a new instance of CloudantDialogStore.
     * @param {string} cloudantUrl - The url of the of cloudant instance to connect to
     * @param {string} dbName - The name of the database to use
     */
    constructor(cloudantUrl, dbName) {
        this.cloudant = cloudant({
            url: cloudantUrl,
            plugin:'promises'
        });
        this.dbName = dbName;
        this.db = null;
    }

    /**
     * Creates and initializes the database.
     * @returns {Promise.<>}
     */
    init() {
        console.log('Getting dialog database...');
		return this.cloudant.db.list()
            .then((dbNames) => {
                let exists = false;
                for (let dbName of dbNames) {
                    if (dbName == this.dbName) {
                        exists = true;
                    }
                }
                if (!exists) {
                    console.log(`Creating dialog database ${this.dbName}...`);
                    return this.cloudant.db.create(this.dbName);
                }
                else {
                    return Promise.resolve();
                }
            })
            .then(() => {
                this.db = this.cloudant.db.use(this.dbName);
                return Promise.resolve();
            })
			.then(() => {
                // create the date/userId index
				var index = {
					type: 'json',
					index: {
						fields: ['date','userId']
					}
				};
				return this.db.index(index);
            })
            .then(() => {
                return Promise.resolve();
            });
    }

    /**
     * Adds a new conversation to Cloudant.
     * @param userId - The ID of the user.
     * @returns {Promise.<TResult>}
     */
    addConversation(userId) {
        var conversationDoc = {
            userId: userId,
            date: Date.now(),
            dialogs: []
        };
        return this.db.insert(conversationDoc);
    }

    /**
     * Adds a new dialog to the conversation.
     * @param conversationId - The ID of the conversation in Cloudant
     * @param dialog - The dialog to add to the conversation
     * @returns {Promise.<TResult>}
     */
    addDialog(conversationId, dialog) {
        return this.db.get(conversationId)
            .then((conversationDoc) => {
                conversationDoc.dialogs.push(dialog);
                return this.db.insert(conversationDoc);
            });
    }
}

module.exports = CloudantDialogStore;