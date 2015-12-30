"use strict";

var parentWindow = window.parent;

var currentMode = 'highlight';
window.addEventListener('message', function(e) {
  var data = e.data;
  var messageType = data.type;
  if(messageType === 'toggleMode') {
    currentMode = data.newMode;
    if(currentMode === 'highlight') {
      updateHighlight(getConfig());
    }
    else {
      removeHighlight();
    }
  }
  else if(messageType === 'config' ) {
    updateConfig(data.config);
    if(currentMode === 'highlight') {
      updateHighlight(getConfig());
    }
  }
});
parentWindow.postMessage({type: 'pageLoad'}, window.location.href);

var SELECTOR = 'h1, h2, h3, h4, h5, td, p, ul, ol, li, blockquote, div, span';

document.write('<style>.algolia-hover { outline: 1px solid red !important; cursor: pointer; }</style>');



$(document).on('mouseover', SELECTOR, function() {
  if(currentMode!=='select') return;
  $(this).addClass('algolia-hover');
  var selector = cssPath(this).join(' ');
  //window.parent.onPathHover(selector);
  parentWindow.postMessage({type: 'hover', selector: selector}, window.location.href);
});

$(document).on('mouseout', SELECTOR, function() {
  $(this).removeClass('algolia-hover');
});

$(document).on('click', SELECTOR, function() {
  if(currentMode!=='select') return;
  var selector = cssPath(this).join(' ');
  if(window.parent.currentLevel !== undefined) {
    //window.parent.onPathClick(selector);
    parentWindow.postMessage({type:'select', selector: selector}, window.location.href);
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

var colors = [ // From d3.scale.category10()
  '#1f77b4',
  '#ff7f0e',
  '#2ca02c',
  '#d62728',
  '#9467bd',
  '#8c564b',
  '#e377c2',
  '#7f7f7f',
  '#bcbd22',
  '#17becf'
];
function updateHighlight(config) {
  removeHighlight();
  var style = addHighlight();
  var sheet = style.sheet;
  Object.keys(config.selectors).forEach(function(id){
    var i = (parseFloat(id.substr(3)) + 1) || 0;
    var selector = config.selectors[id];
    if(selector === '') return;
    var position = sheet.rules ? sheet.rules.length : 0;
    var rule = selector + ' {background-color:' + colors[i] + '!important } ';
    sheet.insertRule(rule, position);
  });
}

function addHighlight(){
  var style = document.createElement('style');
  style.id = 'custom-highlight';
  document.body.appendChild(style);
  return style;
}

function removeHighlight(){
  var style = document.querySelector('style#custom-highlight');
  if(style) style.parentNode.removeChild(style);
}

var currentConfig = {};
function updateConfig(newConfig) {
  currentConfig = newConfig;
}

function getConfig() {
  return currentConfig;
}
