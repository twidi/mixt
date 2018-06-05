# coding: mixt
from mixt import html


def test1():
    assert str(<div class="{'blah'}">
                   blah <a href="%(url)s">blah</a> blah.
               </div>) == """<div class="blah">blah <a href="%(url)s">blah</a> blah.</div>"""


def test2():
    assert str(<div>
                   The owner has not granted you access to this file.
               </div>) == """<div>The owner has not granted you access to this file.</div>"""


def test3():
    a = (<br />)
    b = (<div>
             foo
         </div>)
    assert str(b) == "<div>foo</div>"
    assert a  # pacify lint


def test4():
    assert str(<div class="{ 'foo' }">foo</div>) == '<div class="foo">foo</div>'


def test5():
    assert str(<Fragment>
                   {'foo'}
                   {'bar'}
               </Fragment>) == "foo bar"


def test6():
    assert str(<Fragment>
                   {'foo'}
                   <if cond="{True}">
                       {'foo'}
                   </if>
               </Fragment>) == "foofoo"


def test7():
    assert str(<Fragment>
                   foo
                   {'foo'}
               </Fragment>) == "foo foo"


def test8():
    assert str(<Fragment>{ 'foo' }{ 'foo' }</Fragment>) == "foofoo"


def test9():
    assert str(<div class="foo
                           bar">
               </div>) == '<div class="foo bar"></div>'


def test10():
    assert str(<div class="{'foo'} {'bar'}"></div>) == '<div class="foo bar"></div>'


def test11():

    def get_frag1():
        return <Fragment>
            {'foo'}
        </Fragment>

    def get_frag2():
        return (<Fragment>
            {'foo'}
        </Fragment>)

    # Presence of paretheses around html should not affect contents of tags. (In old pyxl,
    # this led to differences in whitespace handling.)
    assert str(get_frag1()) == str(get_frag2())


def test12():
    def get_frag1():
        return <Fragment>{'foo'}
        </Fragment>

    def get_frag2():
        return <Fragment>{'foo'} # lol
        </Fragment>

    # Presence of comments should not affect contents of tags. (In old pyxl, this led to differences
    # in whitespace handling.)
    assert str(get_frag1()) == str(get_frag2())

