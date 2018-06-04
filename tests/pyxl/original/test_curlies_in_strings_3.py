# coding: mixt
from mixt import html
def test():
    assert str(<Fragment> "{' "foobar" '}" </Fragment>) == ''' " &quot;foobar&quot; " '''
