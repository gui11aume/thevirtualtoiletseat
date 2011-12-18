function postUpdate(action) {

  var request = new XMLHttpRequest();

  request.open("POST", "/update", true);
  request.setRequestHeader("Content-type",
      "application/x-www-form-urlencoded");
  request.setRequestHeader("Content-length", action.length);
  request.setRequestHeader("Connection", "close");

  request.onreadystatechange = function() {
    if (request.readyState === 4 && request.status === 200) {
      document.getElementById("state").innerHTML = request.responseText;
    }
  };

  request.send(action);

}

function get_uid() {
  var cookie_items = document.cookie.split(';');
  for (var i=0 ; i < cookie_items.length ; i++) {
    if (cookie_items[i].match(/^uid=/)) {
      return (cookie_items[i].replace(/uid=/, ''));
    }
  }
}


function ping() {

  var request = new XMLHttpRequest();
  var uid = get_uid();

  request.open("POST", "/ping", true);
  request.setRequestHeader("Content-type",
      "application/x-www-form-urlencoded");
  request.setRequestHeader("Content-length", uid.length);
  request.setRequestHeader("Connection", "close");

  request.send("uid=" + uid);

}



window.onload = function() {
  var keep_pinging = setInterval("ping()", 3000);
}
