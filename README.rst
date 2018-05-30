####
MIXT
####

Write html components directly in python and you have a beautiful but controversial MIXTure

Based on ``pyxl``.

More text to come ;)


************
Installation
************

Run these two commands. The second one will tell python how to understand files with html inside.

.. code-block:: shell

   pip install mixt
   mixt-post-install


***********
Development
***********

Clone the git project then:

.. code-block:: shell

   make dev

To make sur the ``mixt`` codec is installed, check it this way:

.. code-block:: shell

   $ python src/mixt/pyxl/example.py
   <html><body>Hello World!</body></html>

After having done some code:

.. code-block:: shell
    make tests

.. code-block:: shell

    make lint
