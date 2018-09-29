"""Root of the ``mixt`` package."""

from os import path

import pkg_resources
from setuptools.config import read_configuration

from . import exceptions, html as h  # noqa: F401
from .element import Element, ElementProxy  # noqa: F401
from .internal import dev_mode  # noqa: F401,F403  # pylint: disable=wildcard-import
from .internal.base import BaseContext, EmptyContext, Ref  # noqa: F401
from .internal.collectors import CSSCollector, JSCollector  # noqa: F401
from .internal.dev_mode import *  # noqa: F401,F403  # pylint: disable=wildcard-import
from .proptypes import *  # noqa: F401,F403  # pylint: disable=wildcard-import


def _extract_version() -> str:
    """Extract the current version of ``mixt``.

    It will get it from the installed package if any, of from the ``setup.cfg`` file.

    Returns
    -------
    str
        The actual version of the ``mixt`` package.

    """
    try:
        return pkg_resources.get_distribution("mixt").version
    except pkg_resources.DistributionNotFound:
        _conf = read_configuration(
            path.join(path.dirname(__file__), "../../", "setup.cfg")
        )
        return _conf["metadata"]["version"]


__version__ = _extract_version()
