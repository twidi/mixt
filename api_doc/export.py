from contextlib import contextmanager
from os import environ
import os.path
import sys

from mixt import set_dev_mode

from .app import files_to_render


def usage():
        print("""\
Export MIXT documentation.

Usage: `python -m api_doc.export path/to/docs/directory`\
""")


def error(text):
    print(text, file=sys.stderr)
    exit(1)


@contextmanager
def log_rendering(path, title, counter):
    counter['files_count'] += 1
    files_count_str = ("{:" + counter['files_chars_len'] + "}").format(counter['files_count'])
    title = f" [{title}]" if title else ""
    print_line = f"[{files_count_str}/{counter['files_total_str']}] Writing {path}{title}"

    print(f"{print_line}...", end="")
    sys.stdout.flush()

    length = yield
    yield

    print(f'\r{print_line} - {length} bytes [ok]')


def main(directory):

    if not os.path.exists(directory):
        error(f"Directory `{directory}` does not exist.")

    if not os.path.isdir(directory):
        error(f"`{directory}` is not a directory.")

    print(f"Exporting documentation in `{directory}`:\n")

    files = files_to_render()

    files_chars_len = str(len(str(len(files))))
    counter = {
        'files_count': 0,
        'files_chars_len': files_chars_len,
        'files_total_str': ("{:" + files_chars_len + "}").format(len(files)),
    }

    for filename, title, callable, args in files:

        path = os.path.join(directory, filename)

        log_renderer = log_rendering(path, title, counter)
        with log_renderer:

            with open(path, 'w') as file:
                content = str(callable(**args))
                file.write(content)
                log_renderer.gen.send(len(content))

    print(f"\nSuccessfully wrote {counter['files_count']} files to `{directory}`.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        error("`api_doc.export` takes one argument: the directory where to export")

    directory = sys.argv[1]

    if directory in ('-h', '--help'):
        usage()
        exit(0)

    if directory.startswith('-'):
        error(f"No option `{directory}`. Use --help.")

    set_dev_mode(dev_mode=not bool(environ.get('MIXT_DISABLE_DEV_MODE')))

    main(directory)
