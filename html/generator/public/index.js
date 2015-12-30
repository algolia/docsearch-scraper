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
    $('.status-bar').text('');
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

  $('#start-urls, #stop-urls, .lvl-input > input, #min_indexed_level, #strip_chars').on('change', updateCode);
  $('#start-urls').on('change', function() {
    $('iframe').attr('src', '/proxy?url=' + $('#start-urls').val().split("\n")[0]);
  });

  $('#config').on('change', updateUI); 

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
    var config = readConfigFromUI();
    $('#config').val(JSON.stringify(config, null, 2));
    contentWindow.postMessage({type:'config', config: config}, window.location.href);
  }

  function updateUI() {
    var config = JSON.parse($(this).val());

    $('.levels .lvl0 input').val(config.selectors.lvl0);
    $('.levels .lvl1 input').val(config.selectors.lvl1);
    $('.levels .lvl2 input').val(config.selectors.lvl2);
    $('.levels .lvl3 input').val(config.selectors.lvl3);
    $('.levels .lvl4 input').val(config.selectors.lvl4);
    $('.levels .lvl5 input').val(config.selectors.lvl5);
    $('.levels .lvl6 input').val(config.selectors.lvl6);
    $('.levels .text input').val(config.selectors.text);

    $('#stop-urls').val(config.stop_urls);
    
    var startUrls = config.start_urls;
    $('#start-urls').val(startUrls);
    $('iframe').attr('src', '/proxy?url=' + startUrls[0]);


    $('#min_indexed_level').val(config.min_indexed_level || 0);
    $('#strip_chars').val(config.strip_chars || '');

    //contentWindow.postMessage({type:'config', config: config}, window.location.href);
  }

  function readConfigFromUI() {
    var startUrls = $('#start-urls').val().split("\n").filter(function(e) { return e !== ''; });
    var stopUrls = $('#stop-urls').val().split("\n").filter(function(e) { return e !== ''; });
    var config = {
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
      selectors: {},
      custom_settings: {},
      strategy: "default"
    };
    var minIndexedLevel = +$('#min_indexed_level').val();
    if (minIndexedLevel > 0) {
      config.min_indexed_level = minIndexedLevel;
    }
    var stripChars = $('#strip_chars').val();
    if (stripChars !== '') {
      config.strip_chars = stripChars;
    }
    $.each(['lvl0', 'lvl1', 'lvl2', 'lvl3', 'lvl4', 'lvl5', 'text'], function(i, lvl) {
      var v = $('.levels .' + lvl + ' input').val();
      if (v) {
        config.selectors[lvl] = v;
      }
    });
    return config 
  }
});
