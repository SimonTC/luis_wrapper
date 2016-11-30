import pytest
from luis_wrapper import LuisResponse


def test_create_instance_create_correct_class():
    expected_class = str
    value_dict = {'key': 'value'}
    observed_object = LuisResponse._create_instance(expected_class, value_dict, 'key')
    assert isinstance(observed_object, expected_class)


def test_when_key_do_not_exist_no_class_is_created():
    value_dict = {'key': 'value'}
    observed_object = LuisResponse._create_instance(str, value_dict, 'Nokey')
    assert not observed_object


def test_when_key_do_exist_class_is_created():
    value_dict = {'key': 'value'}
    observed_object = LuisResponse._create_instance(str, value_dict, 'key')
    assert observed_object
    assert isinstance(observed_object, str)
    assert observed_object == value_dict['key']


def test_when_list_is_expected_list_is_created():
    value_dict = {'key': ['value1', 'value2']}
    observed_object = LuisResponse._create_instance(str, value_dict, 'key', True)
    assert isinstance(observed_object, list)
    assert len(observed_object) == 2


def test_no_list_created_if_list_not_expected():
    value_dict = {'key': 'value1'}
    observed_object = LuisResponse._create_instance(str, value_dict, 'key')
    assert not isinstance(observed_object, list)


def test_exception_is_raised_if_list_is_given_when_not_expected():
    value_dict = {'key': ['value1', 'value2']}
    with pytest.raises(TypeError) as err:
        LuisResponse._create_instance(str, value_dict, 'key', False)
    assert 'Expected a single element but was given a list' in str(err.value)


def test_exception_is_raised_if_no_list_is_given_when_expected():
    value_dict = {'key': 'value1'}
    with pytest.raises(TypeError) as err:
        LuisResponse._create_instance(str, value_dict, 'key', True)
    assert 'Expected a list but was given a single element' in str(err.value)


def test_exception_is_raised_if_dictionary_is_none():
    value_dict = None
    with pytest.raises(TypeError) as err:
        LuisResponse._create_instance(str, value_dict, 'key', True)
    assert 'Value_dict cannot be None' in str(err.value)


def test_no_class_created_if_value_is_none():
    value_dict = {'key': None}
    observed_object = LuisResponse._create_instance(str, value_dict, 'key')
    assert not observed_object