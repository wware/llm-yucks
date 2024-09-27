# python3 -m doctest x.py
import os


def is_truthy(s: str) -> bool:
    """
    Determines if a given string represents a truthy value.

    Args:
        s (str): The input string to check.

    Returns:
        bool: Whether the input string represents a truthy value. This can be
            either an integer that's not zero, or one of the strings "true", "yes", or "1".

    Example:
        >>> is_truthy("123")
        True
        >>> is_truthy("false")
        False
    """
    try:
        return int(s) != 0
    except ValueError:
        return s.lower() in ("true", "yes", "1")


def fetch_env_var(key: str, default="") -> str:
    """
    Retrieves an environment variable by its key.

    Args:
        key (str): The name of the environment variable to retrieve.
        default (str, optional): The value to return if the environment variable
            is not set. Defaults to an empty string.

    Returns:
        str: The value of the environment variable, or the default value if it's not set.

    Example:
        >>> p = fetch_env_var("PATH")
        >>> assert "/usr/bin" in p
        >>> assert ":/bin:" in p
        >>> assert ":/sbin:" in p
        >>> fetch_env_var("NON_EXISTENT_VAR", "default_value")
        'default_value'
    """
    key = key.upper().replace(" ", "_").replace("-", "_")
    return os.environ.get(key, default)


def set_env_var(key: str, value) -> None:
    """
    Sets an environment variable to a given value.

    Args:
        key (str): The name of the environment variable to set.
        value: The value to set the environment variable to.

    Example:
        >>> set_env_var("MY_VAR", "hello")
        >>> assert fetch_env_var("MY_VAR", "nope") == "hello"
    """
    key = key.upper().replace(" ", "_").replace("-", "_")
    os.environ[key] = str(value)


def boolean_env_var(key) -> bool:
    """
    Retrieves an environment variable and interprets its value as a boolean.

    Args:
        key (str): The name of the environment variable to retrieve.

    Returns:
        bool: Whether the environment variable is set to "true", "yes", or "1".

    Example:
        >>> os.environ["MY_BOOL_VAR"] = "1"
        >>> boolean_env_var("MY_BOOL_VAR")
        True
        >>> boolean_env_var("NON_EXISTENT_VAR")
        False
    """
    return is_truthy(fetch_env_var(key, ""))
