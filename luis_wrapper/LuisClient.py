import requests
from config import APP_ID, SUBSCRIPTION_KEY


class Client:

    _base_url_map = (
        'https://api.projectoxford.ai/luis/v2.0/apps/{}?subscription-key={}&q={}')

    def __init__(self, app_id: str, subscription_key: str):
        self.app_id = app_id
        self.subscription_key = subscription_key

    def reply(self, text: str, context):
        pass

    def analyze(self, text: str):
        url = self._base_url_map.format(
            self.app_id, self.subscription_key, text)
        r = requests.get(url)
        print(r)


if __name__ == '__main__':

    client = Client(APP_ID, SUBSCRIPTION_KEY)
    client.analyze("This")
