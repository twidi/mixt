# coding: mixt

from typing import Dict, List, Optional

from mixt import Element, JSCollector, Ref, Required, exceptions, html, __version__
from mixt.contrib.css import css_vars, render_css, Modes
from mixt.internal import collectors, dev_mode

from .components import CSSCollector, H, MainMenuCollector, VendoredScripts, TypesetStyle
from .components import manual
from .components.models import Class, Module
from .components.style import StyleContext, Styles
from .code_utils import resolve_class, resolve_module
from . import datatypes


PAGES = [
    {
        'title': 'Intro',
        'h_title': "Welcome to MIXT documentation",
        'slug': 'index',
        'conf': [
            {
                'type': "manual",
                'component': manual.Intro
            },
        ]
    },
    {
        'title': 'User guide',
        'slug': 'user-guide',
        'conf': [
            {
                'type': "manual",
                'component': manual.UserGuide
            },
        ]
    },
    {
        'title': 'API',
        'slug': 'api',
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
    },
    {
        'title': 'Mixt CSS',
        'slug': 'contrib-css',
        'conf': [
            {
                'type': "manual",
                'component': manual.ContribCss,
            },
        ]
    },
]


class Head(Element):

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_pycss_global(cls, context):
        colors = context.styles.colors
        return {
            "#main-menu": {
                position: fixed,
                left: 0,
                top: 0,
                overflow: auto,
                z-index: 1,
                height: 100*pc,
                media({max-width: context.styles.breakpoint}): {
                    _: {
                        width: 2*rem,
                        "> ul": {
                            display: none
                        },
                        '&:not(.focus-within) > p': {
                            transform: (
                                rotate(-90*deg),
                                translateX(-6*rem),
                                translateY(-5*px)
                            ),
                            white-space: nowrap,
                        },
                        '&.focus-within': {
                            width: auto,
                            max-width: 90*pc,
                            '> ul': {
                                display: block,
                            },
                            '&:before': {
                                content: str(""),
                            }
                        }
                    },
                },
                media(~_all & {max-width: context.styles.breakpoint}): {
                    _: {
                        width: 10*rem,
                        '&:hover': {
                            width: auto,
                            min-width: 10*rem,
                            max-width: 90*pc,
                        }
                    },
                },
            },
            code: {
                font-weight: normal,
            },
            hr: {

                border: 0,
                height: 1*px,
                background-image: override(
                    -webkit-linear-gradient(left, colors[1], colors[9], colors[1]),
                    -moz-linear-gradient(left, colors[1], colors[9], colors[1]),
                    -ms-linear-gradient(left, colors[1], colors[9], colors[1]),
                    -o-linear-gradient(left, colors[1], colors[9], colors[1]),
                    linear-gradient(left, colors[1], colors[9], colors[1]),
                ),
            },
            body: {
                background: colors[1],
                margin: 0,
            },
            ".doc": {
                margin-left: 1*em + 9*px,
                padding-right: 20*px,
                margin-bottom: 1*em,
                media({max-width: context.styles.breakpoint}): {
                    _: {
                        margin-left: 0.2*em + 9*px,
                        padding-right: 0,
                    }
                },
                "& p, & .h": {
                    padding-right: 5*px,
                },
                ".h": {
                    display: inline,
                }
            },
            "details:not(.doc-part)": {
                padding-left: 5*px,
            },
            main: {
                ">h1": {
                    line-height: 1.3,
                    padding: (0.5*em, 0),
                    background: colors[9],
                    color: white,
                    text-align: center,
                    margin-top: 0,
                    margin-bottom: 1*em,
                    ">a": {
                        color: inherit,
                    }
                },
                media({max-width: context.styles.breakpoint}): {
                    _: {
                        margin-left: 2*rem,
                    }
                },
                media(~_all & {max-width: context.styles.breakpoint}): {
                    _: {
                        margin-left: 10*rem,
                    }
                }
            },
        }

    @classmethod
    def render_css_global(cls, context):
        css = render_css((cls.render_pycss_global(context)))
        return f"""
/* <{cls.__module__}.{cls.__name__}> */
{css}
/* </{cls.__module__}.{cls.__name__}> */
"""


class Page(Element):

    class PropTypes:
        title: Required[str]
        h_title: Optional[str]
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
                            <title>{self.title} - MIXT documentation (version {__version__})</title>
                            <link rel="stylesheet" type="text/css" href="typeset.css" />
                            <link rel="stylesheet" type="text/css" href="global.css" />
                            {lambda: css_ref.current.render_collected()}
                        </Head>
                        <body>
                            {lambda: menu_ref.current.render_menu()}
                            <main>
                            <H level=1>
                                <if cond={self.prop('h_title', None)}>
                                    {self.h_title}
                                </if>
                                <else>
                                    <a href="index.html" title="Back to documentation index">MIXT documentation</a>: {self.title}
                                </else>
                            </H>
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


def resolve_conf(entries: List[Dict]) -> List[datatypes.DocEntry]:
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
            lambda **args: StyleContext(styles=Styles)(Page(**args)),
            {
                'title': page['title'],
                'h_title': page.get('h_title'),
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
