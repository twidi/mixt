# coding: mixt
from mixt import html


def test1():
    assert str(<Fragment>{'<br />'}</Fragment>) == """&lt;br /&gt;"""


def test2():
    assert str(<Fragment>{'<img src="foo" />'}</Fragment>) == """&lt;img src=&quot;foo&quot; /&gt;"""


def test3():
    assert str(<Fragment>{'<div> foobar </div>'}</Fragment>) == """&lt;div&gt; foobar &lt;/div&gt;"""


def test4():
    assert str(<Fragment>{'<div class="foo"> foobar </div>'}</Fragment>) == """&lt;div class=&quot;foo&quot;&gt; foobar &lt;/div&gt;"""


def test5():
    assert str(<Fragment> {'<img src="{cond}" />'} </Fragment>) == """ &lt;img src=&quot;{cond}&quot; /&gt; """


def test6():
    assert str(<Fragment> {' "<br /> '} </Fragment>) == '''  &quot;&lt;br /&gt;  '''


def test7():
    assert str(<Fragment> {' "<br />" '} </Fragment>) == '''  &quot;&lt;br /&gt;&quot;  '''


def test8():
    assert str(<Fragment>{<br />}</Fragment>) == '''<br />'''


def test9():
    assert str(<Fragment>{<br /> if True else <div></div>}</Fragment>) == '''<br />'''


def test10():
    assert str(<Fragment>{<br /> if False else <div></div>}</Fragment>) == '''<div></div>'''
