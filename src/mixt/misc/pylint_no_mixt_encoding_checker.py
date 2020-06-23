"""Fake plugin to allow pylint to work with mixt encoded files with multilines-html.

The ``EncodingChecker`` pylint linter try to encode files line by line, but the ``mixt`` codec
cannot do that as it have to find all closing tags, and they may be not on the same line.

So for ``mixt`` encoded files, we tell this linter to no trying to decode it and assume its
unicode.

It's done via ``patchy``, a controversial way to monkey-patch, but:
1. it works.
2. it is clearly readable.

"""

from typing import Any

import patchy
from pylint.checkers.misc import EncodingChecker


patchy.patch(
    EncodingChecker._check_encoding,
    """\
@@ -1,4 +1,6 @@
 def _check_encoding(self, lineno, line, file_encoding):
+    if file_encoding == 'mixt':
+        return line.decode()
     try:
         return line.decode(file_encoding)
     except UnicodeDecodeError as ex:
    """,
)


def register(  # pylint: disable=missing-param-doc,missing-type-doc,unused-argument
    linter: Any,
) -> None:
    """Needed for pylint, even if we do nothing with it."""
