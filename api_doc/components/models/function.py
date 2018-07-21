# coding: mixt

from mixt import Element, NotProvided, Required, html
from mixt.contrib.css import css_vars, render_css, Modes

from ... import datatypes

from ..doc import DocPart, DocHeader
from ..generic import Details

from . import Code, DocString, NamedValue, UnnamedValue


class Function(Element):
    class PropTypes:
        id_prefix: str = ''
        h_level: int = 2
        obj: Required[datatypes.Function]
        open: bool = True
        open_details: bool = False

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        tagged = tuple(
            f'.function-{name}'
            for name in [
                'staticmethod',
                'property',
                'classmethod'
            ]
        )
        return render_css(merge({
            "/*": f"<{cls.__module__}.{cls.__name__}>",
            ".function-kind": {
                display: none,
            },
            tagged: {
                " > summary > .h:after": merge(
                    context.styles.snippets['TAG'],
                    context.styles.snippets['HL'],
                ),
            },
            ".function": {
                "> .content > details:not(.doc-part) > summary": {
                    opacity: 0.25,
                },
                "&:hover > .content > details:not(.doc-part):not([open]) > summary": {
                    opacity: 1,
                }
            },
            media({max-width: context.styles.breakpoint}): {
                ".function-arg": {
                    display: block,
                    margin-left: 1*em,
                }
            }
        }, {
            f"{t} > summary > .h:after": {
                content: str(t.split('-')[-1])
            }
            for t in tagged
        }, {
            "/**": f"</{cls.__module__}.{cls.__name__}>",
        }))

    def render(self, context):
        func = self.obj
        kind = func.kind or 'function'
        id_prefix = f'{self.id_prefix}{func.name}'

        docstring_details = doc_arguments = doc_return = doc_raises = doc_example = None

        if func.doc.details:
            docstring_details = <DocString doc={func.doc} hide_summary=True />

        args = None
        len_args = len(func.args)
        if len_args:
            args = [
               [
                   html.Span(_class="function-arg")(
                       arg.name,
                       ': ',
                       html.Code()(arg.type),
                       [
                           ' = ',
                           html.Code()(getattr(arg.default, '__name__', str(arg.default)))
                       ] if arg.has_default else '',
                       ', ' if index < len_args - 1 else ''
                   )
               ]
               for index, arg in enumerate(func.args)
            ],

            doc_arguments = <DocPart kind="function" subkind="arguments" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Arguments">Arguments</DocHeader>
                {[
                    <NamedValue value={arg} h_level={self.h_level+2} id_prefix="{id_prefix}-arguments-" />
                    for arg
                    in func.args
                ]}
            </DocPart>

        return_type = ''
        len_ret = 0
        if func.ret:
            len_ret = len(func.ret)
            if len_ret > 1:
                return_type = 'Tuple[' + ', '.join([
                    ret.type for ret in func.ret
                ]) + ']'
            else:
                return_type = func.ret[0].type
            return_type = [' → ', html.Code()(return_type)]

            doc_return = <DocPart kind="function" subkind="returns" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Returns">Returns</DocHeader>
                <if cond={len_ret > 1}>
                    <p>Multiple return values ({len_ret}):</p>
                </if>
                {[
                    <UnnamedValue
                        value={ret}
                        h_level={self.h_level+2}
                        index={index if len_ret > 1 else NotProvided}
                         id_prefix="{id_prefix}-returns-"
                    />
                    for index, ret
                    in enumerate(func.ret, 1)
                ]}
            </DocPart>

        if func.raises:
            doc_raises = <DocPart kind="function" subkind="raises" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Raises">Raises</DocHeader>
                {[
                    <NamedValue value={raise_info} h_level={self.h_level+2} id_prefix="{id_prefix}-raises-" />
                    for raise_info
                    in func.raises
                ]}
            </DocPart>

        if func.example:
            doc_example = <DocPart kind="function" subkind="example" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Example">Example</DocHeader>
                <Code code={func.example} />
            </DocPart>

        return <DocPart kind="function" id_prefix={id_prefix} level={self.h_level} open={self.open} class="function-{kind}">
            <DocHeader menu={func.name} menu-class="menu-function-{kind}">
                <if cond={kind not in ('method', 'function')}>
                    <span class="function-kind">@{kind}<br /></span>
                </if>
                {func.name}<if cond={kind != 'property'}>({args})</if>{return_type}
            </DocHeader>

            <DocString doc={func.doc} hide_details=True />

            <if cond={func.doc.details or func.example or func.args or func.ret or func.raises}>
                <Details class="linked-to-parent" open={self.open_details}>
                    <summary>Details</summary>

                    {docstring_details}
                    {doc_arguments}
                    {doc_return}
                    {doc_raises}
                    {doc_example}

                </Details>
            </if>

        </DocPart>
