LUIS wrapper
============

A python wrapper for the Microsoft LUIS service (http:www.luis.ai).
Use this wrapper to easily connect to LUIS and parse the responses returned from your models.


Usage example
-------------
* Create user at luis.ai
* Create new model
* Grab app id and subscription key for your model
* In python ::

    from luis_wrapper.LuisClient import Client

    app_id = "App id goes here"
    subscription_key = "Subscription key goes here"

    client = Client(app_id, subscription_key)
    conversation = client.analyze("Hello World")
    intent_name = conversation.last_response.top_scoring_intent.name
    print("Your intent was '{}'".format(intent_name))

Contribute
----------

- Issue Tracker: github.com/SimonTC/luis_wrapper/issues
- Source Code: github.com/SimonTC/luis_wrapper/


License
-------

The project is licensed under the MIT license.
See LICENSE for details.
