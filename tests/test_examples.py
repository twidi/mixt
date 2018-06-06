from mixt.examples import simple, simple_pure_python


def test_simple():
    assert simple.render_example() == """<div title="Greeting">Hello, World</div>"""


def test_simple_pure_python():
    assert simple_pure_python.render_example() == """<div title="Greeting">Hello, World</div>"""
