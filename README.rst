####
MIXT
####

Write html components directly in python and you have a beautiful but controversial MIXTure.

Yes, **controversial**.

**If you don't like it, ignore it** (but you can use this without the html-in-python part, see below ;))

*Based* on `pyxl <https://github.com/gvanrossum/pyxl3/>`_. Python 3.6+ only, and use typing for data validation.

Once you have your html, you can do whatever you want with it. Think of it as a replacement for your classic template engine.

**Source code**: `<https://github.com/twidi/mixt/>`_

**Documentation**: `<https://twidi.github.io/mixt/>`_

**PyPI**: `<https://pypi.org/project/mixt/>`_

**CI** (CircleCi): `<https://circleci.com/gh/twidi/workflows/mixt/>`_

***********
Basic usage
***********

Let's create a file ``example.py``

.. code-block:: python

   # coding: mixt

   from mixt import html, Element, Required

   class Hello(Element):
       class PropTypes:
           name: Required[str]

       def render(self, context):
           return <div>Hello, {self.name}</div>

   print(<Hello name="World"/>)


And execute it:

.. code-block:: shell

   $ python example.py
   <div>Hello, World</div>


If you don't like to write html in python, you can still use it:

.. code-block:: python

   from mixt import html, Element, Required

   class Hello(Element):
       class PropTypes:
           name: Required[str]

       def render(self, context):
           return html.Div()("Hello, ", self.name)

   print(Hello(name="World"))


********
Features
********

Yes it is inspired by React (in fact, mainly JSX) and we borrow some of the concept:

- props and PropTypes with validation
- dev-mode to validate props in dev but not in production to speed things up (your tests should have tested that everything is ok)
- context
- class components or simple function components
- high order components

And we added:

- write css using python
- css/js collectors
- proxy components


************
Installation
************

Run these two commands. The second one will tell python how to understand files with html inside.

.. code-block:: shell

   pip install mixt
   mixt-post-install

To check that everything is ready, run:

.. code-block:: shell

   python -m mixt.examples.simple

You should have this output:

.. code-block:: html

   <div title="Greeting">Hello, World</div>

If you don't want to use the html-in-python stuff, don't run ``mixt-post-install``. And then test with (to have the same output):

.. code-block:: shell

   python -m mixt.examples.simple_pure_python

**********
Contribute
**********

Clone the git project then:

.. code-block:: shell

   make dev


To check that everything is ready, run:

.. code-block:: shell

   python -m mixt.examples.simple


You should have this output:

.. code-block:: html

   <div title="Greeting">Hello, World</div>


After having done some code:

.. code-block:: shell

    make tests


.. code-block:: shell

    make lint


If you touch things in the ``codec`` directory, you'll have to run ``make dev`` (or at least ``make full-clean``) to purge the ``pyc`` python files.

Note that our CI will check that every commit passes the ``make lint``, ``make tests`` and ``make check-doc``. So don't forget to run these for each commit.

One way to do it before pushing is:

.. code-block:: shell

    git rebase develop --exec 'git log -n 1; make checks'


**********
User Guide
**********

