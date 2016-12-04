import pytest
import os
from distutils import dir_util
from luis_wrapper.LuisResponse import *
import json

@pytest.fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    Source: http://stackoverflow.com/a/29631801
    """

    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return str(tmpdir)

@pytest.fixture
def data_dict(datadir):
    dict_ = {}
    for file in os.listdir(datadir):
        if file.endswith(".json"):
            path = os.path.join(datadir, file)
            key = file[:-5]
            dict_[key] = create_json(path)
    return dict_


def create_json(path):
    with open(path, 'r') as f:
        dict_ = json.load(f)
    return dict_


@pytest.mark.parametrize("class_, attribute_names", [
    (Response, ['json', 'query', 'top_scoring_intent', 'entities', 'intents']),
    (Intent, ['name', 'score', 'actions', 'triggered_action']),
    (BaseEntity, ['type', 'value', 'resolution']),
    (Entity, ['type', 'value', 'start_index', 'end_index', 'score', 'resolution']),
    (Action, ['name', 'triggered', 'parameters']),
    (Dialog, ['context_id', 'status', 'prompt', 'name', 'parameter_type']),
    (Parameter, ['name', 'type', 'required', 'value'])
])
def test_Given_NoMissingParameters_When_Initializing_Then_NoAttributesAreNone(data_dict, class_, attribute_names):
    dict_ = data_dict[class_.__name__]['NoMissingParameters']
    obj = class_(dict_)
    for attr in attribute_names:
        assert obj.__getattribute__(attr) is not None


@pytest.mark.parametrize("class_, attribute_names, optional_attributes", [
    (Response, ['json', 'query', 'top_scoring_intent', 'entities', 'intents'], ['dialog']),
    (Intent, ['name', 'score', 'actions', 'triggered_action'], ['actions']),
    (BaseEntity, ['type', 'value', 'resolution'], ['resolution']),
    (Parameter, ['name', 'type', 'required', 'value'], ['value'])
])
def test_Given_MissingOptionalParameters_When_Initializing_Then_TheyAreSetToNone(data_dict, class_, attribute_names, optional_attributes ):
    for optional_attr in optional_attributes:
        dict_ = data_dict[class_.__name__]['NoMissingParameters']
        dict_.pop(optional_attr)
        obj = class_(dict_)
        assert obj.__getattribute__(optional_attr) is None

class TestResponse:

    def test_Given_DialogExists_When_InitializingResponse_Then_NeedMoreInfoFlagIsSetCorrectly(self, data_dict):
        dict_ = data_dict['Response']['NoMissingParameters']

        # Test when status is finished
        response = Response(dict_)
        assert not response.need_more_info

        #Test when status is Question
        dict_['dialog'] = data_dict['Dialog']['NoMissingParameters']
        response = Response(dict_)
        assert response.need_more_info

    def test_Given_DialogDoesNotExist_When_InitializingResponse_Then_NeedMoreInfoFlagIsSetToFalse(self, data_dict):
        dict_ = data_dict['Response']['NoMissingParameters']
        dict_.pop("dialog")
        # Test when status is finished
        response = Response(dict_)
        assert not response.need_more_info


class TestDialog:

    def test_Given_StatusIsFinished_When_Initializing_Then_SomeParametersAreSetToNone(self, data_dict):
        dict_ = data_dict['Dialog']['NoMissingParameters']
        dict_['status'] = "Finished"
        dict_.pop('prompt')
        dict_.pop('parameterName')
        dict_.pop('parameterType')
        dialog = Dialog(dict_)
        for attr in ['prompt', 'name', 'parameter_type']:
            assert dialog.__getattribute__(attr) is None
