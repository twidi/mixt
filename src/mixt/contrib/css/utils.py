"""Utils for mixt.contrib.css."""

import builtins
import collections
from typing import Callable, Dict, List, Mapping


__IGNORE_BUILTINS: List[str] = ["globals"]

BUILTINS_LIST: List[str] = [
    key
    for key in builtins.__dict__
    if not key.startswith("_") and key == key.lower() and key not in __IGNORE_BUILTINS
]


# pylint: disable=invalid-name
isbuiltin: Callable[[str], bool] = frozenset(BUILTINS_LIST).__contains__


def _dict_merge(dct: Dict, merge_dct: Mapping, update: bool = True) -> Dict:
    """Merge `merge_dct` into `dct`, recursively.

    Inspired by ``dict.update()``, instead of updating only top-level keys,
    ``_dict_merge`` recurses down into dicts nested to an arbitrary depth, updating keys.

    Be careful: if `update` is true, like ``dict.update``, the given dict, `dct`, will be updated.

    If a value is `None` in `merge_dct`, it will be removed from `dct` if it exists, or ignored
    if not.

    Parameters
    ----------
    dct : Dict
        Dict onto which the merge is executed.
    merge_dct : Mapping
        Dict merged into `dct`.
    update : bool
        If ``True``, the default, `dct` is directly updated.

    Returns
    -------
    Dict
        The merged dict. Will be `dct`, updated, if `update` is `True`, or a new dict if `False`.

    Notes
    -----
    Inspired by https://gist.github.com/angstwad/bf22d1822c38a92ec0a9

    """
    if not update:
        dct = dict(dct)

    for key, value in merge_dct.items():
        if (
            key in dct
            and isinstance(dct[key], dict)
            and isinstance(value, collections.Mapping)
        ):
            dct[key] = _dict_merge(dct[key], value, update)
        elif value is None:
            dct.pop(key, None)
        else:
            dct[key] = value

    return dct


def dict_hash(dct: Dict) -> int:
    """Compute the hash of a dict.

    This is done by converting it to a ``frozenset`` as a dict is not hashable per se.

    Parameters
    ----------
    dct : Dict
        The dict to hash

    Returns
    -------
    int
        The hashed value of the dict.

    """
    return hash(
        frozenset(
            (
                key,
                dict_hash(value)
                if isinstance(value, dict)
                else tuple(value)
                if isinstance(value, list)
                else value,
            )
            for key, value in dct.items()
        )
    )
