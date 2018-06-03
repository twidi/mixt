# coding: mixt
from mixt.pyxl import html
def test():
    a = (<br />)
    b = (<div>
             foo
         </div>)
    assert str(b) == "<div>foo</div>"
    assert a  # pacify lint
