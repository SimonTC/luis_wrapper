import pytest
import os
from distutils import dir_util
from luis_wrapper import LuisResponse

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

    return tmpdir

def test_Given_EssentialParametersAreMissing_When_InitializingClass_Then_ExceptionIsRaised():
    assert False

def test_Given_NonEssentialParametersAreMissing_When_InitializingClass_Then_ClassIsInitializedCorrectlyWithMissingAttributesSetToNone():
    assert False

def test_Given_AllParametersAreGiven_When_InitializingClass_Then_ClassIsInitializedCorrectlyWithoutAnyNoneValues():
    assert False

def test_Given_NoneObejctIsGiven_When_InitializingClass_Then_ExceptionIsRaised():
    assert False

def test_Given_DialogExists_When_InitializingResponse_Then_NeedMoreInfoFlagIsSetCorrectly():
    assert False