Note: You can find the *final* code of this user guide in ``src/mixt/examples/user_guide`` (you'll find ``mixt.py`` and ``pure_python.py``).

Run it with:

.. code-block:: shell

    python -m mixt.examples.user_guide


Start
=====

Let's create a... todo list, yeah!

But before, remember. This is not React, it's not on the browser and there is no Javascript involved here. We only talk about rendering some HTML.

But you can do what you want with it. Add javascript handlers, simple forms...

Talking about forms...

In a todo list, we want to be able to add a todo. It's a simple text input.

So let's create our first component, the ``TodoForm``. We want a form with an input text and a button.

A component is a subclass of the ``Element`` class, with a ``render`` method you have to write.

.. code-block:: python

    # coding: mixt

    from mixt import Element, html  # html is mandatory to resolve html tags

    class TodoForm(Element):

        def render(self, context):  # Ignore the ``context`` argument for now.
            return \  # The ``\`` is only for a better indentation below
                <form method="post" action="???">
                    <label>New Todo: </label><itext name="todo" />
                    <button type="submit">Add</button>
                </form>


Note that this could have been written as a simple function:

.. code-block:: python

    # coding: mixt

    from mixt import Element, html

    def TodoForm():
        return \
            <form method="post" action="???">
                <label>New Todo: </label><itext name="todo" />
                <button type="submit">Add</button>
            </form>


When print the component, these two will give the same result:

.. code-block:: python

    print(<TodoForm />)

.. code-block:: html

    <form method="post" action="???"><label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


Spacing
=======

Notice how it is formatted: no space between tags. In fact, it's `like in JSX <https://reactjs.org/docs/jsx-in-depth.html#string-literals-1>`_:

    JSX removes whitespace at the beginning and ending of a line. It also removes blank lines. New lines adjacent to tags are removed; new lines that occur in the middle of string literals are condensed into a single space

To add a space, or a newline, you can pass some python. Let's, as an example, add a newline before the label:

.. code-block:: python

    #...
                <form method="post" action="???">
                    {'\n'}<label>New Todo: </label><itext name="todo" />
    #...


Now we have this output:

.. code-block:: html

    <form method="post" action="/todo/add">
    <label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


Props
=====

Now let's go further.

Notice the ``action`` attribute of the form. We need to pass something. But hard-coding it does not sound right. Wwe need to pass it to the component.

``Mixt`` has, like ``React``, the concept of properties, aka "props".


PropTypes class
---------------

In ``Mixt``, we define them with a type, in a class inside our component, named ``PropTypes``:

.. code-block:: python

    class TodoForm(Element):

        class PropTypes:
            add_url: str

        def render(self, context):
            return \
                <form method="post" action={self.add_url}>
                    <label>New Todo: </label><itext name="todo" />
                    <button type="submit">Add</button>
                </form>


Here we defined a prop named ``add_url`` which must be a string (``str``). This uses the `python typing syntax <https://docs.python.org/3.6/library/typing.html>`_.

And notice how we changed the ``action`` attribute of the ``form`` tag. It's now ``{self.add_url}`` instead of ``"???"``.

When attributes are passed between curly braces, they are interpreted as pure python at run-time. In fact, as the ``mixt`` parser will convert the whole file to pure python before letting the python interpreter running it, it will stay the same, only the html around will be converted. So there is no penalty to do this.


Props and children
------------------

Look how this would look like if our component was written in pure python:

.. code-block:: python

    from mixt import Element, html

    class TodoForm(Element):

        class PropTypes:
            add_url: str

        def render(self, context):
            return html.Form(method='post', action=self.add_url )(
                html.Label()(
                    html.Raw("New Todo: ")
                ),
                html.InputText(name='todo'),
                html.Button(type='submit')(
                    html.Raw("Add")  # or html.Rawhtml(text="Add")
                ),
            )


Notice how the props are passed to a component as named arguments and how ``action`` is passed: ``action=self.add_url``.

This pure-python component also shows you how it works: props are passed as named argument to the component class, then this component is called, passing children components as positional arguments to the call:

.. code-block:: python

    ComponentClass(prop1="val1", prop2="val2")(
        Children1(),
        Children2(),
    )

What are children? Children are tags inside other tags.

In ``<div id="divid"><span /><p>foo</p></div>``, we have:

- a ``html.Div`` component, with a prop ``id`` and two children:

  - a ``html.Span`` component, without children
  - a ``html.P`` component with one child:

    - a ``html.RawHtml`` component with the text "foo"


Note that you can play with props and children. First the version in pure-python to show how it works:

.. code-block:: python

    def render(self, context):
        props = {"prop1": "val1", "prop2": "val2"}
        children = [Children1(), Children2()]

        return ComponentClass(**props)(*children)
        # You can pass a list of children to to the call, so this would produce the same result:
        # ComponentClass(**props)(children)


Then the ``mixt`` version:

.. code-block:: python

    def render(self, context):
        props = {"prop1": "val1", "prop2": "val2"}
        children = [<Children1/>, <Children2/>]

        return <ComponentClass {**props}>{*children}</ComponentClass>
        # or, the same, passing the children as a list:
        # return <ComponentClass {**props}>{children}</ComponentClass>


Passing props
-------------

Now let's go back to our props ``add_url``.

How to pass it to the component?

The exact same way we passed attributes to HTML tags: they are in fact props defined in the HTML compoments (defined in ``mixt.html``). We support every HTML tags that, at the time of the writing, are valid (not deprecated) in HTML5, with their attributes (excluding the deprecated ones).

So let's do this:

.. code-block:: python

    print(<TodoForm add_url="/todo/add"/>)

.. code-block:: html

    <form method="post" action="/todo/add"><label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>

OK, we have our prop present in the rendered HTML.

Validation
----------

What if we don't pass a string? We said in ``PropTypes`` that we wanted a string...

Numbers
^^^^^^^

Let's try it:

.. code-block:: python

    print(<TodoForm add_url=1/>)

.. code-block:: html

    <form method="post" action="1"><label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


It works! But... it's not a string!! In fact, there is a special case for numbers, you can pass them as numbers instead of strings and they are converted if needed...


Booleans and other special cases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So let's try something else.

.. code-block:: python

    print(<TodoForm add_url=True/>)

.. code-block:: python

    mixt.exceptions.InvalidPropValueError:
    <TodoForm>.add_url: `True` is not a valid value for this prop (type: <class 'bool'>, expected: <class 'str'>)


And it's the same if we pass ``True`` in python

.. code-block:: python

    print(<TodoForm add_url={True}/>)

.. code-block:: python

    mixt.exceptions.InvalidPropValueError:
    <TodoForm>.add_url: `True` is not a valid value for this prop (type: <class 'bool'>, expected: <class 'str'>)


Ok, let's trick the system and pass ``"True"``, as a string.

.. code-block:: python

    print(<TodoForm add_url="True"/>)

.. code-block:: python

    mixt.exceptions.InvalidPropValueError:
    <TodoForm>.add_url: `True` is not a valid value for this prop (type: <class 'bool'>, expected: <class 'str'>)


Still the same, but here we passed a string! Yes but there are 4 values that are always evaluated to what they seems to be:

- True
- False
- None
- NotProvided (a special value meaning "not set" which is different that ``None``)

The only way to pass one of these values as a string, is to pass them via python, as a string:

.. code-block:: python

    print(<TodoForm add_url={"True"}/>)

.. code-block:: html

    <form method="post" action="True"><label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


Except these 4 values, and numbers, every value that is passed to an attribute is considered a string. Even if there is no quotes, like in html in HTML5, where quotes are not mandatory for strings without some characters (no spaces, no ``/``...).

To pass something else, you must surround the value in curly braces (and in this cases there is no need for quotes around the curly braces.


Ok, now we are sure that we only accept string.... but what if I pass nothing? And... what is "nothing"?

Let's start with an empty string in python:

.. code-block:: python

    print(<TodoForm add_url={""}/>)

.. code-block:: html

    <form method="post" action=""><label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


Ok it works, we wanted a string, we have a string.

Now let's pass this empty string directly:

.. code-block:: python

    print(<TodoForm add_url=""/>)

.. code-block:: html

    <form method="post" action=""><label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


It still works, because it's still a string. Let's remove the quotes, to see.

.. code-block:: python

    print(<TodoForm add_url=/>)

.. code-block:: python

    mixt.exceptions.GeneralParserError: <mixt parser> Unclosed Tags: <TodoForm>


Hum yeah, this is not valid HTML. So let's remove the ``=``:

.. code-block:: python

    print(<TodoForm add_url/>)

.. code-block:: python

    mixt.exceptions.InvalidPropValueError:
    <TodoForm>.add_url: `True` is not a valid value for this prop (type: <class 'bool'>, expected: <class 'str'>)


WHAT? Yes, think about HTML5 attributes like ``required``, ``checked``... They only need to be present as an attribute, without value, to be considered ``True``. So when an attribute doesn't have any value, it's a boolean, and it's ``True``.

In addition to not pass a value, those two other ways are valid in HTML5 for a boolean to by ``True``:

- pass an empty string: ``required=""``
- pass the name of the attribute: ``required="required"``

For your convenience, we added another way:

- pass ``True`` (case does not matter), as python or as a string: ``required=True``, ``required={True}``, ``required="true"``

And its counterpart, to pass ``False``:

- pass ``False`` (case does not matter), as python or as a string: ``required=False``, ``required={False}``, ``required="false"``


Required props
--------------

Ok for the boolean attributes. It's not our case. The last thing we can do is to not set the attribute at all:

.. code-block:: python

    print(<TodoForm/>)
    # this is the same: ``print(<TodoForm add_url=NotProvided />)```
    # (``NotProvided`` must be imported from ``mixt``)

.. code-block:: python

    mixt.exceptions.UnsetPropError: <TodoForm>.add_url: prop is not set


It's understandable: we try to access a prop that is not set, of course we cannot use it.


But what if we don't access it? If we don't print the component, it won't be rendered:

.. code-block:: python

    <TodoForm/>

.. code-block:: python

    <TodoForm at 0x7fbd18ea5630>


So we can create an instance but it will fail at render time. But there is a way to prevent that.

By default, all properties are optional. And you don't have to use the ``Optional`` type from the python ``typing`` module for that, it would be cumbersome to do it for each prop.

Instead, ``mixt`` provides a type named ``Required`` that you use the same way than ``Optionnal``.

.. code-block:: python

    from mixt import Element, Required, html

    class TodoForm(Element):

        class PropTypes:
            add_url: Required[str]

        def render(self, context):
            # ...


So we just said we wanted a string, and that it is required.

Let's try again to create it without the prop:

.. code-block:: python

    <TodoForm/>

.. code-block:: python

    mixt.exceptions.RequiredPropError: <TodoForm>.add_url: is a required prop but is not set


Now we have the exception raised earlier in our program.


Default props
-------------

To see other possibilities in props, let's add a new one to change the text label. But we don't want to make it required, and instead have a default value.

For this, it's as easy as adding a value to the prop in the ``PropTypes`` class:

.. code-block:: python

    class TodoForm(Element):

        class PropTypes:
            add_url: Required[str]
            label: str = 'New Todo'

        def render(self, context):
            return \
                <form method="post" action={self.add_url}>
                    <label>{self.label}: </label><itext name="todo" />
                    <button type="submit">Add</button>
                </form>


Now let's try it without passing the prop:

.. code-block:: python

    print(<TodoForm add_url="/todo/add"/>)


.. code-block:: html

    <form method="post" action=""><label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


And if we pass one:

.. code-block:: python

    print(<TodoForm add_url="/todo/add" label="Thing to do" />)


.. code-block:: html

    <form method="post" action="/todo/add"><label>Thing to do: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


It works as expected.

Note that you cannot give a default value while having the prop ``Required``. It makes no sense, so it's checked as soon as possible, while the ``class`` is constructed:

.. code-block:: python

    class TodoForm(Element):

        class PropTypes:
            add_url: Required[str]
            label: Required[str] = 'New Todo'

.. code-block:: python

    mixt.exceptions.PropTypeRequiredError: <TodoForm>.label: a prop with a default value cannot be required


And of course the default value must match the type!

.. code-block:: python

    class TodoForm(Element):

        class PropTypes:
            add_url: Required[str]
            label: str = {'label': 'foo'}

.. code-block:: python

    mixt.exceptions.InvalidPropValueError:
    <TodoForm>.label: `{'label': 'foo'}` is not a valid value for this prop (type: <class 'dict'>, expected: <class 'str'>)


Choices
-------

Another thing we want to do in our component is to let it construct the label, passing it a "type" of todo, but limiting the choices. For this we can use the ``Choices`` type:

.. code-block:: python

    from mixt import Choices, Element, Required, html


    class TodoForm(Element):

        class PropTypes:
            add_url: Required[str]
            type: Choices = ['todo', 'thing']

        def render(self, context):

            return \
                <form method="post" action={self.add_url}>
                    <label>New {self.type}: </label><itext name="todo" />
                    <button type="submit">Add</button>
                </form>


Let's try it:

.. code-block:: python

    print(<TodoForm add_url="/todo/add" type="todo" />)
    print(<TodoForm add_url="/todo/add" type="thing" />)

.. code-block:: html

    <form method="post" action="/todo/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>
    <form method="post" action="/todo/add"><label>New thing: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


And what if we try to pass something else than the available choices? It fails, as expected:

.. code-block:: python

    print(<TodoForm add_url="/todo/add" type="stuff" />)

.. code-block:: python

    mixt.exceptions.InvalidPropChoiceError: <TodoForm>.type: `stuff` is not a valid choice for this prop (must be in ['todo', 'thing'])


Default choices
---------------

But maybe we don't want to pass it and use a default value. What would the result be?

.. code-block:: python

    print(<TodoForm add_url="/todo/add" />)

.. code-block:: python

    mixt.exceptions.UnsetPropError: <TodoForm>.type: prop is not set


So we have to mark the ``type`` prop as required:

.. code-block:: python

    class PropTypes:
        add_url: Required[str]
        type: Required[Choices] = ['todo', 'thing']


So if we don't pass it, it fails earlier:

.. code-block:: python

    print(<TodoForm add_url="/todo/add" />)

.. code-block:: python

    mixt.exceptions.RequiredPropError: <TodoForm>.type: is a required prop but is not set


But it's not what we want, we want a default value.

In fact, you noticed that for types other than ``Choices``, setting a value in ``PropTypes`` gives us a default value. But for ``Choices`` it's different, as the value is the list of choices.

For this, we have ``DefaultChoices``: it work the same as ``Choices``, but use the first entry in the list as the default value. And of course, as with other types having default, it cannot be ``Required``.

Let's try it:

.. code-block:: python

    from mixt import DefaultChoices, Element, Required, html


    class TodoForm(Element):

        class PropTypes:
            add_url: Required[str]
            type: DefaultChoices = ['todo', 'thing']


.. code-block:: python

    print(<TodoForm add_url="/todo/add" />)

.. code-block:: html

    <form method="post" action="/todo/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>

It works as expected.


Advanced types
--------------

Until then, we used simple types, but you can use more complicated ones.

So for example, we'll make the ``add_url`` prop to accept a function that will compute the url for us based on the ``type`` prop. But we also want to allow strings, and with a default value.

We can do that, with typing. Our function will take a string, the ``type`` and will return a string, the url.

So the `syntax <https://docs.python.org/3.6/library/typing.html#typing.Callable>`_ is ``Callable[[str], str]`` for the callable, and we use ``Union`` to accept things of type ``Callable`` or ``str``:

.. code-block:: python

    from typing import Union, Callable
    from mixt import DefaultChoices, Element, Required, html


    class TodoForm(Element):

        class PropTypes:
            add_url: Union[Callable[[str], str], str] = "/todo/add"
            type: DefaultChoices = ['todo', 'thing']

        def render(self, context):

            if callable(self.add_url):
                add_url = self.add_url(self.type)
            else:
                add_url = self.add_url

            return \
                <form method="post" action={add_url}>
                    <label>New {self.type}: </label><itext name="todo" />
                    <button type="submit">Add</button>
                </form>

First, let's try it without the ``add_url`` prop, as we have a default:

.. code-block:: python

    print(<TodoForm  />)

.. code-block:: html

    <form method="post" action="/todo/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


It should work too if we pass a string:

.. code-block:: python

    print(<TodoForm add_url="/todolist/add" />)

.. code-block:: html

    <form method="post" action="/todolist/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


And now we can pass a function:

.. code-block:: python

    def make_url(type):
        return f"/{type}/add"

    print(<TodoForm add_url={make_url} />)

.. code-block:: python

    mixt.exceptions.InvalidPropValueError: <TodoForm>.add_url:
    `<function make_url at 0x7fe2ae87be18>` is not a valid value for this prop (type: <class 'function'>, expected: Union[Callable[[str], str], str])


Oh? Why? I passed a function accepting a string as argument and returning a string. Yes, but don't forget that types are checked! So we must add types to our function:

.. code-block:: python

    def make_url(type: str) -> str:
        return f"/{type}/add"

    print(<TodoForm add_url={make_url} />)

.. code-block:: html

    <form method="post" action="/todo/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


And if we pass another type, the url should change accordingly:

.. code-block:: python

    print(<TodoForm add_url={make_url} type="thing" />)

.. code-block:: html

    <form method="post" action="/thing/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


We can even make this function the default value for our prop:

.. code-block:: python

    from typing import Union, Callable
    from mixt import DefaultChoices, Element, Required, html


    def make_url(type: str) -> str:
        return f"/{type}/add"


    class TodoForm(Element):

        class PropTypes:
            add_url: Union[Callable[[str], str], str] = make_url
            type: DefaultChoices = ['todo', 'thing']

        def render(self, context):

            if callable(self.add_url):
                add_url = self.add_url(self.type)
            else:
                add_url = self.add_url

            return \
                <form method="post" action={add_url}>
                    <label>New {self.type}: </label><itext name="todo" />
                    <button type="submit">Add</button>
                </form>

.. code-block:: python

    print(<TodoForm />)

.. code-block:: html

    <form method="post" action="/todo/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form>


dev-mode
========

Now you may start wondering... python typing is cumbersome and validating may take away some of our precious time.

Let's me answer that:

1. No, typing is not cumbersome. It's really useful to spot bugs and add some self-documentation.
2. Yes, it takes away some of our precious time. But we got you covered.

By default, ``mixt`` run in "dev-mode". And in dev-mode, props are validated when passed to a component. When you are NOT in "dev-mode", the validation is skipped. So in production, you can deactivate the dev-mode (we'll see how in a minute) and pass props very fast:

- we don't check required props (but that would fail if you try to use it in your compoment)
- we don't check if a ``Choices`` prop is, indeed, in the list of choices
- we don't check the type at all, so for example if you want to pass a list for a string, it will work but with understandable strange things happening in your ``render`` method.

But you may say that it's in production that validation is important. Indeed. But of course your code is fully covered by tests, that you run in dev-mode, and so in production, you don't need this validation! And note that it's how React works, by the way, with ``NODE_ENV=production``.

How to change dev-mode? We don't enforce any environment variable but we propose some functions. It's up to you to call them:

.. code-block:: python

    from mixt import set_dev_mode, unset_dev_mode, override_dev_mode, in_dev_mode

    # by default, dev-mode is active
    assert in_dev_mode()

    # you can unset the dev-mode
    unset_dev_mode()
    assert not in_dev_mode()

    # and set it back
    set_dev_mode()
    assert in_dev_mode()

    # set_dev_mode can take a boolean
    set_dev_mode(False)
    assert not in_dev_mode()

    set_dev_mode(True)
    assert in_dev_mode()

    # and we have a context manager to override for a block
    with override_dev_mode(False):
        assert not in_dev_mode()
        with override_dev_mode(True):
            assert in_dev_mode()
        assert not in_dev_mode()
    assert in_dev_mode()


So let's try this with the ``type`` prop. Remember, it looks like:

.. code-block:: python

    type: DefaultChoices = ['todo', 'thing']

We try to pass another choice, first in dev-mode:

.. code-block:: python

    with override_dev_mode(True):
        print(<TodoForm type="stuff" />)

.. code-block:: python

    mixt.exceptions.InvalidPropChoiceError: <TodoForm>.type: `stuff` is not a valid choice for this prop (must be in ['todo', 'thing'])

It fails as expected.

And now by deactivating dev-mode:

.. code-block:: python

    with override_dev_mode(False):
        print(<TodoForm type="stuff" />)

.. code-block:: html

    <form method="post" action="/stuff/add"><label>New stuff: </label><input type="text" name="todo" /><button type="submit">Add</button></form>

It works, we have a todo type that was not in our choices that is used, and is in the ``action`` too. It's the work of your tests to ensure that you never pass invalid props, so you can be confident in production and deactivate dev-mode.


Components cascade
==================

Now we have our form. What other components do we need for our todo list app?

Of course, we need a way to display a todo entry.

But what is a todo entry? Let's create a basic ``TodoObject``:

.. code-block:: python

    class TodoObject:
        def __init__(self, text):
            self.text = text


It's a very simple class, but you can use what you want, of course. It could be Django models, etc...

So we can create our ``Todo`` component, making it accept a required ``TodoObject`` as prop:

.. code-block:: python

    class Todo(Element):
        class PropTypes:
            todo: Required[TodoObject]

        def render(self, context):
            return <li>{self.todo.text}</li>

And we can use it:

.. code-block:: python

    todo = TodoObject("foo")
    print(<Todo todo={todo} />)

.. code-block:: html

    <li>foo</li>


Now we want to have a list of todos. Let's create a ``TodoList`` component that will accept as props a list of ``TodoObject``.

But what is different than our two other components, that only use html tags in their ``render`` method, it's that now we will encapsulate a component into another. Let's see how.

.. code-block:: python

    class TodoList(Element):

        class PropTypes:
            todos: Required[List[TodoObject]]

        def render(self, context):
            return <ul>{[<Todo todo={todo} /> for todo in self.todos]}</ul>


Yes, it's as simple as that: you use ``<Todo...>`` for the ``Todo`` component as you would use an HTML tag. The only difference is that for html tags, you don't need to import them directly (simple import ``html`` from ``mixt``), and by convention we write them in lower-case. For normal components, you have to import them (you can still do ``from mylib import components`` and ``<components.MyComponent ...>``) and use the exact case.

Notice how we required a list, and passed it into the ``<ul>`` via a list-comprehension in curly-braces.

You can do things differently if you want.

Like separating the list comprehension from the html:

.. code-block:: python

    def render(self, context):
        todos = [
            <Todo todo={todo} />
            for todo
            in self.todos
        ]
        return <ul>{todos}</ul>

Or in a dedicated method (that would be useful for testing):

.. code-block:: python

    def render_todos(self, todos):
        return [
            <Todo todo={todo} />
            for todo
            in todos
        ]

    def render(self, context):
        return <ul>{self.render_todos(self.todos)}</ul>


It's up to you: at the end it's just python.

Let's see what is rendered by this component:

.. code-block:: python

    todos = [TodoObject("foo"), TodoObject("bar"), TodoObject("baz")]
    print(<TodoList todos={todos} />)

.. code-block:: html

    <ul><li>foo</li><li>bar</li><li>baz</li></ul>


And finally we have our ``TodoApp`` component that encapsulate the form and the list:

.. code-block:: python

    class TodoApp(Element):

        class PropTypes:
            todos: Required[List[TodoObject]]
            type: DefaultChoices = ['todo', 'thing']

        def render(self, context):
            return \
                <div>
                    <h1>The "{self.type}" list</h1>
                    <TodoForm type={self.type} />
                    <TodoList todos={self.todos} />
                </div>

.. code-block:: python

    todos = [TodoObject("foo"), TodoObject("bar"), TodoObject("baz")]
    print(<TodoList todos={todos} type="thing" />)

.. code-block:: html

    <div><h1>The "thing" list</h1><form>...</form><ul><li>foo</li><li>bar</li><li>baz</li></ul></div>


Let's pass this HTML to an HTML beautifier:

.. code-block:: html

    <div>
        <h1>The "thing" list</h1>
        <form method="post" action="/thing/add">
            <label>New thing: </label>
            <input type="text" name="todo" />
            <button type="submit">Add</button>
        </form>
        <ul>
            <li>foo</li>
            <li>bar</li>
            <li>baz</li>
        </ul>
    </div>

And that's it, we have our todo-list app! To use it in a page, just create a component that will render the html base markup and integrate the ``TodoApp`` component in it. You don't even need a component:

.. code-block:: python

    todos = [TodoObject("foo"), TodoObject("bar"), TodoObject("baz")]

    print(
        <html>
            <body>
                <TodoApp todos={todos} type="thing" />
            </body>
        </html>
    )

The beautified output would be:

.. code-block:: html

    <html>

    <body>
        <div>
            <h1>The "thing" list</h1>
            <form method="post" action="/thing/add">
                <label>New thing: </label>
                <input type="text" name="todo" />
                <button type="submit">Add</button>
            </form>
            <ul>
                <li>foo</li>
                <li>bar</li>
                <li>baz</li>
            </ul>
        </div>
    </body>

    </html>


Overriding a component
======================

We have a generic todo-list, but following the available types of todo, we may want to have a "todo-list" and a "thing-list".

We already have the todo list because our ``TodoApp`` has a type of ``todo`` by default.

So let's create a ``ThingApp``.


Inheritance
-----------

The first way of doing this is to inherit from our ``TodoApp``. But by inheriting we cannot remove props from the parent (it's not really true, we'll see this later), so we still have the ``type`` prop by default. But we don't want to accept anything else than "thing". So we can redefine the ``type`` prop like this:

.. code-block:: python

    class ThingApp(TodoApp):
        class PropTypes:
            type: DefaultChoices = ['thing']

Let's use this component:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} />)

.. code-block:: html

    <div><h1>The "thing" list</h1><form method="post" action="/thing/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form><ul><li>foo</li></ul></div>

If we try to pass "todo" for the ``type`` props, it won't work:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} type="todo" />)

.. code-block:: python

    mixt.exceptions.InvalidPropChoiceError:
    <ThingApp>.type: `todo` is not a valid choice for this prop (must be in ['thing'])

But still, it's strange to be able to pass a type.


Parent components
-----------------

Let's try another way: A parent component. A component that does nothing else that doing things with its children and returning it. What we want here, is a component that will return a ``TodoApp`` with the ``type`` prop forced to "thing".

Let's do this

.. code-block:: python

    class ThingApp(Element):
        class PropTypes:
            todos: Required[List[TodoObject]]

        def render(self, context):
            return <TodoApp todos={self.todos} type="thing" />

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} />)

.. code-block:: html

    <div><h1>The "thing" list</h1><form method="post" action="/thing/add"><label>New todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form><ul><li>foo</li></ul></div>


It works, and this time, we cannot pass the ``type`` prop:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} />)

