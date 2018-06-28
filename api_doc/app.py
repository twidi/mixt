# coding: mixt

from typing import Dict, List

from mixt import Element, JSCollector, Ref, Required, exceptions, html, __version__
from mixt.internal import collectors, dev_mode

from .components import CSSCollector, Intro, MainMenuCollector, VendoredScripts, TypesetStyle
from .components import manual
from .components.models import Class, Module
from .code_utils import resolve_class, resolve_module
from . import types


PAGES = [
    {
        'title': 'API',
        'slug': 'index',
        'conf': [
            {
                'type': "manual",
                'component': manual.PropTypes
            },
            {
                'type': "class",
                'class': Element,
                'attributes': ['__tag__', '__display_name__'],
                'methods': [
                    'prop', 'prop_name', 'has_prop', 'set_prop', 'unset_prop', 'prop_default',
                    'is_prop_default', 'prop_type', 'is_prop_required', 'set_props', 'props', 'to_string',
                    'children', 'append', 'prepend', 'remove', 'add_class', 'append_class', 'prepend_class',
                    'remove_class', 'has_class', 'classes', 'render', 'prerender', 'postrender',
                    'postrender_child_element', 'add_ref',
                ],
            },
            {
                'type': "class",
                'class': Ref,
                'methods': ['current'],
            },
            {
                'type': "module",
                'module': dev_mode,
                'name': 'dev_mode',
                'functions': [
                    'set_dev_mode', 'unset_dev_mode', 'override_dev_mode', 'in_dev_mode'
                ]
            },
            {
                'type': "manual",
                'component': manual.Context
            },
            {
                'type': "module",
                'module': collectors,
                'name': 'collectors',
                'classes': ['CSSCollector', 'JSCollector'],
            },
            {
                'type': "manual",
                'component': manual.HtmlTags,
            },
            {
                'type': "manual",
                'component': manual.HtmlUtils,
            },
            {
                'type': "module",
                'module': exceptions,
                'name': 'exceptions',
                'classes': [
                    'MixtException', 'ElementError', 'PropError', 'PropTypeError', 'PropTypeChoicesError',
                    'PropTypeRequiredError', 'InvalidPropNameError', 'InvalidPropValueError',
                    'InvalidPropChoiceError', 'InvalidPropBoolError', 'RequiredPropError',
                    'UnsetPropError', 'InvalidChildrenError', 'GeneralParserError',
                    'BadCharError', 'ParserError'
                ],
            },
        ]
    }
]


class Head(Element):

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        return """
/* <app.Head> */
#main-menu {
    position: fixed;
    left: 0;
    top: 0;
    overflow: auto;
    z-index: 1;
    height: 100%%;
}

@media (max-width: %(BREAKPOINT)s) {
    #main-menu {
        width: 2rem;
    }
    #main-menu > ul {
        display: none;
    }
    #main-menu:not(.focus-within) > p {
        transform: rotate(-90deg) translateX(-6rem) translateY(-5px);
        white-space: nowrap;
    }
    #main-menu.focus-within {
        width: auto;
        max-width: 90%%;
    }
    #main-menu.focus-within > ul {
        display: block;
    }
    #main-menu.focus-within:before {
        content: "";
    }
    main {
        margin-left: 2rem;
    }
}

@media not all and (max-width: %(BREAKPOINT)s) {
    #main-menu {
        width: 10rem;
    }
    #main-menu:hover {
        width: auto;
        min-width: 10rem;
        max-width: 90%%;
    }
    main {
        margin-left: 10rem;
    }
}
code {
    font-weight: normal;
}

hr { 
  border: 0; 
  height: 1px; 
  background-image: -webkit-linear-gradient(left, %(BG1)s, %(BG9)s, %(BG1)s);
  background-image: -moz-linear-gradient(left, %(BG1)s, %(BG9)s, %(BG1)s);
  background-image: -ms-linear-gradient(left, %(BG1)s, %(BG9)s, %(BG1)s);
  background-image: -o-linear-gradient(left, %(BG1)s, %(BG9)s, %(BG1)s); 
}
body {
    background: %(BG1)s;
    margin: 0;
}
.doc {
    margin-left: calc(1em + 9px);
    padding-right: 20px;
    margin-bottom: 1em;
}
@media (max-width: %(BREAKPOINT)s) {
    .doc {
        margin-left: calc(0.2em + 9px);
        padding-right: 0;
    }
}
.doc p, .doc .h   {
    padding-right: 5px;
}
.doc .h   {
    display: inline
}
details:not(.doc-part) {
    padding-left: 5px;
}
/* </app.Head> */
        """

