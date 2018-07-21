# coding: mixt

from mixt import Element, Required, html
from mixt.contrib.css import css_vars, render_css, Modes

from .generic import Details, H


class DocPart(Element):
    class PropTypes:
        id_prefix: str = ''
        kind: Required[str]
        subkind: str
        open: bool = False
        level: Required[int]

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        return render_css({
            "/*": f"<{cls.__module__}.{cls.__name__}>",
            ".doc-part": {
                padding: (5*px, 0, 5*px, 5*px),
                border-radius: (7*px, 0, 0, 7*px),
                -moz-outline-radius: (7*px, 0, 0, 7*px),
                -webkit-outline-radius: (7*px, 0, 0, 7*px),
                outline-radius: (7*px, 0, 0, 7*px),
                "&[open] > summary > .h": {
                    text-decoration: underline
                }
            },
            "/**": f"</{cls.__module__}.{cls.__name__}>",
        })

    @classmethod
    def render_js_global(cls, context):
        # language=JS
        return """
/* <components.doc.DocPart> */
var DocPart = {
    getFor: function(node) {
        while (node && node.classList) {
            if (node.classList.contains('doc-part')) {
                return node;
            }
            node = node.parentNode;
        }
        return null;
    },    
    onEnter: function(ev) {
        var docPart = DocPart.getFor(ev.currentTarget);
        docPart.dispatchEvent(new CustomEvent("doc_part_enter", {bubbles: true}));
    },    
    onLeave: function(ev) {
        var docPart = DocPart.getFor(ev.currentTarget);
        docPart.dispatchEvent(new CustomEvent("doc_part_leave", {bubbles: true}));
    },    
    onToggle: function(ev) {
        var docPart = DocPart.getFor(ev.currentTarget);
        docPart.dispatchEvent(new CustomEvent("doc_part_toggle", {bubbles: true, detail: {open: ev.currentTarget.open}}));
    },
    init: function() {
        var docParts = document.querySelectorAll('.doc-part');
        for (var i = 0; i < docParts.length; i++) { 
            var docPart = docParts[i];
            docPart.addEventListener('mouseenter', DocPart.onEnter);  
            docPart.addEventListener('mouseleave', DocPart.onLeave);  
        }
        setTimeout(function() {
            for (var i = 0; i < docParts.length; i++) { 
                var docPart = docParts[i];
                if (Details.matches(docPart)) {
                    docPart.addEventListener('toggle', DocPart.onToggle);
                    var linkedDetails = Details.getLinked(docPart);
                    if (linkedDetails) {
                        linkedDetails.addEventListener('toggle', DocPart.onToggle);
                    }
                } 
            }
        }, 500);
    }
};
DocPart.init();
/* </components.doc.DocPart> */
        """

    def render(self, context):

        kind = self.kind
        subkind = self.prop("subkind", "")
        id = self.id_prefix
        if subkind:
            id = f"{id}-{subkind}" if id else subkind

        header = self.children(selector=DocHeader)[0]
        content = self.children(selector=DocHeader, exclude=True)

        classes = ["doc-part"]
        menu_classes = [f"menu-{kind}"]
        if subkind:
            classes.extend([f"{kind}-doc-part", f"{kind}-{subkind}"])
            menu_classes[0] += f"-{subkind}"
        else:
            classes.append(kind)

        if header.menu_class:
            menu_classes.append(header.menu_class)

        return <Details id={id} class={' '.join(classes)} tabindex=-1 open={self.open}>
            <summary>
                <H
                    menu={header.menu}
                    level={self.level}
                    menu-link="#{id}"
                    menu-class={' '.join(menu_classes)}
                >
                    {header}
                </H>
            </summary>
            {content}
        </Details>


class DocHeader(Element):
    class PropTypes:
        menu: Required[str]
        menu_class: str = ''

