from bottle import Bottle, redirect, response, run

from .app import files_to_render


def setup_routing(app: Bottle):
    app.route('/', callback=lambda: redirect('/index.html'))

    for filename, title, callable, args in files_to_render():

        def get_callback(filename, callable, args):
            content_type = None
            if filename.endswith('.js'):
                content_type = "text/javascript"
            elif filename.endswith('.css'):
                content_type = "text/css"

            def callback():
                if content_type:
                    response.content_type = content_type
                return str(callable(**args))

            return callback

        app.route(f'/{filename}', callback=get_callback(filename, callable, args))


app = Bottle()
setup_routing(app)


run(
    app=app,
    host='0.0.0.0',
    port=8080,
    # reloader=True
)
