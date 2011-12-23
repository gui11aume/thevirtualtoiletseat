function postUpdate(action) {
// Send user action (button click) to the sever.
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

function get_uid_from_cookie() {
// Parse the cookie and get the uid attribute from it.
  var cookie_items = document.cookie.split(';');
  // Split on ";", find "uid" and parse the value.
  for (var i=0 ; i < cookie_items.length ; i++) {
    if (cookie_items[i].match(/^\s*uid=/)) {
      return (cookie_items[i].replace(/^\s*uid=/, ''));
    }
  }

}


function ping() {
// Ping the server with AJAX.
  var request = new XMLHttpRequest();
  var uid = get_uid_from_cookie();
  request.open("POST", "/ping", true);
  request.setRequestHeader("Content-type",
      "application/x-www-form-urlencoded");
  request.setRequestHeader("Content-length", uid.length);
  request.setRequestHeader("Connection", "close");

  request.onreadystatechange = function() {
    if (request.readyState === 4 && request.status === 200) {
      document.getElementById("ajax").innerHTML = request.responseText;
    }
  };

  request.send("uid=" + uid);

}


window.onload = function() {
// Let it ping!!
  ping();
  var keep_pinging = setInterval("ping()", 3000);
}
