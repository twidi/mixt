# coding: mixt

from mixt import html, h

from ..doc import DocPart, DocHeader
from ..generic import Rst, SourceCode
from .base import _Manual


class Context(_Manual):

    def render(self, context):
        id_prefix = f'{self.id_prefix}Context'

        return <DocPart kind="Context" id_prefix={id_prefix} level={self.h_level}>
            <DocHeader menu="Context">Context</DocHeader>
            <Rst>{h.Raw(
# language=RST
"""
**Context provides a way to pass data through the component tree without having to
pass props down manually at every level.**

In a typical Mixt application, data is passed top-down (parent to child) via props,
but this can be cumbersome for certain types of props (e.g. locale preference,
UI theme, authenticated user...) that are required by many components within an
application.

Context provides a way to share values like these between components without
having to explicitly pass a prop through every level of the tree.

A context is a simple element than simply render its children, passing itself
down the tree. So every element in a tree under a context, gain this context.

You cannot pass anything to a context. A context has a ``PropTypes`` class
defining the expected props and their types.

You can have many contexts in the tree. They are merged so their children elements
can access props of all of them. You just cannot set the same prop in these
different contexts.
"""
            )}</Rst>

            <DocPart kind="Context" subkind="example" id_prefix={id_prefix} level={self.h_level+1} open>
                <DocHeader menu="Example">Example</DocHeader>
                <SourceCode language="python">{h.Raw(
# language=Python
"""
>>> from mixt import BaseContext, Element, NotProvided, html

>>> class AuthenticatedContext(BaseContext):
...     class PropTypes:
...         auth_username: str
        
>>> class App(Element):
...     def render(self, context):
...         return <div>
...             <if cond={context.prop('auth_username', None)}>
...                 Welcome back, {context.auth_username}.
...             </if>
...             <else>
...                 Hello. You need to idenfify yourself.
...             </else>
...         </div>
        
>>> print(<App />)
<div>Hello. You need to idenfify yourself.</div>

>>> who = 'John'
>>> print(
...     <AuthenticatedContext auth_username={who}>
...         <App />
...     </AuthenticatedContext>
... )
<div>Welcome back, John.</div>

>>> who = NotProvided
>>> print(
...     <AuthenticatedContext auth_username={who}>
...         <App />
...     </AuthenticatedContext>
... )
<div>Hello. You need to idenfify yourself.</div>
"""
                )}</SourceCode>
            </DocPart>

        </DocPart>
