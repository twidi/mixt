# coding: mixt
from mixt import html
def test():
    assert str(<Fragment>
                   {'foo'}
                   <if cond="{True}">
                       {'foo'}
                   </if>
               </Fragment>) == "foofoo"
