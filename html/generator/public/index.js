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
  $(document).on('click', '.levels .btn', function toggleLevelSelect() {
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

  $(document).on('click', '.levels .fa-times', function clearInput() {
    $(this).siblings('input').val('');
    updateCode();
    contentWindow.postMessage({type:'toggleMode', newMode: 'highlight'}, window.location.href);
  });

  $('#start-urls, #stop-urls, .lvl-input > input').on('change', updateCode);
  $('#start-urls').on('change', function() {
    $('iframe').attr('src', '/proxy?url=' + $('#start-urls').val().split("\n")[0]);
  });

  function onPathClick(path) {
    var selectedLevel = window.currentLevel;
    if (selectedLevel !== undefined) {
      var inputForSelectedLevel = selectedLevel.siblings('input');
      var val = inputForSelectedLevel.val();
      if (val) {
        val += ', ' + path;
      } else {
        val = path;
      }
      inputForSelectedLevel.val(val);
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
      allowed_domains: startUrls.map(function(e) {
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
        lvl0: $('.levels .lvl0 input').val(),
        lvl1: $('.levels .lvl1 input').val(),
        lvl2: $('.levels .lvl2 input').val(),
        lvl3: $('.levels .lvl3 input').val(),
        lvl4: $('.levels .lvl4 input').val(),
        lvl5: $('.levels .lvl5 input').val(),
        text: $('.levels .text input').val()
      },
      custom_settings: {},
      strategy: "default"
    };
    $('#code').text(JSON.stringify(code, null, 2));
    contentWindow.postMessage({type:'config', config: code}, window.location.href);
  }
});
