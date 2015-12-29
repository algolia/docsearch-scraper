$(function(){
  var contentIframe = document.querySelector('iframe');
  var contentWindow = contentIframe.contentWindow;

  window.addEventListener('message', function(e){
    var type = e.data.type;
    var selector = e.data.selector;
    if(type === 'select') onPathClick(selector);
    if(type === 'hover') onPathHover(selector);
    if(type === 'pageLoad') updateCode();
  });

  updateCode();

  window.currentLevel = undefined;
  $(document).on('click', '.levels .btn', function() {
    if(window.currentLevel === undefined) {
      window.currentLevel = $(this);
      window.currentLevel.addClass('active');
      contentWindow.postMessage({type:'toggleMode', newMode: 'select'}, window.location.href);
    } else if(!window.currentLevel.is($(this))) {
      window.currentLevel.removeClass('active');
      window.currentLevel = $(this);
      window.currentLevel.addClass('active');
      contentWindow.postMessage({type:'toggleMode', newMode: 'select'}, window.location.href);
    } else { //window.currentLevel === $(this)
      window.currentLevel.removeClass('active');
      window.currentLevel = undefined;
      contentWindow.postMessage({type:'toggleMode', newMode: 'highlight'}, window.location.href);
    }
  });
  $(document).on('click', '.levels .fa-times', function() {
    var b = $(this).parent().find('.btn');
    b.text(b.attr('rel'));
    updateCode();
    contentWindow.postMessage({type:'toggleMode', newMode: 'highlight'}, window.location.href);
  });

  $('#start-urls, #stop-urls').on('change', updateCode);
  $('#start-urls').on('change', function() {
    $('iframe').attr('src', '/proxy?url=' + $('#start-urls').val().split("\n")[0]);
  });

  function onPathClick(path) {
    if (window.currentLevel !== undefined) {
      var val = window.currentLevel.text().substring(6);
      if (val) {
        val += ', ' + path;
      } else {
        val = path;
      }
      window.currentLevel.text(window.currentLevel.attr('rel') + ': ' + val);
      updateCode();
    }
  }

  function onPathHover(path) {
    $('.status-bar').text(path);
  }

  function updateCode() {
    var startUrls = $('#start-urls').val().split("\n").filter(function(e) { return e !== ''; });
    var stopUrls = $('#stop-urls').val().split("\n").filter(function(e) { return e !== ''; });
    var code = {
      index_name: "FIXME",
      allowed_domains: startUrls.map(function(e) {``
                                     var a = document.createElement("a");
                                     a.href = e;
                                     return a.hostname;
      }).reduce(function(arr, e) {
        if (arr.indexOf(e) < 0) arr.push(e);
        return arr;
      }, []),
      start_urls: startUrls,
      stop_urls: stopUrls,
      selectors_exclude: [],
      selectors: {
        lvl0: $('.levels .btn[rel="lvl0"]').text().substring(6),
        lvl1: $('.levels .btn[rel="lvl1"]').text().substring(6),
        lvl2: $('.levels .btn[rel="lvl2"]').text().substring(6),
        lvl3: $('.levels .btn[rel="lvl3"]').text().substring(6),
        lvl4: $('.levels .btn[rel="lvl4"]').text().substring(6),
        lvl5: $('.levels .btn[rel="lvl5"]').text().substring(6),
        text: $('.levels .btn[rel="text"]').text().substring(6)
      },
      custom_settings: {},
      strategy: "default"
    };
    $('#code').text(JSON.stringify(code, null, 2));
    contentWindow.postMessage({type:'config', config: code}, window.location.href);
  }
});
