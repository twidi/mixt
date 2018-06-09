from mixt.examples import simple, simple_pure_python
from mixt.examples.todolist import __main__ as todolist


def test_simple():
    assert simple.render_example() == """<div title="Greeting">Hello, World</div>"""


def test_simple_pure_python():
    assert simple_pure_python.render_example() == """<div title="Greeting">Hello, World</div>"""


def test_todolist():
    assert todolist.render_example() == ''.join(line.strip() for line in """
<html>

<body>
    <main class="app">
        <h1>The todo list</h1>
        <form method="post" action="/todo/add">
            <label>New Todo: </label>
            <input type="text" name="todo" />
            <button type="submit">Add</button>
        </form>
        <ul>
            <li>foo
                <form method="post" action="/todo/1/remove">
                    <button type="submit">Remove</button>
                </form>
            </li>
            <li>bar
                <form method="post" action="/todo/2/remove">
                    <button type="submit">Remove</button>
                </form>
            </li>
            <li>baz
                <form method="post" action="/todo/3/remove">
                    <button type="submit">Remove</button>
                </form>
            </li>
        </ul>
    </main>
</body>

</html>""".split("\n"))