.. code-block:: python

    mixt.exceptions.InvalidPropNameError: <ThingApp>.type: is not an allowed prop


PropTypes DRYness
-----------------

Notice how we had to define the type for the ``todos`` props. Both in ``TodoApp`` and ``TodoThing``.

There are many ways to handle that.

The first one would be to ignore the type in ``ThingApp`` because it will be checked in ``TodoApp``. So we'll use the type ``Any``:


.. code-block:: python

    from typing import Any

    #...

    class ThingApp(Element):
        class PropTypes:
            todos: Any

     #...


Let's try with a valid list of todos:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} />)

.. code-block:: html

    <div><h1>The "thing" list</h1><form>...</form><ul><li>foo</li></ul></div>


But what if we pass something else?

.. code-block:: python

    print(<ThingApp todos="foo, bar" />)

.. code-block:: python

    mixt.exceptions.InvalidPropValueError:
    <TodoApp>.todos: `foo, bar` is not a valid value for this prop (type: <class 'str'>, expected: List[TodoObject])

It works as expected but the error is reported at the ``TodoApp`` level, which is perfectly normal.

Another way would be to defined the type at a higher level:

.. code-block:: python

    TodoObjects = Required[List[TodoObject]]

    class TodoApp(Element):
        class PropTypes:
            todos: TodoObjects
     # ...

    class ThingApp(Element):
        class PropTypes:
            todos: TodoObjects
     # ...

