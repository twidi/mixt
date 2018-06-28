from docutils import nodes
from docutils.examples import internals
import os.path

from mixt import h

from ..generic.rst import htmlize_node, htmlize_rst
from .base import _Manual


class UserGuide(_Manual):

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
        section = [
            child for child
            in document.children
            if (child.attributes.get('names') or [''])[0] == 'user guide'
        ][0]
        section.children.pop(0)  # remove the title

        section.children[0].children[0:0] = [
            nodes.paragraph(
                text="""\
This user-guide will introduce you through the whole set of features provided by Mixt, step by step.  
"""
            ),
        ]


        return h.Div()(
            htmlize_node(section),
            htmlize_rst(
# language=RST
"""
****
Next
****

As a next step, you may want to read `the API documentation <api.html>`_.
"""
            )
        )
