import requests
from luis_wrapper import config
from luis_wrapper.LuisResponse import Response
import urllib


class Conversation:
    """A wrapper for a conversation with LUIS

    Attributes
    ----------
    verbose: bool
        Flag indicating whether the result returned from LUIS should include all possible Intents (True) or just
        the most likely intent (False)
    app_id : str (GUID)
        ID of the LUIS app
    subscription_key: str (GUID)
        Subscription key for the LUIS app
    conversation_id: str
        ID for the current conversation.
        Is set after the first call to ask() or start_conversation()
    responses: list[Response]
        The list of responses received from LUIS in chronological order with oldest first
    last_response: Response
        The last response received from LUIS
    cancelation_words: list[str]
        List of words used to cancel a request for more information in on_need_more_info_default()

    """
    _base_url_map = (
        'https://api.projectoxford.ai/luis/v2.0/apps/'
        '{}?subscription-key={}&q={}&verbose={}')

    _reply_url_map = '&contextid={}&forceset={}'

    verbose = True
    app_id = ''
    subscription_key = ''
    conversation_id = None
    responses = []
    last_response = None

    cancelation_words = {'cancel', 'stop'}

    def __init__(self, app_id: str, subscription_key: str, verbose=True):
        self.app_id = app_id
        self.subscription_key = subscription_key
        self.verbose = verbose

    def _build_reply_url(self, query: str, parameter_name: str) -> str:
        url = self._build_base_url(query)
        reply_part = self._reply_url_map.format(
            self.conversation_id, parameter_name)
        url += reply_part
        return url

    def _clean_text(self, text: str) -> str:
        clean_text = text.strip()
        clean_text = urllib.parse.quote_plus(clean_text)
        return clean_text

    def _build_base_url(self, query: str) -> str:
        if not query:
            raise ValueError("Text cannot be empty")
        url = self._base_url_map.format(
            self.app_id, self.subscription_key, query, self.verbose)
        return url

    def _get_response(self, url: str) -> Response:
        r = requests.get(url)
        r.raise_for_status()
        return Response(r.json())

    def reply(self,
              response_query: str,
              parameter_name: str,
              conversation_id: str = None) -> Response:
        """Reply to an earlier response from LUIS

        Use this to give further information to LUIS.

        Parameters
        ----------
        response_query
            Query containing the response to the questions asked by LUIS
        parameter_name
            Name of the parameter that is replaced by the query (Not usre this is needed)
        conversation_id
            Id of the conversation being replied to. Can be None if the call to reply is a result of an
            earlier call to ask()

        Returns
        -------
        Response
            The parsed response from LUIS
        Raises
        ------
        TypeError
            If no conversation id is given or set earlier.

        """
        current_conversation = conversation_id or self.conversation_id
        if not current_conversation:
            raise TypeError("Conversation id must be set")
        response_query = self._clean_text(response_query)
        url = self._build_reply_url(response_query, parameter_name)
        response = self._get_response(url)
        self.responses.append(response)
        self.last_response = response
        return response

    def ask(self, query: str) -> Response:
        """Send a query to LUIS

        Use this method if you don't need to check for action fulfillment

        Parameters
        ----------
        query: str
            The query for LUIS. Cannot only consist of spaces or be None

        Returns
        -------
        Response
            The parsed response from LUIS

        """
        query = self._clean_text(query)
        url = self._build_base_url(query)
        response = self._get_response(url)
        if response.need_more_info:
            self.conversation_id = response.dialog.context_id
        self.responses.append(response)
        self.last_response = response
        return response

    def start_conversation(self, query: str) -> Response:
        """Start a new conversation with LUIS

        Will first return when LUIS has all the information it needs or the conversation is canceled

        Parameters
        ----------
        query
            The initial query for LUIS.

        Returns
        -------
        Response
            The parsed final response from LUIS
        """
        response = self.ask(query)
        while response.need_more_info:
            query = self.on_need_more_info_default(response)
            if query in self.cancelation_words:
                return None
            parameter_name = response.dialog.parameter_type
            response = self.reply(query, parameter_name)
        return response

    def on_need_more_info_default(self, response: Response) -> str:
        """The default method run when LUIS need more information

        Parameters
        ----------
        response
            The response triggering the need for more information

        Returns
        -------
            str
                The new query to send back to the LUIS model
        """
        print(response.dialog.prompt)
        answer = input('>> ')
        return answer


class Client:
    """A client used to communicate with a LUIS model

    Attributes
    ----------
    app_id: str (GUID)
        ID of the LUIS app
    subscription_key: str (GUID without dashes)
        Subscription key for the LUIS app
    """

    def __init__(self, app_id: str, subscription_key: str):
        self.app_id = app_id
        self.subscription_key = subscription_key

    def analyze(self, text: str, verbose: bool = True) -> Conversation:
        """Start a conversation with LUIS to analyze the given text

        Parameters
        ----------
        text
            Text to analysze. Cannot be an empty string or only white spaces
        verbose
            Flag indicating whether the result returned from LUIS should include all possible Intents (True) or just
            the most likely intent (False)
        Returns
        -------
        Conversation
            The conversation started by the client
        """
        conversation = Conversation(
            self.app_id, self.subscription_key, verbose=verbose)
        conversation.start_conversation(text)
        return conversation


if __name__ == '__main__':
    client = Client(config.APP_ID, config.SUBSCRIPTION_KEY)
    while True:
        print('What is your command?')
        text = input('>> ')
        if text in {'stop', 'exit'}:
            break
        conversation = client.analyze(text)
        intent_name = conversation.last_response.top_scoring_intent.name
        print('Your intent was {}'.format(intent_name))
