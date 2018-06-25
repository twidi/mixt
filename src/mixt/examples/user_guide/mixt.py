# coding: mixt
# pylint: disable=missing-docstring,invalid-name,redefined-builtin,unused-argument,missing-param-doc,missing-type-doc,unnecessary-lambda
# flake8: noqa: D

"""The final "mixt" version of the todolist app presented in the user-guide.

To create the "pure-python" version:

    cp mixt.py pure_python.py
    black pure_python.py
    sed  -e 's/^# coding: mixt//' -e 's/"mixt"/"pure python"/' -i pure_python.py

"""

from typing import Callable, List, Union

from mixt import BaseContext, DefaultChoices, Element, JSCollector, Ref, Required, html


class TodoObject:
    """A simple object to host a todo entry, with just a text."""
    def __init__(self, text):
        self.text = text


def make_url(type: str) -> str:
    """Will compose a url based on the given type."""
    return f"/{type}/add"


class TodoForm(Element):
    """A Component to render the form used to add a toto entry."""

    class PropTypes:
        add_url: Union[Callable[[str], str], str] = make_url
        type: DefaultChoices = ['todo', 'thing']

    @classmethod
    def render_js_global(cls, context):
        # language=JS
        return """
function on_todo_add_submit(form) {
    var text = form.todo.value;
    add_todo(text);
}
"""

    def render(self, context):

        if callable(self.add_url):
            add_url = self.add_url(self.type)
        else:
            add_url = self.add_url

        return \
            <form method="post" action={add_url} onsubmit="return on_todo_add_submit(this);">
                <label>New {self.type}: </label><itext name="todo" />
                <button type="submit">Add</button>
            </form>


class Todo(Element):
    """A component used to display a todo entry."""

    class PropTypes:
        todo: Required[TodoObject]

    def render(self, context):
        return <li>{self.todo.text}</li>


class TodoList(Element):
    """ A component used to display a list of todo entries."""

    class PropTypes:
        todos: Required[List[TodoObject]]

    @classmethod
    def render_js_global(cls, context):

        todo_placeholder = <Todo todo={TodoObject(text='placeholder')} />

        # language=JS
        return """
TODO_TEMPLATE = "%s";
function add_todo(text) {
    var html = TODO_TEMPLATE.replace("placeholder", text);
    var ul = document.querySelector('#todo-items');
    ul.innerHTML = html + ul.innerHTML;
}
""" % (todo_placeholder)

    def render(self, context):
        return <ul id="todo-items">{[<Todo todo={todo} /> for todo in self.todos]}</ul>


class TodoApp(Element):
    """A component used to render the whole todo app."""

    class PropTypes:
        todos: Required[List[TodoObject]]
        type: DefaultChoices = ['todo', 'thing']

    def render(self, context):
        return \
            <div>
                <h1>The "{self.type}" list</h1>
                <TodoForm type={self.type} />
                <TodoList todos={self.todos} />
            </div>


def thingify(WrappedComponent):
    """A "higher-order component" that force pass `type="thing"` to the wrapped component."""

    class HOC(Element):
        __display_name__ = f"thingify({WrappedComponent.__display_name__})"

        class PropTypes(WrappedComponent.PropTypes):
            __exclude__ = {'type'}

        def render(self, context):
            return <WrappedComponent type="thing" {**self.props}>{self.children()}</WrappedComponent>

    return HOC


def from_data_source(WrappedComponent, prop_name, get_source):
    """A "higher-order component" that fill the `prop_name` prop of the wrapped component with
    content coming from the `get_source` function."""

    class HOC(Element):
        __display_name__ = f"from_data_source({WrappedComponent.__display_name__})"

        class PropTypes(WrappedComponent.PropTypes):
            __exclude__ = {prop_name}

        def render(self, context):
            props = self.props.copy()
            props[prop_name] = get_source(props, context)
            return <WrappedComponent {**props}>{self.children()}</WrappedComponent>

    return HOC


class UserContext(BaseContext):
    """A context that will pass the authenticated user id down the whole components tree."""
    class PropTypes:
        authenticated_user_id: Required[int]


def get_todos(props, context):
    """A "data source" that will return some todo entries depending of the context user id."""
    if not context.has_prop('authenticated_user_id') or not context.authenticated_user_id:
        return []
    return {
        1:[
            TodoObject("1-1"),
            TodoObject("1-2"),
        ],
        2: [
            TodoObject("2-1"),
            TodoObject("2-2"),
        ]
    }[context.authenticated_user_id]



SourcedTodoApp = from_data_source(TodoApp, 'todos', get_todos)
ThingApp = thingify(SourcedTodoApp)


def render_example():
    """Render the html for this example."""

    js_ref = Ref()

    return str(
        <html>
            <head>
                {lambda: js_ref.current.render_collected()}
            </head>
            <body>
                <JSCollector ref={js_ref} >
                    <UserContext authenticated_user_id=1>
                        <ThingApp />
                    </UserContext>
                </JSCollector>
            </body>
        </html>
    )


if __name__ == "__main__":
    print(render_example())