Now if we pass something else, we have the error reported at the correct level:

.. code-block:: python

    print(<ThingApp todos="foo, bar" />)

.. code-block:: python

    mixt.exceptions.InvalidPropValueError:
    <TodoThing>.todos: `foo, bar` is not a valid value for this prop (type: <class 'str'>, expected: List[TodoObject])


But if you can't or don't want to do that, you can keep the type defined in ``TodoApp`` et use the ``prop_type`` class method of a component to get the type of a prop:

.. code-block:: python

    class ThingApp(Element):
        class PropTypes:
            todos: TodoApp.prop_type("todos")
     # ...

But does it really matter to have the error raised for ``ThingApp`` or ``TodoApp``? Because at the end, it's really ``TodoApp`` that have to do the check.

So this should be a way to do this in a more generic way..


Function
--------

We saw earlier that a component can be a single function to render a component. It just have to return a component, an html tag. One difference with class components is that there is not ``PropTypes`` so no validation. But... it's exactly what we need.

We want our ``ThingApp`` to accept some props (the ``todos`` prop), and return a ``TodoApp`` with a specific ``type`` prop.

So we could do:

.. code-block:: python

    def ThingApp(todos):
        return <TodoApp type="thing" todos={todos} />

Here we can see that we cannot pass ``type`` to ``ThingsApp``, it is not a valid argument.

