import requests
from luis_wrapper import config
from luis_wrapper.LuisResponse import Response
import urllib

class Conversation:
    id = None
    responses = []

    @property
    def last_response(self):
        return self.responses[-1]

    def __init__(self, initial_response: Response):
        pass

    def conversation_is_finished(self):
        pass

    def add_response(self, response: Response):
        self.responses.append(response)




class LuisClient:

    app_id = None
    subscription_key = None

    def __init__(self, app_id, subscription_key):
        """

        Parameters
        ----------
        app_id: str (GUID)
            ID of the LUIS app
        subscription_key: str (GUID without dashes)
            Subscription key for the LUIS app
        """
        pass

    def analyze(self, text, conversation=None):
        """Send the text to LUIS to be analyzed.

        Request an analysis of the given text from LUIS. If a conversation is given, the text is treated as an
        answer to the last response from LUIS.

        Parameters
        ----------
        text : str
            The text to  be analyzed.
            Cannot be None or only spaces
        conversation : Conversation (None)
            The conversation this request is part of

        Returns
        -------
        Conversation
            The conversation that result from this request to LUIS
        """
        pass