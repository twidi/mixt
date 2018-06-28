from docutils import nodes
from docutils.examples import internals
import os.path

from mixt import h

from ..generic.rst import htmlize_node, htmlize_rst
from .base import _Manual


class Intro(_Manual):

    def render(self, context):
        readme_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                '../' * (len(__name__.split('.')) - 1),
                'README.rst'
            )
        )

        with open(readme_path) as file:
            content = file.read()

        document = internals(content)[0]
        document.children = [
            child for child
            in document.children[1:]  # remove the title
            if (child.attributes.get('names') or [''])[0] not in ('user guide', 'api')
        ]

        document.children[0].children[0:0] = [
            nodes.strong(text="MIXT"),
            nodes.Text(": "),
        ]

        return h.Div()(
            htmlize_node(document),
            htmlize_rst(
# language=RST
"""
**********
User guide
**********

As a next step, you may want to read `the user guide <user-guide.html>`_.

***
API
***

And then you can continue by reading `the API documentation <api.html>`_.
"""
            )
        )
