####
MIXT
####

Write html components directly in python and you have a beautiful but controversial MIXTure.

Yes, **controversial**.

**If you don't like it, ignore it** (but you can use this without the html-in-python part, see below ;))

*Based* on `pyxl <https://github.com/gvanrossum/pyxl3/>`_. Python 3.6+ only.

*****
Usage
*****

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


There is more. Doc will come soon, we are still in early alpha :)

************
Installation
************

Run these two commands. The second one will tell python how to understand files with html inside.

.. code-block:: shell

   pip install mixt
   mixt-post-install

To check that everything is ready, run:

.. code-block:: shell

   python -m mixt.example

You should have this output:

.. code-block::

   <div title="Greeting">Hello, World</div>

If you don't want to use the html-in-python stuff, don't run ``mixt-post-install``. And then test with (to have the same output):

.. code-block:: shell

   python -m mixt.example_pure_python

***********
Development
***********

Clone the git project then:

.. code-block:: shell

   make dev


To check that everything is ready, run:

.. code-block:: shell

   python -m mixt.example


You should have this output:

.. code-block::

   <div title="Greeting">Hello, World</div>


After having done some code:

.. code-block:: shell

    make tests


.. code-block:: shell

    make lint
