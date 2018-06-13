from mixt.examples import simple, simple_pure_python
from mixt.examples.user_guide import (
    __main__ as user_guide_main,
    mixt as user_guide_mixt,
    pure_python as user_guide_python,
)


def test_simple():
    expected = """<div title="Greeting">Hello, World</div>"""
    assert simple.render_example() == expected
    assert simple_pure_python.render_example() == expected


def test_user_guide():

    expected = """\
<html><head><script type="text/javascript">
function on_todo_add_submit(form) {
    var text = form.todo.value;
    add_todo(text);
}

TODO_TEMPLATE = "<li>placeholder</li>";
function add_todo(text) {
    var html = TODO_TEMPLATE.replace("placeholder", text);
    var ul = document.querySelector('#todo-items');
    ul.innerHTML = html + ul.innerHTML;
}
</script>""" + ''.join(line.strip() for line in """
    </head>
    <body>
        <div>
            <h1>The "thing" list</h1>
            <form method="post" action="/thing/add" onsubmit="return on_todo_add_submit(this);">
                <label>New thing: </label>
                <input type="text" name="todo" />
                <button type="submit">Add</button>
            </form>
            <ul id="todo-items">
                <li>1-1</li>
                <li>1-2</li>
            </ul>
        </div>
    </body>
</html>""".split("\n"))

    assert user_guide_main.render_example() == expected
    assert user_guide_mixt.render_example() == expected
    assert user_guide_python.render_example() == expected
