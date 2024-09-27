import os
from unittest.mock import patch
import pytest


@pytest.mark.parametrize("input_value, expected", [
    ("123", True),
    ("false", False),
    ("yes", True),
    ("0", False),
])
def test_is_truthy(input_value):
    """
    Test the is_truthy function with different input values.
    """
    assert is_truthy(input_value) == expected


@patch('os.environ')
@pytest.mark.parametrize("key, default, expected", [
    ("PATH", "", "/usr/bin:/bin:/usr/sbin:/sbin"),
    ("NON_EXISTENT_VAR", "default_value", "default_value"),
])
def test_fetch_env_var(mock_environ, key, default, expected):
    """
    Test the fetch_env_var function with different input values.
    """
    mock_environ.get.return_value = expected
    assert fetch_env_var(key, default) == expected


@patch('os.environ')
@pytest.mark.parametrize("key, value", [
    ("MY_VAR", "hello"),
])
def test_set_env_var(mock_environ, key, value):
    """
    Test the set_env_var function.
    """
    set_env_var(key, value)
    assert mock_environ[key] == str(value)


@patch('os.environ')
@pytest.mark.parametrize("key, expected", [
    ("MY_BOOL_VAR", True),
    ("NON_EXISTENT_VAR", False),
])
def test_boolean_env_var(mock_environ, key, expected):
    """
    Test the boolean_env_var function.
    """
    if key == "MY_BOOL_VAR":
        mock_environ[key] = "true"
    else:
        assert not key in os.environ
    assert boolean_env_var(key) == expected
