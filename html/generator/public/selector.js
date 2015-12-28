"use strict";

var SELECTOR = 'h1, h2, h3, h4, h5, td, p, ul, ol, li, blockquote, div, span';

document.write('<style>.algolia-hover { border: 1px solid red !important; cursor: pointer; }</style>');

$(document).on('mouseenter', SELECTOR, function() {
  $(this).addClass('algolia-hover');
  var selector = cssPath(this).join(' ');
  window.parent.onPathHover(selector);
});

$(document).on('mouseout', SELECTOR, function() {
  $(this).removeClass('algolia-hover');
});

$(document).on('click', SELECTOR, function() {
  var selector = cssPath(this).join(' ');
  if(window.parent.currentLevel !== undefined) {
    window.parent.onPathClick(selector);
    return false;
  }
});

function cssPath(el, path) {
  path = path || [];
  if (!el || getNodeName(el) === 'html') return path;

  if (el.id && path.length > 0) {
    path.unshift('#' + el.id);
    return path;
  }
  var classes = getClassSelector(el);
  var node = getNodeName(el);
  if (classes) {
    var elSelector = node + classes;
    path.unshift(elSelector);
  } else if (path.length === 0) {
    path.push(node);
  }
  return cssPath(el.parentNode, path);
}

function getClassSelector(el) {
  return el.className && el.className.split(' ')
    .filter(function(className) { return className !== 'algolia-hover' })
    .map(function(className) { return '.' + className })
    .join('');
}

function getNodeName(el) {
  return (el.nodeName).toLowerCase();
}
