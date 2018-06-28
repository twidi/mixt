from mixt import Element


class _Manual(Element):
    class PropTypes:
        id_prefix: str = ''
        h_level: int = 2
        _class: str ="manual"

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        return """
/* <components.manual.base._Manual> */
.doc > .manual:first-child:last-child {
    padding: 5px 0 5px 1em;
    border-radius: 7px 0 0 7px;
}
.manual > .content > p:first-child {
    margin-top: 1em;
}
.manual > .content > p:first-child strong {
    line-height: 1.3;
}

.manual:hover,
.manual:target,
.manual.focus-within {
    background: %(BG2)s;
}
.manual .doc-part:hover,
.manual .doc-part:focus,
.manual .doc-part.focus-within {
    background: %(BG3)s;
}
.manual .doc-part .doc-part:hover,
.manual .doc-part .doc-part:focus,
.manual .doc-part .doc-part.focus-within {
    background: %(BG4)s;
}
.manual .doc-part .doc-part .doc-part:hover,
.manual .doc-part .doc-part .doc-part:focus,
.manual .doc-part .doc-part .doc-part.focus-within {
    background: %(BG5)s;
}
.manual .doc-part .doc-part .doc-part .doc-part:hover,
.manual .doc-part .doc-part .doc-part .doc-part:focus,
.manual .doc-part .doc-part .doc-part .doc-part.focus-within {
    background: %(BG6)s;
}
/* </components.manual.base._Manual> */
        """
