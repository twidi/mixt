from mixt import Element
from mixt.contrib.css import css_vars, render_css, Modes


class _Manual(Element):
    class PropTypes:
        id_prefix: str = ''
        h_level: int = 2
        _class: str ="manual"

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        colors = context.styles.colors

        _target = "&:hover, &:target, &.focus-within"
        _focus = "&:hover, &:focus, &.focus-within"

        return render_css({
            "/*": f"<{cls.__module__}.{cls.__name__}>",
            ".doc > .manual:first-child:last-child": {
                padding: (5*px, 0, 5*px, 1*em),
                border-radius: (7*px, 0, 0, 7*px),
            },
            ".manual": {
                "> .content": {
                    "> p:first-child": {
                        margin-top: 1*em,
                        strong: {
                            line-height: 1.3,
                        }
                    }
                },
                _target: {
                    background: colors[2]
                },
                ".doc-part": {
                    _focus: {
                        background: colors[3]
                    },
                    ".doc-part": {
                        _focus: {
                            background: colors[4]
                        },
                        ".doc-part": {
                            _focus: {
                                background: colors[5]
                            },
                            ".doc-part": {
                                _focus: {
                                    background: colors[6]
                                },
                            }
                        }
                    }
                },
            },
            "/**": f"</{cls.__module__}.{cls.__name__}>",
        })