Let's try it:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} />)

.. code-block:: html

    <div><h1>The "thing" list</h1><form>...</form><ul><li>foo</li></ul></div>


Here we have only one prop to pass so it's easy. But imagine if we have many ones. We can use the ``{**props}`` syntax:

.. code-block:: python

    def ThingApp(**props):
        return <TodoApp type="thing" {**props} />


And you can do with even fewer characters (if it counts):

.. code-block:: python

    ThingApp = lambda **props: <TodoApp type="thing" {**props} />


These two fonctions behave exactly the same.

And you cannot pass a ``type`` prop because it would be a python error, as it would be passed twice to ``TodoApp``:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} type="thing" />)

.. code-block:: python

    TypeError: BaseMetaclass object got multiple values for keyword argument 'type'


(yes it talks about ``BaseMetaclass`` which is the metaclass that creates our components classes)

And any other wrong props would be validated by ``TodoApp``:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} foo="bar" />)

.. code-block:: python

    mixt.exceptions.InvalidPropNameError: <TodoApp>.foo: is not an allowed prop

With this in mind, we could have created a generic fonction that force the type of any component accepting a ``type`` prop:

.. code-block:: python

    Thingify = lambda component, **props: <component type="thing" {**props} />

.. code-block:: python

    print(<Thingify component={TodoApp} todos={[TodoObject("foo")]} />)

