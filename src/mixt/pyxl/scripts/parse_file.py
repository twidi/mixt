#!/usr/bin/env python

import sys
from mixt.pyxl.codec.tokenizer import pyxl_tokenize, pyxl_untokenize


def main():
    f = open(sys.argv[1], "r")
    print(pyxl_untokenize(pyxl_tokenize(f.readline)), end="")


if __name__ == "__main__":
    main()
