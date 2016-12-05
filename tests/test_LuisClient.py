import pytest
from luis_wrapper.LuisClient import LuisClient, Conversation
from luis_wrapper.LuisResponse import Response, Dialog
from unittest.mock import MagicMock



@pytest.fixture
def response(monkeypatch):
    monkeypatch.setattr('test_LuisClient.Response', MagicMock(Response))
    return Response

@pytest.fixture
def conversation(response):
    return Conversation(response)

@pytest.fixture
def client():
    app_id = "An app id"
    subscription_key = "A subscription key"
    return LuisClient(app_id, subscription_key)

class TestLuisClient:

    def test_ParametetersAreSetCorrectly(self):
        app_id = "An app id"
        subscription_key = "A subscription key"
        client = LuisClient(app_id, subscription_key)
        assert client.app_id == app_id
        assert client.subscription_key == subscription_key

    @pytest.mark.parametrize("id, key, expected_message", [
        (None, "A key", "App id cannot be None"),
        ("", "A key", "App id cannot be empty"),
        ("  ", "A key", "App id cannot be empty"),
        ("An app id", None, "Subscription key cannot be None"),
        ("An app id", "", "Subscription key cannot be empty"),
        ("An app id", " ", "Subscription key cannot be empty")
    ])
    def test_Given_MissingOrEmptyParameterGiven_When_Initializing_Then_ExceptionIsRaised(self, id, key, expected_message):
        with pytest.raises(ValueError) as err:
            LuisClient(id, key)
        assert expected_message in str(err)

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

    def test_Given_NonEmptyString_When_CallingAnalyze_Then_ConversationIsReturned(self, client):
        input = "Hello there"
        result = client.analyze(input)
        assert isinstance(result, Conversation)

    def test_Given_ConversationGiven_When_CallingAnalyze_Then_SameConversationIsReturned(self, client, conversation):
        conv = conversation
        new_conversation = client.analyze("Hello", conv)
        assert conv == new_conversation


class TestConversation:

    def test_Given_NewConversation_Then_OnlyOneResponseExistInResponsesList(self, conversation):
        assert len(conversation.responses) == 1

    def test_Given_NewConversation_Then_LastResponseIsSet(self, conversation):
        assert conversation.last_response is None

    def test_Given_InitialResponse_When_Instantiating_Then_ConversationIDIsSetCorrectly(self, monkeypatch, response):
        monkeypatch.setattr('test_LuisClient.Dialog', MagicMock(Dialog))
        conversation_id = "A long GUID"
        d = Dialog
        monkeypatch.setattr(d, 'context_id', conversation_id, raising=False)
        response.dialog = d
        c = Conversation(response)
        assert c.id == conversation_id

    def test_Given_NewResponseAdded_WhenOneResponseAlreadyExists_Then_ResponseListAndLastResponseIsUpdated(self, monkeypatch, conversation):
        monkeypatch.setattr('test_LuisClient.Response', MagicMock(Response))
        r = Response
        old_response = conversation.last_response
        lenght_before = len(conversation.responses)
        conversation.add_response(r)
        new_response = conversation.last_response
        length_after = len(conversation.responses)
        assert old_response != new_response
        assert length_after == lenght_before + 1

    def test_IsConversationFinishedCorrectlyRead(self, monkeypatch, response):
        response.need_more_info = True
        c = Conversation(response)
        assert not c.conversation_is_finished()
        monkeypatch.setattr('test_LuisClient.Response', MagicMock(Response))
        r = Response
        r.need_more_info = False
        c.add_response(r)
        assert c.conversation_is_finished()
