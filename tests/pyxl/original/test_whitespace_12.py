# coding: mixt
from mixt import html
def test():
    # Presence of comments should not affect contents of tags. (In old pyxl, this led to differences
    # in whitespace handling.)
    assert str(get_frag1()) == str(get_frag2())

def get_frag1():
    return <Fragment>{'foo'}
    </Fragment>

def get_frag2():
    return <Fragment>{'foo'} # lol
    </Fragment>
