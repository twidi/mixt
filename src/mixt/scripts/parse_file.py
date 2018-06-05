#!/usr/bin/env python

"""A script to convert a "mixt" encoded file to a pure python file."""

import sys
from mixt.codec.tokenizer import pyxl_tokenize, pyxl_untokenize


def main() -> None:
    """Convert the file given in argument to pure python and print the output."""
    file = open(sys.argv[1], "r")
    print(pyxl_untokenize(pyxl_tokenize(file.readline)), end="")


if __name__ == "__main__":
    main()