.. code-block:: html

    <div><h1>The "thing" list</h1><form>...</form><ul><li>foo</li></ul></div>


The rendered component is ``TodoApp``, the ``type`` prop is "thing" and the other props (here only ``todos``) are correctly passed.


Higher-order components
-----------------------

Now extend this concept to a more generic case: "higher-order components". In `React a "high order component" <https://reactjs.org/docs/higher-order-components.html>`_, is "a function that takes a component and returns a new component."


The idea is:

.. code-block:: python

    EnhancedComponent = higherOrderComponent(WrappedComponent)

A classic way of doing it is to return a new component class:

.. code-block:: python

    def higherOrderComponent(WrappedComponent):

        class HOC(Element):
            __display_name__ = f"higherOrderComponent({WrappedComponent.__display_name__})"

            class PropTypes(WrappedComponent.PropTypes):
                pass

            def render(self, context):
                return <WrappedComponent {**self.props}>{self.childre()}</WrappedComponent>

        return HOC

Notice how we set the ``PropTypes`` class to inherit from the one of the wrapped component, and how we pass all the props to the wrapped component, along with the children. With the returned component will accept the same props, with the same types, as the wrapped one.

And also notice the ``__display_name__``. It will be used in exceptions to let you now the component that raised it. Here, without forcing it, it would have been set to ``HOC``, which is not helpful. Instead, we indicate that it is a transformed version of the passed component.

Here it is a function that does nothing useful.

In our example we could have done this:

.. code-block:: python

    def thingify(WrappedComponent):

        class HOC(Element):
            __display_name__ = f"thingify({WrappedComponent.__display_name__})"

            class PropTypes(WrappedComponent.PropTypes):
                __exclude__ = {'type'}

            def render(self, context):
                return <WrappedComponent type="thing" {**self.props}>{self.children()}</WrappedComponent>

        return HOC


Two important things here:

- notice how we use ``__exclude__ = {'type'}`` to remove the ``type`` prop from the ones we inherit from ``WrappedComponent.PropTypes``. So the returned component will expect the exact same props as the wrapped one, except for ``type``.
- we added ``{self.children()}`` in the rendered wrapped component, because even if we actually know that the component we'll wrap, ``TodoApp``, doesn't take children (it could but it does nothing with them), we cannot say in advance that it will always be the case, and also that this higher-order component won't be used to wrap another component than ``TodoApp``. So it's better to always do this.

And now we can create our ``ThingApp``:

.. code-block:: python

    ThingApp = thingify(TodoApp)


And use it:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} />)

.. code-block:: html

    <div><h1>The "thing" list</h1><form>...</form><ul><li>foo</li></ul></div>


If we try to pass the type:

.. code-block:: python

    print(<ThingApp todos={[TodoObject("foo")]} type="thing" />)


.. code-block:: python

    mixt.exceptions.InvalidPropNameError: <thingify(TodoApp)>.type: is not an allowed prop


So as planned, we cannot pass the type. And notice how the ``__display_name__`` is used.


Let's think about how powerful this is.

Let say we want to keep our ``TodoApp`` take a list of ``TodoObject``. But we want to get them from a "source".

We can even directly write it this new higher-order-component in a generic way:

.. code-block:: python

    def from_data_source(WrappedComponent, prop_name, get_source):

        class HOC(Element):
            __display_name__ = f"from_data_source({WrappedComponent.__display_name__})"

            class PropTypes(WrappedComponent.PropTypes):
                __exclude__ = {prop_name}

            def render(self, context):
                props = self.props.copy()
                props[prop_name] = get_source(props, context)
                return <WrappedComponent {**props}>{self.children()}</WrappedComponent>

        return HOC


This time, the function ``from_data_source`` takes two arguments in addition to the ``WrappedComponent``:

- ``prop_name``: it's the name of the prop of the wrapped component to fill with some data
- ``get_source``: it's a function that will be called to get the data

Look how we inherited the ``PropTypes`` from the wrapped component and how we excluded ``prop_name``. So we don't have (and can't) pass the data to our new component.

And then in ``render``, we set a prop to pass to ``WrappedComponent`` with the result of a call to ``get_source``.

So let's write a very simple function (this could be a complicated one with caching, filtering...) that take the props and the context, and returns some data:

.. code-block:: python

    def get_todos(props, context):
        # here it could be a call to a database
        return [
            TodoObject("fooooo"),
            TodoObject("baaaar"),
        ]


And we can compose our component:

.. code-block:: python

    SourcedTodoApp = from_data_source(TodoApp, 'todos', get_todos)
    ThingApp = thingify(SourcedTodoApp)


And run it:

.. code-block:: python

    print(<ThingApp />)

.. code-block:: html

    <div><h1>The "thing" list</h1><form>...</form><ul><li>fooooo</li><li>baaaar</li></ul></div>


It works as expected, and the data is fetched only when the component needs to be rendered.


Context
=======

So, we have a todo list, that can fetch data from an external source. But we may want the data to be different depending on the user.

What we can do, it's at the main level, get our user and passing it on every component to be sure that each component is able to get the current logged in user.

Wouldn't it be cumbersome?

Solving this use case is the exact purpose of the ``Context`` concept provided by ``mixt``. It is, of course, `inspired by the concept of context in React <https://reactjs.org/docs/context.html>`_.

And as they said:

    Context is designed to share data that can be considered “global” for a tree of React components, such as the current authenticated user, theme, or preferred language.

Creating a context is as simple as creating a component, except that it will inherits from ``BaseContext`` and doesn't need a ``render`` method (it will render its children).

And it takes a ``PropTypes`` class, that define the types of data the context will accept and pass down the tree.

So let's create our context that will hold the id of the authenticated user.

.. code-block:: python

    from mixt import BaseContext

    class UserContext(BaseContext):
        class PropTypes:
            authenticated_user_id: Required[int]


Now, we want to update our ``get_todos`` method to take the ``authenticated_user_id`` into account.

Remember, we passed it the props and the context. The context will be useful here:

.. code-block:: python

    def get_todos(props, context):
        return {
            1:[
                TodoObject("1-1"),
                TodoObject("1-2"),
            ],
            2: [
                TodoObject("2-1"),
                TodoObject("2-2"),
            ]
        }[context.authenticated_user_id]


And now we can render our app with the context:

.. code-block:: python

    print(
        <UserContext authenticated_user_id=1>
            <ThingApp />
        </UserContext>
    )

.. code-block:: python

    <div><h1>The "thing" list</h1><form>...</form><ul><li>1-1</li><li>1-2</li></ul></div>


We can see the todo entries for the user 1.

Let's try with the user 2:

.. code-block:: python

    print(
        <UserContext authenticated_user_id=2>
            <ThingApp />
        </UserContext>
    )