class Page(Element):

    class PropTypes:
        title: Required[str]
        slug: Required[str]
        conf: Required[List[Dict]]
        global_css_collector: Required[CSSCollector]
        global_js_collector: Required[JSCollector]

    def render(self, context):
        css_ref = self.add_ref()
        js_ref = self.add_ref()
        menu_ref = self.add_ref()

        return \
            <CSSCollector ref={css_ref} reuse={self.global_css_collector} reuse_non_global=False>
                <JSCollector ref={js_ref} reuse={self.global_js_collector} reuse_non_global=False>
                    <Doctype />
                    <html lang="en">
                        <Head>
                            <meta charset="utf-8"/>
                            <meta name="viewport" content="width=device-width, initial-scale=1"/>
                            <title>{self.title} - MIXT documentation</title>
                            <link rel="stylesheet" type="text/css" href="typeset.css" />
                            <link rel="stylesheet" type="text/css" href="global.css" />
                            {lambda: css_ref.current.render_collected()}
                        </Head>
                        <body>
                            {lambda: menu_ref.current.render_menu()}
                            <main>
                            <Intro version={__version__}/>
                            <MainMenuCollector ref={menu_ref}>
                            <div class="doc">
                                {[
                                    component_class(obj=doc_entry)
                                    for component_class, doc_entry
                                    in resolve_conf(self.conf)
                                ]}
                            </div>
                            </MainMenuCollector>
                            </main>
                    <script type="text/javascript" src="vendored.js"></script>
                    <script type="text/javascript" src="global.js"></script>
                    {lambda: js_ref.current.render_collected()}
                </body>
            </html>
            </JSCollector>
        </CSSCollector>


def resolve_conf(entries: List[Dict]) -> List[types.DocEntry]:
    result = []
    for entry in entries:
        if entry['type'] == 'class':
            result.append((
                Class,
                resolve_class(
                    klass=entry['class'],
                    attrs=entry.get('attributes') or [],
                    methods=entry.get('methods') or [],
                    name=entry.get('name'),
                )
            ))
        if entry['type'] == 'module':
            result.append((
                Module,
                resolve_module(
                    module=entry['module'],
                    attrs=entry.get('attributes') or [],
                    functions=entry.get('functions') or [],
                    name=entry.get('name'),
                    classes=entry.get('classes') or [],
                )
            ))
        if entry['type'] == 'manual':
            result.append((
                lambda obj: obj,
                entry['component']()
            ))
    return result


def files_to_render():

    global_js_collector = JSCollector()
    global_css_collector = CSSCollector()

    files = []

    for page in PAGES:
        files.append([
            f"{page['slug']}.html",
            page['title'],
            Page,
            {
                'title': page['title'],
                'slug': page['slug'],
                'conf': page['conf'],
                'global_js_collector': global_js_collector,
                'global_css_collector': global_css_collector,
            }
        ])

    files.append([
        "typeset.css",
        None,
        TypesetStyle,
        {'with_tag': False}
    ])

    files.append([
        "global.css",
        None,
        global_css_collector.render_collected,
        {'with_tag': False}
    ])

    files.append([
        "vendored.js",
        None,
        VendoredScripts,
        {'with_tag': False}
    ])

    files.append([
        "global.js",
        None,
        global_js_collector.render_collected,
        {'with_tag': False}
    ])

    return files
