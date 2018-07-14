from mixt import Element, html
from mixt.contrib.css import css_vars, render_css, Modes


class Details(Element):
    class PropTypes(html.Details.PropTypes):
        pass

    @classmethod
    def render_js_global(cls, context):
        # language=JS
        return """
/* <components.generic.details.Details> */
var Details = {
    lastNodeToFocus: null,
    lastNodeToScrollTo: null,
    matches: function(node) {
        return node.matches && node.matches('details');
    },
    getLinked: function(node) {
        var linked = node.querySelector('details.linked-to-parent');
        return (linked && linked.parentNode && linked.parentNode.parentNode && linked.parentNode.parentNode === node) ? linked : null;
    },
    openFor: function(element, parents_only) {
        if (Details.matches(element) && !element.open) {
            if (!parents_only) {
                element.open = true;
                opened = true;
            }
            parents_only = false
        }
        if (element.parentNode) {
            Details.openFor(element.parentNode, parents_only);
        }
    },
    focusNode: function(node) {
        Details.lastNodeToFocus = node;
        setTimeout(function() {
            if (node !== Details.lastNodeToFocus) { return; }
            node.focus();
        }, 100);
    },
    scrollIntoView: function(node) {
        Details.lastNodeToScrollTo = node;
        setTimeout(function() {
            if (node !== Details.lastNodeToScrollTo) { return; }
            scrollIntoView(node, {
                behavior: 'smooth',
                scrollMode: 'if-needed',
                block: 'start',
                inline: 'nearest',
            });
            Details.focusNode(node);
        }, 10);
    },
    onHashChange: function () {
      var hash = location.hash.substring(1);
      if (hash) {
        var node = document.getElementById(hash);
        if (node) {
            Details.openFor(Details.getLinked(node) || node);
            Details.scrollIntoView(node);
        } 
      }
    },
    init: function() {
        window.addEventListener('hashchange', Details.onHashChange);
        if (location.hash) { Details.onHashChange(); }
    }
};
Details.init();
/* </components.generic.details.Details> */
        """

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_pycss_global(cls, context):
        return {
            details: {
                ".h": {
                    margin-top: 0,
                    padding: (3*px, 0),
                    margin-bottom: 0,
                },
                "&[open]": {
                    ".h": {
                        margin-bottom: 1*em,
                    }
                },
                ".h:last-child": {
                    margin-bottom: 0,
                },
                "details + &, summary + &": {
                    margin-top: 1*em,
                },
                "> :not(summary)": {
                    margin-left: 1*em,
                    media({max-width: context.styles.breakpoint}): {
                        margin-left: 0.2*em,
                    }
                },
                "> div.content": {
                    border-left: (solid, rgba(0, 0, 0, 0.1), 1*px),
                    margin-left: 4*px,
                    padding: (5*px, 0, 5*px, 1*em),
                    (" > :first-child" * nb for nb in b.range(1, 7)): {
                        margin-top: 0,
                    },
                    "> p:last-child": {
                        margin-top: 0,
                    },
                    media({max-width: context.styles.breakpoint}): {
                        margin-left: 3*px,
                        padding-left: 0.2*em,
                    }
                },
            },
            summary: {
                cursor: pointer,
                white-space: nowrap,
                ".h": {
                    display: inline-block,
                    vertical-align: middle,
                    line-height: 1.3,
                    white-space: normal,
                },
            },
            ".h + details": {
                margin-top: 1*em,
            },
            "&:hover, &:focus, &.focus-within": {
                "> div.content": {
                    border-left: (solid, transparent, 1*px),
                }
            }
        }

    @classmethod
    def render_css_global(cls, context):
        css = render_css((cls.render_pycss_global(context)))
        return f"""
/* <{cls.__module__}.{cls.__name__}> */
{css}
/* </{cls.__module__}.{cls.__name__}> */
"""

    def render(self, context):
        summary = self.children('summary')
        children = self.children('summary', exclude=True)
        if len(children) == 1:
            if not children[0].has_class('content'):
                children[0].prepend_class('content')
        else:
            children = html.Div(_class="content")(
                children
            )
        return html.Details(**self.props)(
            summary, children
        )

