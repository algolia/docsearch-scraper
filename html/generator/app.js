var http = require('http');
var cheerio = require('cheerio');
var express = require('express');
var app = express();
var URL = require('url');

app.use(express.static('public'));

app.get('/proxy', function(req, res) {
  var request = require('request');

  var url = req.query.url;

  // If our URL doesn't contain a protocol or
  // ending slash, add it here
  if (url.indexOf('://') === -1) {
    url = 'http://' + url;
    if (!url.match(/\/$/)) {
      url += '/';
    }
  }

  var page = request.get(url, function(error, response, body) {
    if (!error) {
      var proxied = proxy(body, url);
      res.header('Cache-Control', 'no-cache, private, no-store, must-revalidate, max-stale=0, post-check=0, pre-check=0');
      res.send(proxied);
    }
  });
});

var server = app.listen(3000, function () {
  var host = server.address().address;
  var port = server.address().port;
  console.log('Example app listening at http://%s:%s', host, port);
});

function updateUrl(element, attribute, url, proxify) {
  var val = element.attr(attribute);
  if (val && val.indexOf('/') === 0) {
    var pathname = URL.parse(url).pathname;
    val = url.replace(pathname, '') + val;
  } else {
    var sep = url[url.length - 1] === '/' ? '' : '/';
    val = url + sep + val;
  }
  element.attr(attribute, (proxify ? '/proxy?url=' : '') + val);
}

function proxy(html, url) {
  var $ = cheerio.load(html);

  $('body').append('<script src="https://cdn.jsdelivr.net/jquery/2.1.4/jquery.min.js" type="text/javascript"></script>');
  $('body').append('<script src="http://localhost:3000/selector.js" type="text/javascript"></script>');

  $('a:not([href^="http://"])' +
    ':not([href^="https://"])' +
    ':not([href^="//"])' +
    ':not([href^="javascript:"])')
    .each(function() {
      updateUrl($(this), 'href', url, true);
    });

  $('img:not([src^="http://"])' +
    ':not([src^="https://"])' +
    ':not([src^="//"])')
    .each(function() {
      updateUrl($(this), 'src', url);
    });

  $('link:not([href^="http://"])' +
    ':not([href^="https://"])' +
    ':not([href^="//"])')
    .each(function() {
      updateUrl($(this), 'href', url);
    });

  $('script[src]:not([src^="http://"])' +
    ':not([src^="https://"])' +
    ':not([src^="//"])')
    .each(function() {
      updateUrl($(this), 'src', url);
    });

  return $.html();
};