.. code-block:: python

    <div><h1>The "thing" list</h1><form>...</form><ul><li>2-1</li><li>2-2</li></ul></div>

We can see the todo entries for the user 2.

In this case of course we could have passed the user id as a prop. But imagine the todo app being deep in the components tree, it's a lot easier to pass it this way.

But as said in the React documentation:

    Don’t use context just to avoid passing props a few levels down. Stick to cases where the same data needs to be accessed in many components at multiple levels.

When there is no context, the ``context`` argument of the ``render`` method is set to ``EmptyContext`` and not to ``None``. So you can directly use the ``has_prop`` method to check if a prop is available via the context.

Let's update the ``get_todos`` functions to return an empty list of todo objects if there is not authenticated user.

.. code-block:: python

    def get_todos(props, context):
        if not context.has_prop('authenticated_user_id') or not context.authenticated_user_id:
            return []
        return {
            1:[
                TodoObject("1-1"),
                TodoObject("1-2"),
            ],
            2: [
                TodoObject("2-1"),
                TodoObject("2-2"),
            ]
        }[context.authenticated_user_id]

Let's try this:

.. code-block:: python

    print(<ThingApp />)

.. code-block:: python

    <div><h1>The "thing" list</h1><form>...</form><ul></ul></div>


And it still works with a user in the context:

.. code-block:: python

    print(
        <UserContext authenticated_user_id=1>
            <ThingApp />
        </UserContext>
    )

.. code-block:: python

    <div><h1>The "thing" list</h1><form>...</form><ul><li>1-1</li><li>1-2</li></ul></div>


**Important note about contexts**: you can have many contexts! But defining the same prop in many contexts may lead to undefined behaviour.


Style and Javascript
====================

Everybody loves a beautiful design, and maybe some interaction.

It is easily doable: we generate HTML and HTML can contains some CSS and JS.

Let's add some interaction first: when adding an item in the ``TodoForm``, let's add it to the list.

