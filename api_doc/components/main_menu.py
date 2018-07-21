from mixt.contrib.css import css_vars, render_css, Modes

from .generic import MenuCollector


class MainMenuCollector(MenuCollector):

    # noinspection PyUnresolvedReferences
    @css_vars(globals())
    @classmethod
    def render_css_global(cls, context):
        colors = context.styles.colors

        tagged = tuple(
            f'.menu-{name}'
            for name in [
                'class',
                'module',
                'function-staticmethod',
                'function-property',
                'function-classmethod'
            ]
        )

        return render_css(merge({
            "/*": f"<{cls.__module__}.{cls.__name__}>",
            "#main-menu": {
                background: colors[9],
                color: white,
                "> p": {
                    margin-left: 10*px,
                },
                "ul": {
                    list-style: none,
                    margin-left: 1*em,
                },
                "> ul": {
                    margin: 10*px,
                    padding-right: 15*px,
                },
                "a": {
                    color: inherit,
                    text-decoration: none,
                    line-height: 1.8,
                    display: inline-block,
                    white-space: nowrap,
                },
                "li > a": {
                    display: block,
                }
            },
            tagged: {
                "&:after": merge(
                    context.styles.snippets['TAG'],
                    context.styles.snippets['HL'],
                ),
            },
            "li:not(:hover)": {
                "> .menu-class:after": context.styles.snippets['HL_REVERSE'],
                "> details > summary:not(.current)": {
                    (f"> {t}" for t in tagged): {
                        "&:after": context.styles.snippets['HL_REVERSE']
                    },
                }
            },
            "#main-menu ": {
                "li:hover > details > summary,"
                "li:hover > a,"
                ".current": {
                    color: colors[9],
                    "&:before": {
                        content: str(" "),
                        background: white,
                        position: absolute,
                        height: 1.8*em,
                        z-index: -1,
                        left: 0,
                        right: 0,
                    }
                },

            },
        }, {
            f"{t}:after": {
                content: str(t.split('-')[-1])
            }
            for t in tagged
        }, {
            "/**": f"</{cls.__module__}.{cls.__name__}>"
        }))

    @classmethod
    def render_js_global(cls, context):
        # language=JS
        return """
/* <components.main_menu.MainMenuCollector> */

var MainMenu = {
    menu: null,
    onDocPartEnter: function(ev) {
        var docPart = DocPart.getFor(ev.target);
        var isDetails = Details.matches(docPart);
        var menuEntry = Menu.getItemForId(MainMenu.menu, docPart.id, true, true);
        if (menuEntry) {
            (isDetails ? menuEntry.parentNode : menuEntry).classList.add('current');
        }
    },
    onDocPartLeave: function(ev) {
        var docPart = DocPart.getFor(ev.target);
        var isDetails = Details.matches(docPart);
        var menuEntry = Menu.getItemForId(MainMenu.menu, docPart.id);
        if (menuEntry) {
            (isDetails ? menuEntry.parentNode : menuEntry).classList.remove('current');
        }
    },
    onDocPartToggle: function(ev) {
        var docPart = DocPart.getFor(ev.target);
        var menuEntry = Menu.getItemForId(MainMenu.menu, docPart.id, true);
        if (menuEntry) {
            menuEntry.parentNode.parentNode.open = ev.detail.open;
        }
    },
    init: function() {
        MainMenu.menu = document.getElementById('main-menu');
        document.addEventListener("doc_part_enter", MainMenu.onDocPartEnter);
        document.addEventListener("doc_part_leave", MainMenu.onDocPartLeave);
        document.addEventListener("doc_part_toggle", MainMenu.onDocPartToggle);
    }
};
MainMenu.init();

/* <components.main_menu.MainMenuCollector> */
        """

    def render_menu(self):
        return super().render_menu(id="main-menu")
