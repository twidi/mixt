#!/usr/bin/env python

"""A script to convert a "mixt" encoded file to pure python and execute it.

Can take the path to the python file as argument, , ``-c`` to read the code following, or
``-`` to read from stdin.

No need for the `# coding: mixt` header or the `from mixt import html` import line.

"""

from io import StringIO
import sys

from mixt import html  # noqa: F401  # pylint: disable=unused-import
from mixt.codec.tokenizer import pyxl_tokenize, pyxl_untokenize


def main() -> None:
    """Convert the file given in argument to pure python and execute the output."""
    name = (
        "mixt"
        if sys.argv[0] == "mixt" or sys.argv[0].endswith("/mixt")
        else sys.argv[0]
    )

    usage = f"""\
Convert mixt encoded python to pure python, executing the resulting python.

Usage:
    {name} path/to/script.py [args...]
    {name} -c 'some python code' [args...]
    echo "some python code" | {name} -  [args...]
"""

    if len(sys.argv) >= 2 and sys.argv[1] == "-":
        file = sys.stdin
    elif len(sys.argv) >= 3 and sys.argv[1] == "-c":
        file = StringIO(sys.argv[2])
        del sys.argv[2:3]  # remove code to execute from args
    elif len(sys.argv) < 2:
        print(usage, file=sys.stderr)
        sys.exit(1)
    else:
        global __file__  # let the executed script know itself  # noqa: B950  # pylint: disable=redefined-builtin,global-statement
        __file__ = file = sys.argv[1]  # type: ignore

    del sys.argv[1:2]  # remove path or -/-c args from args

    with open(file, "r") if isinstance(file, str) else file as buffer:  # type: ignore
        # Use globals as our "locals" dictionary so that something
        # that tries to import __main__ (e.g. the unittest module)
        # will see the right things.
        exec(pyxl_untokenize(pyxl_tokenize(buffer.readline)), globals(), globals())  # noqa: B950  # pylint: disable=exec-used


if __name__ == "__main__":
    main()
