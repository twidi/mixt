# coding: mixt
from mixt import html
def test():
    assert str(<Fragment>
                   foo
                   {'foo'}
               </Fragment>) == "foo foo"
