# coding: mixt

from bottle import route, run

from .app import App


@route('/')
def index():
    return str(<App />)


run(
    host='0.0.0.0',
    port=8080,
    # reloader=True
)
