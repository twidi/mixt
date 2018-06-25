"""Functions to get/activate/deactivate dev-mode.

In "dev-mode", active by default, a lots of costly checks will be done when trying to set
the props of elements to ensure that the types match the ones defined in ``PropTypes``.

It's active by default to let you be sure that your code is correct.

Your tests must run in "dev-mode".

But in production, you trust your tests, and don't need to enforce type checking of your props.

And as "costly" means "time" or "money", you are encouraged to deactivate the "dev-mode" in
production.

The included functions can be imported from ``mixt.dev_mode`` or, by convenience, from
``mixt``.

Examples
--------
# This example shows how in non-dev mode, props are not validated.
# This should of course be covered by tests so this cannot happen.

>>> class Greeting(Element):
...     class PropTypes:
...         name: Required[str]
...
...     def render(self, context):
...         return <div>Hello, <strong>{self.name}</strong></div>

>>> print(in_dev_mode())  # dev-mode is on by default
True

>>> wrong_data = {"firstname": "John"}
>>> print(<Greeting name={wrong_data} />)
Traceback (most recent call last):
...
mixt.exceptions.InvalidPropValueError: <Greeting>.name: `{'firstname': 'John'}` is not a valid
value for this prop (type: <class 'dict'>, expected: <class 'str'>)

>>> with override_dev_mode(False):
...     print(in_dev_mode())
...     print(<Greeting name={wrong_data} />)
False
<div>Hello, <strong>{'firstname': 'John'}</strong></div>

"""

from .proptypes import BasePropTypes


__all__ = ["set_dev_mode", "unset_dev_mode", "override_dev_mode", "in_dev_mode"]

set_dev_mode = BasePropTypes.__set_dev_mode__
unset_dev_mode = BasePropTypes.__unset_dev_mode__
override_dev_mode = BasePropTypes.__override_dev_mode__
in_dev_mode = BasePropTypes.__in_dev_mode__
