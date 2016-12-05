import requests
from luis_wrapper import config
from luis_wrapper.LuisResponse import Response
import urllib
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Conversation:

    @property
    def last_response(self) -> Response:
        return self.responses[-1]

    def __init__(self, initial_response: Response):
        logger.debug('Initializing Conversation')
        self.responses = []
        self.add_response(initial_response)
        logger.debug('number of responses after adding response: {}'.format(len(self.responses)))
        try:
            self.id = initial_response.dialog.context_id
        except AttributeError:
            self.id = None

    def conversation_is_finished(self) -> bool:
        return not self.last_response.need_more_info

    def add_response(self, response: Response):
        logger.debug('Adding response')
        self.responses.append(response)
        logger.debug('Response list length is now {}'.format(len(self.responses)))


class Client:
    _base_url_map = (
        'https://api.projectoxford.ai/luis/v2.0/apps/'
        '{}?subscription-key={}&q={}&verbose=True')

    _reply_url_map = '&contextid={}'  # There is also a forceset parameter used when replying, but it doesn't seem
                                      # to be used Set it with &forceset={}

    def __init__(self, app_id, subscription_key):
        """

        Parameters
        ----------
        app_id: str (GUID)
            ID of the LUIS app
        subscription_key: str (GUID without dashes)
            Subscription key for the LUIS app
        """
        if not app_id or app_id.strip() == '':
            raise ValueError('App id cannot be empty or None')
        if not subscription_key or subscription_key.strip() == '':
            raise ValueError('Subscription key cannot be empty or None')
        self.app_id = app_id
        self.subscription_key = subscription_key

    def analyze(self, text, conversation=None) -> Conversation:
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
        clean_text = self._clean_text(text)
        if not clean_text:
            raise ValueError("Text cannot be empty")
        if conversation:
            reply = self._reply(clean_text, conversation)
        else:
            reply = self._ask(clean_text)
        return reply

    def _ask(self, text: str) -> Conversation:
        url = self._build_base_url(text)
        response = self._get_response(url)
        return Conversation(response)

    def _reply(self, text: str, conversation: Conversation) -> Conversation:
        url = self._build_reply_url(text, conversation.id)
        response = self._get_response(url)
        conversation.add_response(response)
        return conversation

    def _get_response(self, url: str) -> Response:
        r = requests.get(url)
        r.raise_for_status()
        return Response(r.json())

    def _clean_text(self, text: str) -> str:
        clean_text = text.strip()
        clean_text = urllib.parse.quote_plus(clean_text)
        return clean_text

    def _build_base_url(self, text: str):
        return self._base_url_map.format(self.app_id, self.subscription_key, text)

    def _build_reply_url(self, text: str, conversation_id: str):
        base_url = self._build_base_url(text)
        reply_url = self._reply_url_map.format(conversation_id)
        return '{}{}'.format(base_url, reply_url)