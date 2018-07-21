# coding: mixt

from typing import List, Optional
from mixt import Element, Required, html
from mixt.contrib.css import css_vars, CssDict


class H(Element):
    class PropTypes(html.H.PropTypes):
        _class: str = 'h'
        menu: Optional[str]
        menu_link: str
        menu_class: str

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        _focus = "&:hover, &:focus, &.focus-within"

        return CssDict({
            "/*": f"<{cls.__module__}.{cls.__name__}>",
            ".h": {
                "+ .permalink": {
                    visibility: hidden,
                    padding-left: 0.5*em,
                    vertical-align: middle,
                    line-height: 0.8,
                    color: '#333',
                    opacity: 0.75,
                    _focus: {
                        visibility: visible,
                    }
                },
                _focus: {
                    "+ .permalink": {
                        visibility: visible,
                    },
                },
            },
            div: {
                _focus: {
                    "> .h + .permalink": {
                        visibility: visible,
                    }
                }
            },
            details: {
                _focus: {
                    "> summary > .h + .permalink": {
                        visibility: visible,
                    }
                }
            },
            "/**": f"</{cls.__module__}.{cls.__name__}>",
        })

    def render(self, context):
        props = dict(self.props)
        props.pop('menu', None)
        props.pop('menu_class', None)
        menu_link = props.pop('menu_link', None)
        h = <h {**props}>{self.children()}</h>
        if menu_link:
            return [
                h,
                <a class="permalink" href={menu_link} title="Permalink to here">¶</a>
            ]
        return h


class Item:

    class InvalidLevel(Exception):
        def __init__(self, element, last):
            min = last.root_level
            max = last.element.level + 1 if last.element else min
            super().__init__(
                f'<H level={element.level} menu-link="{element.menu_link}" menu="{element.menu}" menu-class="{element.prop("menu-class")}"/>: level expected to be between {min} and {max} (included).'
            )

    def __init__(self, element, parent):
        self.element = element
        self.parent = parent
        self.children = []

    @property
    def root_level(self):
        if not self.parent:
            return self.children[0].element.level
        return self.parent.root_level

    @property
    def text(self):
        return self.element.menu if self.element else 'Table of content'

    def _add_children(self, element):
        item = Item(element, self)
        self.children.append(item)
        return item

    def add(self, element):

        if not self.parent:
            if self.children and element.level != self.root_level:
                raise self.InvalidLevel(element, self)
            return self._add_children(element)

        if element.level == self.element.level + 1:
            return self._add_children(element)

        if element.level <= self.element.level:
            return self.parent.add(element)

        raise self.InvalidLevel(element, self)


class MenuCollector(Element):

    def __init__(self, **kwargs):
        self.__root__ = Item(None, None)
        self.__last__ = self.__root__
        super().__init__(**kwargs)

    def postrender_child_element(self, child, child_element, context):
        if isinstance(child, H) and child.prop('menu', None):
            if not child.has_prop('menu_link'):
                raise Exception(f'<H level={child.level} menu="{child.menu}" menu-class="{child.prop("menu-class")}"/>: must have a link')
            self.__last__ = self.__last__.add(child)

    def render_menu(self, id, _class=None):
        if self.__root__.children:
            return <Menu id={id} class={_class or ''} menu={self.__root__} />

    @classmethod
    def render_js_global(cls, context):
        # language=JS
        return """
/* <components.generic.menu.MenuCollector> */
var Menu = {
    lastNodeToScrollTo: null,
    scrollIntoView: function(menu, menu_entry) {
        Menu.lastNodeToScrollTo = menu_entry;
        setTimeout(function() {
            if (menu_entry !== Menu.lastNodeToScrollTo) { return; }
            scrollIntoView(menu_entry, {
                behavior: 'smooth',
                scrollMode: 'if-needed',
                block: 'center',
                inline: 'nearest',
            });
            setTimeout(function() {
                menu.scrollLeft = 0;
            }, 500);
        }, 10);
    },
    getItemForId: function(menu, id, open, open_parents_only) {
        var menu_entry = menu.querySelector('a[href="#' + id + '"]');
        if (menu_entry && open) {
            Details.openFor(menu_entry, open_parents_only && menu_entry.parentNode.matches('summary'));
            Menu.scrollIntoView(menu, menu_entry);
        }
        return menu_entry;
    },
    onItemClick: function(ev) {
        if (ev.target.matches('a')) {
            var parent = ev.target.parentNode;
            if (parent.matches('summary')) {
                parent.parentNode.open = !parent.parentNode.open;
            }
            var href = ev.target.getAttribute('href');
            if (href.charAt(0) !== '#') {
                return;
            }
            var node = document.getElementById(href.substring(1));
            if (!node) {
                return;
            }
            ev.stopPropagation();
            ev.preventDefault();
    
            history.pushState(null, null, href);
            window.dispatchEvent(new HashChangeEvent("hashchange"))
        }
    },
    init: function() {
        var menus = document.querySelectorAll('nav.menu');
        for (var i = 0; i < menus.length; i++) { 
            menus[i].addEventListener('click', Menu.onItemClick);  
        }
    }
};
Menu.init();
/* </components.generic.menu.MenuCollector> */
        """


class MenuItem(Element):
    class PropTypes:
        item: Required[Item]

    def render(self, context):
        item = self.item

        link = <a href='{item.element.menu_link}' class="{item.element.prop("menu-class", "")}">{item.text}</a>

        if item.children:
            return <li>
                <details>
                    <summary>{link}</summary>
                    {<MenuItems items={item.children} />}
                </details>
            </li>

        return <li>{link}</li>


class MenuItems(Element):
    class PropTypes:
        items: Required[List[Item]]

    def render(self, context):
        return <ul>
            {[
                <MenuItem item={item} />
                for item in self.items
            ]}
        </ul>


class Menu(Element):
    class PropTypes:
        menu: Required[Item]

    def render(self, context):
        menu = self.menu
        return <nav id={self.id} class="menu">
            <p><a href='#top'>{menu.text}</a></p>
            <MenuItems items={menu.children} />
        </nav>
