from .generic import MenuCollector


class MainMenuCollector(MenuCollector):

    @classmethod
    def render_css_global(cls, context):
        # language=CSS
        return """
/* <components.main_menu.MainMenuCollector> */
#main-menu {
    background: %(BG9)s;
    color: white;
}
#main-menu > p {
    margin-left: 10px;
}
#main-menu ul {
    list-style: none;
    margin-left: 1em;
}
#main-menu > ul {
    margin: 10px;
    padding-right: 15px;
}

#main-menu a {
    color: inherit;
    text-decoration: none;
    line-height: 1.8;
    display: inline-block;
}

.menu-class:after, 
.menu-module:after, 
.menu-function-staticmethod:after, 
.menu-function-property:after,
.menu-function-classmethod:after { 
    %(TAG)s
    %(HL)s
}
li:not(:hover) > .menu-class:after,
li:not(:hover) > details > summary:not(.current) > .menu-class:after,
li:not(:hover) > details > summary:not(.current) > .menu-module:after,
li:not(:hover) > details > summary:not(.current) > .menu-function-staticmethod:after, 
li:not(:hover) > details > summary:not(.current) > .menu-function-property:after,
li:not(:hover) > details > summary:not(.current) > .menu-function-classmethod:after {
    %(HL-reverse)s
}

.menu-class:after { 
    content: "class";
}
.menu-module:after { 
    content: "module";
}
li:not(:hover) > details > summary:not(.current) > .menu-function-staticmethod:after, 
li:not(:hover) > details > summary:not(.current) > .menu-function-property:after,
li:not(:hover) > details > summary:not(.current) > .menu-function-classmethod:after {
    %(HL-reverse)s
}

#main-menu li:hover > details > summary,
#main-menu li:hover > a,
#main-menu .current {
    color: %(BG9)s;
}
#main-menu li:hover > details > summary::before,
#main-menu li:hover > a::before,
#main-menu .current::before {
    content: " ";
    background: white;
    position: absolute;
    height: 1.8em;
    z-index: -1;
    left: 0;
    right: 0;
}


.menu-function-staticmethod:after {
    content: "staticmethod";
}
.menu-function-property:after {
    content: "property";
}
.menu-function-classmethod:after {
    content: "classmethod";
}

/* </components.main_menu.MainMenuCollector> */
        """

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
