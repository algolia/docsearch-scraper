var http = require('http');
var phantom = require('phantom');
var phantom_params = {
  'web-security': 'no',
};

phantom.create({parameters: phantom_params}, function(ph) {
  http.createServer(function(request, response) {
    ph.createPage(function(page) {
      request.on('data', function(data) {

        var post = JSON.parse(data);
        var url = post['url'];
        var js_wait = post['js_wait'];
        console.log("> PhantomJS: " + url + " (js_wait=" + js_wait + "s)");

        page.set('loadImages', false);
        page.open(url, function (status) {
          setTimeout(function() {
            page.evaluate(function() {
              return document.documentElement.innerHTML;
            }, function(result) {
              response.writeHead(200, {'original_url': url});
              response.end(result);
            });
          }, js_wait * 1000);
        });

      });
    });
  }).listen(8090);
});
