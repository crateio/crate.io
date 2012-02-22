/**
 * Fayer.js v1.0.4
 *
 * Author : Sandeep Jain
 * Author Webiste: http://www.jsvrocks.com/
 * GitHub: https://github.com/sandeepjain/fayer
 *
 * Copyright 2011, Sandeep Jain
 * Dual licensed under the MIT or GPL Version 2 licenses.
 */
(function(window, undefined) {
    var document = window.document,
        tracker = {
            page : '',
            isInitialized : false
        },
        // Minification variable
        funcTypeStr = 'Function',
        objTypeStr = 'Object';

    // helper functions

    // check if element exists in array
    function inArray(elem, array) {
        if (!isTypeOf('Array', array)) {
            return -1;
        }
        if (array.indexOf) {
            return array.indexOf(elem);
        }
        for (var i = 0, length = array.length; i < length; i++) {
            if (array[i] === elem) {
                return i;
            }
        }
        return -1;
    }

    // reliable check of variable type
    function isTypeOf (type, obj) {
        return obj !== undefined && obj !== null && Object.prototype.toString.call(obj).slice(8, -1) === type;
    }

    function _fayer () {
        var self = this;
        self.init = function (attrib) {
            return self.detectPage(attrib);
        };
        self.detectPage  = function (attrib) {
            var queryFunc = isTypeOf(funcTypeStr, attrib) ?
                attrib :
                function () {
                    // If no attribute specified then default to attribute 'id'
                    attrib = isTypeOf('String', attrib) && attrib !== '' ? attrib : 'id';
                    var val = document.body.getAttribute(attrib);
                    return val === null ?  undefined : val;
                };
            tracker.page = queryFunc() || '';
            tracker.isInitialized = true;
            return self;
        };
        self.on  = function (page, func) {
            if (tracker.isInitialized === false) {
                self.init();
                tracker.isInitialized = true;
            }
            if (isTypeOf(funcTypeStr, page)) {
                // Check if only function is passed as parameter
                page();
            } else if (isTypeOf(objTypeStr, page)) {
                // if argument is an object
                for (var fn in page) {
                    page.hasOwnProperty(fn) && self.on(fn, page[fn]);
                }
            } else if (self.isIn(page) && isTypeOf(funcTypeStr, func)) {
                func();
            }
            return self;
        };
        self.notOn  = function (page, func) {
            // if argument is an object
            if (isTypeOf(objTypeStr, page)) {
                for (var fn in page) {
                    page.hasOwnProperty(fn) && self.notOn(fn, page[fn]);
                }
            } else {
                !self.isIn(page) && self.on(func);
            }
            return self;
        };
        self.is  = function (page) {
            return (page === tracker.page);
        };
        self.isIn  = function (page) {
            return isTypeOf('RegExp', page)
                ? page.test(tracker.page)
                : self.is(page)
                    ? true
                    : inArray(tracker.page, page) !== -1;
        };
    };

    // Expose to global scope
    window.fayer = new _fayer;

})(window);
