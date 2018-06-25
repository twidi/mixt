# coding: mixt

from mixt import Element, Required, html
from .generic import H


class Intro(Element):
    class PropTypes:
        version: Required[str]

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        return """
/* <components.intro.Intro> */
#intro > h1 {
    line-height: 1.3;
    padding: 0.5em 0;
    background: %(BG9)s;
    color: white;
    text-align: center;
    margin-top: 0;
}
#intro > h1 > span {
    display: block;
    font-size: 60%%;
    font-weight: normal;
}
#intro > p {
    margin-left: 9px;
    margin-right: 9px;
}
/* </components.intro.Intro> */
        """

    def render(self, context):
        return <section id="intro">
            <H level=1>
                Welcome to <strong>MIXT</strong> documentation.
                <span>(Version {self.version})</span>
            </H>
            <p>
                This page holds the documentation about the API of{" "}
                <strong><a href="https://pypi.org/project/mixt/" title="Link to Mixt page on Pypi">Mixt</a></strong>.
                <br />
                And yes, we eat our own dog food: this documentation is auto-generated, via Mixt components.
            </p>
            <p>
                For a complete user-guide on how to use <strong>Mixt</strong>, from the beginning to advanced topics,{" "}
                it is <a href="https://pypi.org/project/mixt/#user-guide" title="mixt user guide">hosted on PyPI</a>.
            </p>
            <hr />
        </section>
