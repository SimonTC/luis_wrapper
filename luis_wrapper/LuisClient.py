import requests
from config import APP_ID, SUBSCRIPTION_KEY
from LuisResponse import Response


class Client:

    _base_url_map = (
        'https://api.projectoxford.ai/luis/v2.0/apps/{}?subscription-key={}&q={}&verbose={}')

    last_response = None
    current_response = None

    def __init__(self, app_id: str, subscription_key: str):
        self.app_id = app_id
        self.subscription_key = subscription_key

    def reply(self, text: str, context):
        pass

    """
    set verbose to false if you just want to receive the most important information
    """
    def analyze(self, text: str, verbose: bool = True) -> Response:
        self.last_response = self.current_response
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty")
        url = self._base_url_map.format(
            self.app_id, self.subscription_key, text, verbose)
        self.current_response = self._get_response(url)
        return self.current_response

    def _get_response(self, url: str) -> Response:
        r = requests.get(url)
        r.raise_for_status();
        return Response(r.json())



if __name__ == '__main__':
    client = Client(APP_ID, SUBSCRIPTION_KEY)
    response = client.analyze("This")
    print(response.top_scoring_intent)
