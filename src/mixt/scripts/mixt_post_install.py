#!/usr/bin/env python

"""Install the ``mixt.pth`` file to let python understand the ``mixt`` encoding."""

from distutils.sysconfig import get_python_lib
import os.path


PTH_FILENAME = "mixt.pth"
PTH_CONTENT = (
    "import sys; exec('"
    "try:\\n"
    "    import mixt.codec.fast_register\\n"
    "except ImportError:\\n"
    "    pass\\n"
    "')"
)


def main() -> None:
    """Copy the codec register code in a ``mixt.pth`` file in the lib python directory."""
    python_lib = get_python_lib()
    with open(os.path.join(python_lib, PTH_FILENAME), "w") as pth_file:
        pth_file.write(PTH_CONTENT)


if __name__ == "__main__":
    main()
