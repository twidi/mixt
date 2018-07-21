from contextlib import contextmanager

import pytest

from mixt.contrib.css import render_css
from mixt.contrib.css.loading import CSS_VARS, css_vars, import_css, load_css_keywords

from .test_vars import test_defaults


DEFAULT_CSS_VARS_LEN = 137
LOADED_CSS_VARS_LEN = 4976


def len_css_vars():
    return len([key for key in CSS_VARS if not key.lower().startswith("pytest")])


@contextmanager
def tmp_load_keywords():
    css_vars_copy = CSS_VARS.copy()
    try:
        load_css_keywords()
        yield
    finally:
        load_css_keywords.main_is_done = False
        CSS_VARS.clear()
        CSS_VARS.update(css_vars_copy)


def test_default_css_vars():
    assert len_css_vars() == DEFAULT_CSS_VARS_LEN
    test_defaults()


def test_load_css_keywords():
    with tmp_load_keywords():
        assert len_css_vars() == LOADED_CSS_VARS_LEN
    assert len_css_vars() == DEFAULT_CSS_VARS_LEN


def test_default_still_works_after_loading():
    with tmp_load_keywords():
        test_defaults()


# noinspection PyUnresolvedReferences
def test_import_css():

    #  globals are clean
    with pytest.raises(NameError):
        3 * px

    with import_css(globals()):
        assert b.str(px(3)) == "3px"  # b.str for builtins

    # globals are clearer
    with pytest.raises(NameError):
        3 * px


# noinspection PyUnresolvedReferences
def test_css_vars_decorator():
    with tmp_load_keywords():
        # globals are clean
        with pytest.raises(NameError):
            margin-bottom

        # noinspection PyUnresolvedReferences
        @css_vars(globals())
        def css():
            return {body: {margin-bottom: 3 * px, foo: none}}

        assert (
            render_css(css())
            == """\
body {
  margin-bottom: 3px;
  foo: none;
}
"""
        )
        # foo and Foo where added to CSS_VARS
        assert len_css_vars() == LOADED_CSS_VARS_LEN + 2

        # globals are cleared
        with pytest.raises(NameError):
            margin-bottom
