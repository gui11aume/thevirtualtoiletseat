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
