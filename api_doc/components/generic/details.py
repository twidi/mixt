from mixt import Element, html


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

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        return """
/* <components.generic.details.Details> */

details .h {
    margin-top: 0;
    padding: 3px 0;
}
details[open] .h {
    margin-bottom: 1em;
}
details:not([open]) .h {
    margin-bottom: 0;
}
summary {
    cursor: pointer;
    white-space: nowrap;
}
summary .h {
    display: inline-block;
    vertical-align: middle;
    line-height: 1.3;
    white-space: normal;
}
.h + details {
    margin-top: 1em;
}     
details + details, summary + details {
    margin-top: 1em;
}
details > :not(summary) {
    margin-left: 1em;
}
@media (max-width: %(BREAKPOINT)s) {
    details > :not(summary) {
        margin-left: 0.2em;
    }
}

details > div.content > :first-child, 
details > div.content > :first-child > :first-child, 
details > div.content > :first-child > :first-child > :first-child,
details > div.content > :first-child > :first-child > :first-child > :first-child,
details > div.content > :first-child > :first-child > :first-child > :first-child > :first-child,
details > div.content > :first-child > :first-child > :first-child > :first-child > :first-child > :first-child {
    margin-top: 0;
}

details .h:last-child,
details > div.content > p:last-child {
    margin-bottom: 0;
}

details > div.content {
    border-left: solid rgba(0, 0, 0, 0.1) 1px;
    margin-left: 4px;
    padding: 5px 0 5px 1em;
}
@media (max-width: %(BREAKPOINT)s) {
    details > div.content {
        margin-left: 3px;
        padding-left: 0.2em;
    }
}
details:hover > div.content,
details:focus > div.content,
details.focus-within > div.content {
    border-left: solid transparent 1px;
}
/* </components.generic.details.Details> */
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

