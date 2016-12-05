import pytest
from luis_wrapper.LuisClient import Client


class TestLuisClient:

    @pytest.fixture
    def client(self):
        app_id = "An app id"
        subscription_key = "A subscription key"
        return Client(app_id, subscription_key)

    def test_ParametetersAreSetCorrectly(self):
        app_id = "An app id"
        subscription_key = "A subscription key"
        client = Client(app_id, subscription_key)
        assert client.app_id == app_id
        assert client.subscription_key == subscription_key

    @pytest.mark.parametrize("input", [
        (''), (' '), ('     ')
    ])
    def test_Given_EmptyString_When_CallingAnalyze_Then_ExceptionIsRaised(self, client, input):
        with pytest.raises(ValueError) as err:
            client.analyze(input)


    def test_Given_NoneAsString_When_CallingAnalyze_Then_ExceptionIsRaised(self, client):
        input = None
        with pytest.raises(ValueError) as err:
            client.analyze(input)

    def test_Given_NonEmptyString_When_CallingAnalyze_Then_ConversationIsReturned(self):
        assert False