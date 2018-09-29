from typing import List

from mixt import Element, h, html
from mixt.internal.base import Props
from mixt.internal.html import HtmlBaseElement, HtmlElementMetaclass


# TODO: at the mixt level, add an official way to pass a tag to use as a base tag
#       and inherits its proptypes


class UIMetaClass(HtmlElementMetaclass):
    # TODO: add all modifiers as bool props default to False
    pass


class UI(HtmlBaseElement, metaclass=UIMetaClass):
    BASE_CLASS: str = ""
    UI_CLASS: bool = True

    def _to_list(self, acc: List):
        # TODO:
        # - extract all given class
        # - start by ui
        # - then all modifiers
        # - then the TAG_CLASS
        # - then the other classess

        if self.UI_CLASS:
            self.prepend_class("ui")
        if self.BASE_CLASS:
            self.append_class(self.BASE_CLASS)
        super()._to_list(acc)

    def _get_attribute_props(self) -> Props:
        return {
            name: value
            for name, value in self.props.items()
            if name in HtmlBaseElement.PropTypes.__types__
        }


class Button(UI, html.Button):
    BASE_CLASS: str = "button"
    MODIFIERS = "basic primary secondary animated vertical fade labeled left".split()

    class Visible(html.Div):
        """

        Examples
        --------
        >>> print(
        ...     <Button animated fade>
        ...         <Button.Visible>Sign-up for a Pro account</Button.Visible>
        ...         <Button.Hidden>$12.99 a month</Button.Hidden>
        ...     </Button>
        ... )
        <button class="ui animated fade button">
            <div class="visible content">Sign-up for a Pro account</div>
            <div class="hidden content">$12.99 a month</div>
        </button>


        """

        __tag__ = "div"

        class PropTypes:
            _class: str = "visible content"

    class Hidden(html.Div):
        """
        For the example, see ``Button.Visible``

        """

        __tag__ = "div"

        class PropTypes:
            _class: str = "hidden content"

    class Or(Element):
        """

        Examples
        --------
        <Buttons>
            <Button>Cancel</Button>
            <Button.Or />
            <Button positive>Save</Button>
        </Buttons>

        """

        class PropTypes:
            text: str = "or"

        def render(self, context):
            return h.Div(_class="or", data_text=self.text)()
