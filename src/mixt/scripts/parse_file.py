#!/usr/bin/env python

"""A script to convert a "mixt" encoded file to a pure python file.

Can take the path to the python file as argument, , ``-c`` to read the code following, or
``-`` to read from stdin.

"""

from io import StringIO
import sys

from mixt.codec.tokenizer import pyxl_tokenize, pyxl_untokenize


def main() -> None:
    """Convert the file given in argument to pure python and print the output."""
    name = "parse-mixt" if sys.argv[0].endswith("parse-mixt") else sys.argv[0]

    usage = f"""\
Convert mixt encoded python to pure python, printing it on standard output.

Usage:
    {name} path/to/script.py
    {name} -c 'some python code'
    echo "some python code" | {name} -
"""

    if len(sys.argv) == 2 and sys.argv[1] == "-":
        file = sys.stdin
    elif len(sys.argv) == 3 and sys.argv[1] == "-c":
        file = StringIO(sys.argv[2])
    elif len(sys.argv) != 2:
        print(usage, file=sys.stderr)
        sys.exit(1)
    else:
        file = sys.argv[1]  # type: ignore

    with open(file, "r") if isinstance(file, str) else file as buffer:  # type: ignore
        print(pyxl_untokenize(pyxl_tokenize(buffer.readline)), end="")


if __name__ == "__main__":
    main()
