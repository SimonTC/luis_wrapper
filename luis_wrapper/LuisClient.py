import requests
import config
from LuisResponse import Response
import urllib

class Conversation:
    _base_url_map = (
        'https://api.projectoxford.ai/luis/v2.0/apps/{}?subscription-key={}&q={}&verbose={}')

    _reply_url_map = '&contextid={}&forceset={}'

    verbose = True
    app_id = ''
    subscription_key = ''
    conversation_id = None
    responses = []
    last_response = None

    cancelation_words = {'cancel', 'stop'}

    current_response = None

    def __init__(self, app_id: str, subscription_key: str, verbose=True):
        self.app_id = app_id
        self.subscription_key = subscription_key
        self.verbose = verbose

    def _build_reply_url(self, text: str, parameter_name: str) -> str:
        url = self._build_base_url(text)
        reply_part = self._reply_url_map.format(
            self.conversation_id, parameter_name)
        url += reply_part
        return url

    def _clean_text(self, text: str) -> str:
        clean_text = text.strip()
        clean_text = urllib.parse.quote_plus(clean_text)
        return clean_text

    def _build_base_url(self, text: str) -> str:
        if not text:
            raise ValueError("Text cannot be empty")
        url = self._base_url_map.format(
            self.app_id, self.subscription_key, text, self.verbose)
        return url

    def _get_response(self, url: str) -> Response:
        r = requests.get(url)
        r.raise_for_status()
        return Response(r.json())

    def reply(self, text: str, parameter_name: str, conversation_id: str = None) -> Response:
        current_conversation = conversation_id or self.conversation_id
        if not current_conversation:
            raise TypeError("Conversation id must be set")
        text = self._clean_text(text)
        url = self._build_reply_url(text, parameter_name)
        response = self._get_response(url)
        self.responses.append(response)
        self.last_response = response
        return response

    def ask(self, text: str) -> Response:
        text = self._clean_text(text)
        url = self._build_base_url(text)
        response = self._get_response(url)
        if response.need_more_info:
            self.conversation_id = response.dialog.context_id
        self.current_response = response
        self.responses.append(response)
        self.last_response = response
        return response

    def start_conversation(self, text: str) -> Response:
        response = self.ask(text)
        while response.need_more_info:
            text = self.on_need_more_info_default(response)
            if text in self.cancelation_words:
                return None
            parameter_name = response.dialog.parameter_type
            response = self.reply(text, parameter_name)
        return response

    def on_need_more_info_default(self, response: Response) -> str:
        print(response.dialog.prompt)
        answer = input('>> ')
        return answer

class Client:

    def __init__(self, app_id: str, subscription_key: str):
        self.app_id = app_id
        self.subscription_key = subscription_key

    """
    set verbose to false if you just want to receive the most important information
    """
    def analyze(self, text: str, verbose: bool = True) -> Conversation:

        conversation = Conversation(self.app_id, self.subscription_key, verbose=verbose)
        conversation.start_conversation(text)
        return conversation

    def _get_response(self, url: str) -> Response:
        r = requests.get(url)
        r.raise_for_status();
        return Response(r.json())


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

