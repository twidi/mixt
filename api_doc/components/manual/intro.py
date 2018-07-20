from docutils import nodes
from docutils.examples import internals
import os.path

from mixt import h

from ..generic.rst import htmlize_node, htmlize_rst
from .base import _Manual


class Intro(_Manual):

    def get_path(self, name):
        return os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                '../' * (len(__name__.split('.')) - 1),
                name
            )
        )

    def render(self, context):
        readme_path = self.get_path('README.rst')

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

        contrib_path = self.get_path(os.path.join('src/mixt/contrib/README.rst'))
        with open(contrib_path) as file:
            contrib_content = file.read()

        contrib_document = internals(contrib_content)[0]

        for section in [child for child in contrib_document.children if isinstance(child, nodes.section)]:
            section_title = section.children[0].rawsource
            link = f'`Read the "mixt.contrib.{section_title}" documentation <contrib-{section_title}.html>`_.'
            link_para = nodes.paragraph()
            link_para.children = internals(link)[0].children
            section.children.append(link_para)

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
            ),
            htmlize_node(contrib_document)
        )
