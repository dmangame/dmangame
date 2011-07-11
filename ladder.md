---
title: ladder
layout: default
---

<script>
  function hide_loading() {
    var el = document.getElementById('ladder_loading');
    el.style.visibility = 'hidden';
    el.style.height = '0px';
  };
</script>
<div id="ladder_loading">
  loading appengine... it might be a while
</div>
<iframe class="clearfix" style="height:100%; width:1000px; border: 0px; overflow_ hidden" src="http://dmangame-app.appspot.com/ladder" onload="hide_loading()">
</iframe>
