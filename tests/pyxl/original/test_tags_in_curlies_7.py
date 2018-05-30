# coding: mixt
from mixt.pyxl import html
def test():
    assert str(<Fragment> {' "<br />" '} </Fragment>) == '''  &quot;&lt;br /&gt;&quot;  '''
