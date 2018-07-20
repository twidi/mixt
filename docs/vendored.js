
/* <components.script.VendoredScripts> */
// "focus-within" polyfill: https://gist.github.com/aFarkas/a7e0d85450f323d5e164
(function(window, document){
    'use strict';
    var slice = [].slice;
    var removeClass = function(elem){
        elem.classList.remove('focus-within');
    };
    var update = (function(){
        var running, last;
        var action = function(){
            var element = document.activeElement;
            running = false;
            if(last !== element){
                last = element;
                slice.call(document.getElementsByClassName('focus-within')).forEach(removeClass);
                while(element && element.classList){
                    element.classList.add('focus-within');
                    element = element.parentNode;
                }
            }
        };
        return function(){
            if(!running){
                requestAnimationFrame(action);
                running = true;
            }
        };
    })();
    document.addEventListener('focus', update, true);
    document.addEventListener('blur', update, true);
    update();
})(window, document);

// "scrollIntoView" only if needed: https://github.com/stipsan/scroll-into-view-if-needed
!function(t,e){"object"==typeof exports&&"undefined"!=typeof module?module.exports=e():"function"==typeof define&&define.amd?define(e):t.scrollIntoView=e()}(this,function(){"use strict";var t,e=function(){return t||(t="CSS1Compat"===document.compatMode?document.documentElement:document.scrollingElement||document.documentElement),t},o=function(t){return null!=t&&"object"==typeof t&&(1===t.nodeType||11===t.nodeType)},i=function(t,e){return"X"===e?t.clientWidth<t.scrollWidth:t.clientHeight<t.scrollHeight},n=function(t,e,o){var i=getComputedStyle(t,null)["overflow"+e];return(!o||"hidden"!==i)&&("visible"!==i&&"clip"!==i)},r=function(t,o){return t===e()||i(t,"Y")&&n(t,"Y",o)||i(t,"X")&&n(t,"X",o)},l=function(t,e,o,i,n,r,l,f){return r<t&&l>e||r>t&&l<e?0:r<t&&f<o||l>e&&f>o?r-t-i:l>e&&f<o||r<t&&f>o?l-e+n:0},f=function(t,i){void 0===i&&(i={});var n=i,f=n.scrollMode,c=void 0===f?"always":f,d=n.block,s=void 0===d?"center":d,u=n.inline,h=void 0===u?"nearest":u,a=n.boundary,p=n.skipOverflowHiddenElements,v=void 0!==p&&p,w="function"==typeof a?a:function(t){return t!==a};if(!o(t))throw new Error("Element is required in scrollIntoView");for(var m,g=t.getBoundingClientRect(),b=[];o(m=t.parentNode||t.host)&&w(t);)r(m,v)&&b.push(m),t=m;var y,T,L=e(),M=window.visualViewport?window.visualViewport.width:Math.min(L.clientWidth,window.innerWidth),H=window.visualViewport?window.visualViewport.height:Math.min(L.clientHeight,window.innerHeight),W=window.scrollX||window.pageXOffset,C=window.scrollY||window.pageYOffset;if("if-needed"===c&&b.every(function(t){var e=t.getBoundingClientRect();if(g.top<e.top)return!1;if(g.bottom>e.bottom)return!1;if(t===L){if(g.bottom>H||g.top<0)return!1;if(g.left>M||g.right<0)return!1}return!0}))return[];return b.map(function(t){var e=t.getBoundingClientRect(),o=getComputedStyle(t),i=parseInt(o.borderLeftWidth,10),n=parseInt(o.borderTopWidth,10),r=parseInt(o.borderRightWidth,10),f=parseInt(o.borderBottomWidth,10),c=0,d=0;if("start"===s)if(y||(y=g.top),L===t)c=C+y;else{var u=Math.min(y-e.top,t.scrollHeight-t.clientHeight-t.scrollTop);c=t.scrollTop+u-n}if("center"===s)if(y||(y=g.top+g.height/2),L===t)c=C+y-H/2;else{var a=0-Math.min(e.top+e.height/2-y,t.scrollTop);c=t.scrollTop+a}if("end"===s)if(y||(y=g.bottom),L===t)c=C+y-H;else{var p=0-Math.min(e.bottom-y,t.scrollTop);c=t.scrollTop+p+f}if("nearest"===s)if(y||(y=g.top),L===t){var v=l(C,C+H,H,n,f,C+y,C+y+g.height,g.height);c=C+v}else{var w=l(e.top,e.bottom,e.height,n,f,y,y+g.height,g.height);c=t.scrollTop+w}if("start"===h)if(T||(T=g.left),L===t)d=W+T;else{var m=Math.min(T-e.left,t.scrollHeight-t.clientLeft-t.scrollLeft);d=t.scrollLeft+m-i}if("center"===h)if(T||(T=g.left+g.width/2),L===t)d=W+T-M/2;else{var b=0-Math.min(e.left+e.width/2-T,t.scrollLeft);d=t.scrollLeft+b}if("end"===h)if(T||(T=g.right),L===t)d=W+T-M;else{var E=0-Math.min(e.right-T,t.scrollLeft);d=t.scrollLeft+E+r}if("nearest"===h)if(T||(T=g.left),L===t){var k=l(W,W+M,M,i,r,W+T,W+T+g.width,g.width);d=W+k}else{var I=l(e.left,e.right,e.width,i,r,T,T+g.width,g.width);d=t.scrollLeft+I}return y+=t.scrollTop-c,T+=t.scrollLeft-d,{el:t,top:c,left:d}})},c=function(t){return"function"==typeof t},d=function(t){return t===Object(t)&&0!==Object.keys(t).length},s=function(t,o){void 0===o&&(o="auto");var i=e(),n="scrollBehavior"in i.style;t.forEach(function(t){var e=t.el,r=t.top,l=t.left;e.scroll&&n?e.scroll({top:r,left:l,behavior:o}):e===i?window.scrollTo(l,r):(e.scrollTop=r,e.scrollLeft=l)})},u=function(t){return void 0===t&&(t=!0),!0===t||null===t?{block:"start",inline:"nearest"}:!1===t?{block:"end",inline:"nearest"}:d(t)?t:{block:"start",inline:"nearest"}};return function(t,e){if(void 0===e&&(e=!0),d(e)&&c(e.behavior))return e.behavior(f(t,e));var o=u(e);return s(f(t,o),o.behavior)}});
/* </components.script.VendoredScripts> */