First we add in our ``TodoForm`` component a ``render_javascript`` method that will host our (bad, we could do better but it's not the point) javascript:

.. code-block:: python

    class TodoForm(Element):
        # ...

        def render_javascript(self, context):
            return html.Raw("""
    function on_todo_add_submit(form) {
        var text = form.todo.value;
        alert(text);
    }
            """)

To start we only display the new todo text.

Now update our ``render`` method to return this javascript (note that the use of a ``render_javascript`` method is only to separate concerns, it could have been in the ``render`` method directly.

.. code-block:: python

    class TodoForm(Element):
        # ...

        def render(self, context):
            # ...

            return \
                <Fragment>
                    <script>{self.render_javascript(context)}</script>
                    <form method="post" action={add_url} onsubmit="return on_todo_add_submit(this);">
                        <label>New {self.type}: </label><itext name="todo" />
                        <button type="submit">Add</button>
                    </form>
                </Fragment>

Notice the ``Fragment`` tag. It's a way to encapsulate many elements to be returned, like in React. It could have been a simple list but with comas at the end:

.. code-block:: python

    return [
        <script>...</script>,
        <form>
            ...
        </form>
    ]

Now we want to add an item to the list. It's not the role of the ``TodoForm`` to do this, but to the list. So we'll add some JS in the ``TodoList`` component: a function that take some text and create a new entry.

As for ``TodoForm``, we add a ``render_javascript`` method with (still bad) javascript:

.. code-block:: python

    class TodoList(Element):
        # ...

        def render_javascript(self, context):

            todo_placeholder = <Todo todo={TodoObject(text='placeholder')} />

            return html.Raw("""
    TODO_TEMPLATE = "%s";
    function add_todo(text) {
        var html = TODO_TEMPLATE.replace("placeholder", text);
        var ul = document.querySelector('#todo-items');
        ul.innerHTML = html + ul.innerHTML;
    }
            """ % (todo_placeholder))

And we update our ``render`` method to add the ``<script>`` tag and an ``id`` to the ``ul`` tag, used in the javascript:

.. code-block:: python

    class TodoList(Element):
        # ...

        def render(self, context):
            return \
                <Fragment>
                    <script>{self.render_javascript(context)}</script>
                    <ul id="todo-items">{[<Todo todo={todo} /> for todo in self.todos]}</ul>
                </Fragment>

And now we can update the ``render_javascript`` method of the ``TodoForm`` component to use our new ``add_toto`` javascript function:


.. code-block:: python

    class TodoForm(Element):
        # ...

        def render_javascript(self, context):
            return html.Raw("""
    function on_todo_add_submit(form) {
        var text = form.todo.value;
        add_todo(text);
    }
            """)

And that's all. Nothing special, in fact.

But let's take a look at the output of ou ``TodoApp``:

.. code-block:: python

    print(
        <UserContext authenticated_user_id=1>
            <ThingApp />
        </User>
    )

The beautified output is:

.. code-block:: html

    <div>
        <h1>The "thing" list</h1>
        <script>
            function on_todo_add_submit(form) {
                var text = form.todo.value;
                add_todo(text);
            }
        </script>
        <form method="post" action="/thing/add" onsubmit="return on_todo_add_submit(this);">
            <label>New thing: </label>
            <input type="text" name="todo" />
            <button type="submit">Add</button>
        </form>
        <script>
            TODO_TEMPLATE = "<li>placeholder</li>";

            function add_todo(text) {
                var html = TODO_TEMPLATE.replace("placeholder", text);
                var ul = document.querySelector('#todo-items');
                ul.innerHTML = html + ul.innerHTML;
            }
        </script>
        <ul id="todo-items">
            <li>1-1</li>
            <li>1-2</li>
        </ul>
    </div>

So we have many ``script`` tag. It could be great to have only one.

Collectors
----------

``mixt`` comes with a way to "collect" parts of what is rendered to put them somewhere else. We have at our disposal two simple collectors, to be used as components: ``JSCollector`` and ``CSSCollector``.

These components collect parts of their children tree.

Collector.Collect
^^^^^^^^^^^^^^^^^

The first way is by using the collector ``Collect`` tag.

First let's change our main call:

.. code-block:: python

    from mixt import JSCollector

    print(
        <JSCollector render_position="after">
            <UserContext authenticated_user_id=1>
                <ThingApp />
            </User>
        </JSCollector>
    )

This will collect the content of all the ``JSCollector.Collect`` tag.

Let's update our ``TodoForm`` and replace our ``script`` tag by a ``JSCollector.Collect`` tag:

.. code-block:: python

    class TodoForm(Element):
        # ...

        def render(self, context):

            if callable(self.add_url):
                add_url = self.add_url(self.type)
            else:
                add_url = self.add_url

            return \
                    <JSCollector.Collect>{self.render_javascript(context)}</JSCollector.Collect>
                    <form method="post" action={add_url} onsubmit="return on_todo_add_submit(this);">
                        <label>New {self.type}: </label><itext name="todo" />
                        <button type="submit">Add</button>
                    </form>
                </Fragment>


We can do the same with the ``TodoList``:

.. code-block:: python

    class TodoList(Element):
        # ...

        def render(self, context):
            return \
                <Fragment>
                    <JSCollector.Collect>{self.render_javascript(context)}</JSCollector.Collect>
                    <ul id="todo-items">{[<Todo todo={todo} /> for todo in self.todos]}</ul>
                </Fragment>


Now let's run our updated code:

.. code-block:: python

    print(
        <JSCollector render_position="after">
            <UserContext authenticated_user_id=1>
                <ThingApp />
            </User>
        </JSCollector>
    )

The beautified output is:

.. code-block:: html

    <div>
        <h1>The "thing" list</h1>
        <form method="post" action="/thing/add" onsubmit="return on_todo_add_submit(this);">
            <label>New thing: </label>
            <input type="text" name="todo" />
            <button type="submit">Add</button>
        </form>
        <ul id="todo-items">
            <li>1-1</li>
            <li>1-2</li>
        </ul>
    </div>
    <script type="text/javascript">
        function on_todo_add_submit(form) {
            var text = form.todo.value;
            add_todo(text);
        }

        TODO_TEMPLATE = "<li>placeholder</li>";

        function add_todo(text) {
            var html = TODO_TEMPLATE.replace("placeholder", text);
            var ul = document.querySelector('#todo-items');
            ul.innerHTML = html + ul.innerHTML;
        }
    </script>

As you can see, all the scripts are in a single ``script`` tag, at the end. More precisely, at the end of where the ``JSCollector`` tag was, because we used ``render_position="after"``. Another possibility is ``render_position="before"`` to put this where the ``JSCollector`` tag started.

All of this work exactly the same way for the ``CSSCollector`` tag, where content is put in a ``<style type="text/css>`` tag.

render_[js|css] methods
^^^^^^^^^^^^^^^^^^^^^^^

As using JS/CSS is quite common in the HTML world, we added some sugar to make all of this even easier to do.

If you have a ``render_js`` method, the ``JSCollector`` will automatically collect the result of this method. Same for ``CSSSelector`` and the ``render_css`` method.

With this, no need for a ``JSCollector.Collect`` tag.

To make this work in our example, in ``TodoForm`` and ``TodoList``:

- remove the ``JSCollector.Collect`` tags
- remove the now unneeded ``Fragment`` tags
- rename the ``render_javascript`` methods to ``render_js``.
- remove the call to ``html.Raw`` in ``render_js`` as it's not needed when the collector calls ``render_js`` itself: if the output is a string, it is considered a "raw" one

This way we have exactly the same result.

render_[js|css]_global methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It works now because we only have one instance of a child with a ``render_js`` method.

But if we have many children, this method will be called for each child. If fact, it should only contains code that is very specific to this instance.

To serve js/css only once for a Component class, we have to use ``render_js_global`` or ``render_css_global`` (expected to be ``classmethod``)

It will be collected the first time, and only the first time, an instance is found, before collecting the ``render_js`` method.

So here, we can change our ``render_js`` to ``render_js_global``, decorate them with ``@classmethod`` and it will still work the same.

references
^^^^^^^^^^

We now are able to regroup javascript or style. But what if we want to put it elsewhere, like in the ``head`` tag or at the end of the ``body`` tag?

It's possible with references, aka "refs". It's the same context as in React, without the DOM part of course.

You create a ref, pass it to a component, and you can use it anywhere.

Let's update our main code to do this.

First we create a ref.

.. code-block:: python

    from mixt import Ref

    js_ref = Ref()


This will create a new object that will hold a reference to a component. In a component, you don't need to import ``Ref`` and can use ``js_ref = self.add_ref()``, but we are not in a component here.


To save a ref, we simply pass it to the ``ref`` prop:

.. code-block:: python

    <JSCollector ref={js_ref} >...</JSCollector>


Notice that we removed the ``render_position`` prop, because now we don't want the JS to be put before or after the tag, but elsewhere.

To access the component referenced by a ref, use the ``current`` attribute:

.. code-block:: python

    js_collector = js_ref.current

Of course this can be done only AFTER the rendering.

How can we use this to add a ``script`` tag in our ``head``.

First update our html to include the classic ``html``, ``head`` and ``body`` tags:

.. code-block:: python

    return str(
        <html>
            <head>
            </head>
            <body>
                <JSCollector ref={js_ref} >
                    <UserContext authenticated_user_id=1>
                        <ThingApp />
                    </UserContext>
                </JSCollector>
            </body>
        </html>
    )

At this point we don't have any ``script`` tag in the output:

.. code-block:: html

    <html>

    <head></head>

    <body>
        <div>
            <h1>The "thing" list</h1>
            <form method="post" action="/thing/add" onsubmit="return on_todo_add_submit(this);">
                <label>New thing: </label>
                <input type="text" name="todo" />
                <button type="submit">Add</button>
            </form>
            <ul id="todo-items">
                <li>1-1</li>
                <li>1-2</li>
            </ul>
        </div>
    </body>

    </html>


First thing to know: a collector is able to render all the things it collected by calliing its ``render_collected`` method.

And remembering that it already includes the ``script`` tag, we may want to do this:

.. code-block:: python

    # ...
    <head>
        {js_ref.current.render_collected()}
    </head>
    # ...

but this doesn't work:

.. code-block:: python

    AttributeError: 'NoneType' object has no attribute 'render_collected'


It's because we try to access the current value at render time. It must be done after.

For this, we can use a feature of ``mixt``: if something added to the tree is a callable, it will be called after the rendering, when converting to string.

So we can use for example a lambda:

.. code-block:: python

    # ...
    <head>
        {lambda: js_ref.current.render_collected()}
    </head>
    # ...

And now it works:

.. code-block:: html

    <html>

    <head>
        <script type="text/javascript">
            function on_todo_add_submit(form) {
                var text = form.todo.value;
                add_todo(text);
            }

            TODO_TEMPLATE = "<li>placeholder</li>";

            function add_todo(text) {
                var html = TODO_TEMPLATE.replace("placeholder", text);
                var ul = document.querySelector('#todo-items');
                ul.innerHTML = html + ul.innerHTML;
            }
        </script>
    </head>

    <body>
        <div>
            <h1>The "thing" list</h1>
            <form method="post" action="/thing/add" onsubmit="return on_todo_add_submit(this);">
                <label>New thing: </label>
                <input type="text" name="todo" />
                <button type="submit">Add</button>
            </form>
            <ul id="todo-items">
                <li>1-1</li>
                <li>1-2</li>
            </ul>
        </div>
    </body>

    </html>


User guide conclusion
=====================

Hurray we made it! All the main features of ``mixt`` explained. You can now use ``mixt`` in your own projects.

***
API
***

As a next step, you may want to read `the API documentation <https://twidi.github.io/mixt/api.html>`_.
