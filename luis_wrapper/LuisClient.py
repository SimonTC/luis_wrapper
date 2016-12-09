import requests
from luis_wrapper import config
from luis_wrapper.LuisResponse import Response
import urllib
import logging
import aiohttp
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


class Conversation:
    """A wrapper class around one conversation with LUIS"""
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
        """Check if more information is needed before this conversation is finished.

        Looks at the status of the last response received.

        Returns
        -------
        bool
            True if no more information is needed
            False if LUIS still needs information
        """
        return not self.last_response.need_more_info

    def add_response(self, response: Response):
        """Add response to the list of responses"""
        logger.debug('Adding response')
        self.responses.append(response)
        logger.debug('Response list length is now {}'.format(len(self.responses)))


class Client:
    """A client used to communicate with a LUIS model"""
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
        Do not give a conversation object if you want to start a new analysis.
        Text sent when a Conversation is given is only used to answer questions asked by the LUIS model.

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
        """Send new query to LUIS"""
        url = self._build_base_url(text)
        response = self._get_response(url)
        return Conversation(response)

    def _reply(self, text: str, conversation: Conversation) -> Conversation:
        """Send QUery to LUIS continuing an ongoing conversation"""
        url = self._build_reply_url(text, conversation.id)
        response = self._get_response(url)
        conversation.add_response(response)
        return conversation

    def _get_response(self, url: str) -> Response:
        """Connect to LUIS and parse response"""
        r = requests.get(url)
        r.raise_for_status()
        return Response(r.json())

    def _clean_text(self, text: str) -> str:
        """Clean text so it can be sent to LUIS"""
        logger.debug('Cleaning {}'.format(text))
        clean_text = text.strip()
        clean_text = urllib.parse.quote_plus(clean_text)
        return clean_text

    def _build_base_url(self, text: str):
        """Build the base url used when sending queries to LUIS"""
        return self._base_url_map.format(self.app_id, self.subscription_key, text)

    def _build_reply_url(self, text: str, conversation_id: str):
        """Build url used for sending queries to LUIS that responds to an earlier response from LUIS"""
        base_url = self._build_base_url(text)
        reply_url = self._reply_url_map.format(conversation_id)
        return '{}{}'.format(base_url, reply_url)


class AsyncClient(Client):

    async def analyze(self, text, conversation=None):
        """Send a async request to LUIS to analyze the given text.

        Request an async analysis of the given text from LUIS. If a conversation is given, the text is treated as an
        answer to the last response from LUIS.
        Do not give a conversation object if you want to start a new analysis.
        Text sent when a Conversation is given is only used to answer questions asked by the LUIS model.

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
        logger.debug('Start analysis of {}'.format(text))
        clean_text = self._clean_text(text)
        if not clean_text:
            logger.debug('Text cannot be empty')
            raise ValueError("Text cannot be empty")
        if conversation:
            reply = await self._reply(clean_text, conversation)
        else:
            reply = await self._ask(clean_text)
        return reply

    async def _ask(self, text: str) -> Conversation:
        """Send new async query to LUIS"""
        logger.debug('Asking LUIS about {}'.format(text))
        url = self._build_base_url(text)
        response = await self._get_response(url)
        return Conversation(response)

    async def _reply(self, text: str, conversation: Conversation) -> Conversation:
        """Send async query to LUIS continuing an ongoing conversation"""
        logger.debug('Replying to LUIS with {}'.format(text))
        url = self._build_reply_url(text, conversation.id)
        response = await self._get_response(url)
        conversation.add_response(response)
        return conversation

    async def _get_response(self, url: str) -> Response:
        """Connect async to LUIS and parse response"""
        logger.debug('Starting async session with LUIS')
        with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    err_message = (
                        'Request to LUIS failed with error code {}'.format(
                            r.status))
                    logger.error(err_message)
                    raise HTTPError(err_message)
                values = await r.json()
                logger.debug('Response received')
                return Response(values)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    client = Client(config.APP_ID, config.SUBSCRIPTION_KEY)
    while True:
        print("What is your command?")
        command = input('>> ')
        if command in ['stop', 'exit']:
            break
        conversation = client.analyze(command)
        while not conversation.conversation_is_finished():
            print(conversation.last_response.dialog.prompt)
            command = input('>> ')
            conversation = client.analyze(command, conversation)
        intent_name = conversation.last_response.top_scoring_intent.name
        print("Your intent was '{}'".format(intent_name))
    print("Conversation with LUIS has stopped")
