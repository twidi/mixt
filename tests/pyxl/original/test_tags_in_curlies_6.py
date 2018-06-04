# coding: mixt
from mixt import html
def test():
    assert str(<Fragment> {' "<br /> '} </Fragment>) == '''  &quot;&lt;br /&gt;  '''
