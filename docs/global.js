
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
        
/* <components.doc.DocPart> */
var DocPart = {
    getFor: function(node) {
        while (node && node.classList) {
            if (node.classList.contains('doc-part')) {
                return node;
            }
            node = node.parentNode;
        }
        return null;
    },    
    onEnter: function(ev) {
        var docPart = DocPart.getFor(ev.currentTarget);
        docPart.dispatchEvent(new CustomEvent("doc_part_enter", {bubbles: true}));
    },    
    onLeave: function(ev) {
        var docPart = DocPart.getFor(ev.currentTarget);
        docPart.dispatchEvent(new CustomEvent("doc_part_leave", {bubbles: true}));
    },    
    onToggle: function(ev) {
        var docPart = DocPart.getFor(ev.currentTarget);
        docPart.dispatchEvent(new CustomEvent("doc_part_toggle", {bubbles: true, detail: {open: ev.currentTarget.open}}));
    },
    init: function() {
        var docParts = document.querySelectorAll('.doc-part');
        for (var i = 0; i < docParts.length; i++) { 
            var docPart = docParts[i];
            docPart.addEventListener('mouseenter', DocPart.onEnter);  
            docPart.addEventListener('mouseleave', DocPart.onLeave);  
        }
        setTimeout(function() {
            for (var i = 0; i < docParts.length; i++) { 
                var docPart = docParts[i];
                if (Details.matches(docPart)) {
                    docPart.addEventListener('toggle', DocPart.onToggle);
                    var linkedDetails = Details.getLinked(docPart);
                    if (linkedDetails) {
                        linkedDetails.addEventListener('toggle', DocPart.onToggle);
                    }
                } 
            }
        }, 500);
    }
};
DocPart.init();
/* </components.doc.DocPart> */
        
/* <components.generic.details.Details> */
var Details = {
    lastNodeToFocus: null,
    lastNodeToScrollTo: null,
    matches: function(node) {
        return node.matches && node.matches('details');
    },
    getLinked: function(node) {
        var linked = node.querySelector('details.linked-to-parent');
        return (linked && linked.parentNode && linked.parentNode.parentNode && linked.parentNode.parentNode === node) ? linked : null;
    },
    openFor: function(element, parents_only) {
        if (Details.matches(element) && !element.open) {
            if (!parents_only) {
                element.open = true;
                opened = true;
            }
            parents_only = false
        }
        if (element.parentNode) {
            Details.openFor(element.parentNode, parents_only);
        }
    },
    focusNode: function(node) {
        Details.lastNodeToFocus = node;
        setTimeout(function() {
            if (node !== Details.lastNodeToFocus) { return; }
            node.focus();
        }, 100);
    },
    scrollIntoView: function(node) {
        Details.lastNodeToScrollTo = node;
        setTimeout(function() {
            if (node !== Details.lastNodeToScrollTo) { return; }
            scrollIntoView(node, {
                behavior: 'smooth',
                scrollMode: 'if-needed',
                block: 'start',
                inline: 'nearest',
            });
            Details.focusNode(node);
        }, 10);
    },
    onHashChange: function () {
      var hash = location.hash.substring(1);
      if (hash) {
        var node = document.getElementById(hash);
        if (node) {
            Details.openFor(Details.getLinked(node) || node);
            Details.scrollIntoView(node);
        } 
      }
    },
    init: function() {
        window.addEventListener('hashchange', Details.onHashChange);
        if (location.hash) { Details.onHashChange(); }
    }
};
Details.init();
/* </components.generic.details.Details> */
        