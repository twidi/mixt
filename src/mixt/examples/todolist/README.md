# A simple todolist app

With 4 components, represented here in a tree (an component at a level calls the components at the sublevel)

- TodoApp
  - TodoForm
  - TodoList
    - Todo


To test it:

```bash
python -m mixt.examples.todolist
```

```html
<html><body><main class="app"><h1>The todo list</h1><form method="post" action="/todo/add"><label>New Todo: </label><input type="text" name="todo" /><button type="submit">Add</button></form><ul><li>foo<form method="post" action="/todo/1/remove"><button type="submit">Remove</button></form></li><li>bar<form method="post" action="/todo/2/remove"><button type="submit">Remove</button></form></li><li>baz<form method="post" action="/todo/3/remove"><button type="submit">Remove</button></form></li></ul></main></body></html>
```

The output is not really readable, but passing it to a [beautifier](http://htmlformatter.com/) (but not that in HTML spaces are not ignored, so the result is not exactly the same):

```html
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

</html>
```
