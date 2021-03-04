from typing import Union


def del_none(d: Union[dict, list]):
    """
    Delete keys with the value ``None`` in a dictionary or list of dictionaries, recursively.

    This alters the input so you may wish to ``copy`` the dict first.
    """
    if isinstance(d, dict):
        for key, value in list(d.items()):
            if value is None:
                del d[key]
            elif isinstance(value, dict):
                del_none(value)
            elif isinstance(value, list):
                del_none(value)
    elif isinstance(d, list):
        for value in d:
            del_none(value)
    return d
