(function() {
  var httpRequest;
  document.getElementById("check").addEventListener('submit', makeRequest);

  function makeRequest(e) {
		e.preventDefault();
    httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
      console.log('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }
    httpRequest.onreadystatechange = alertContents;
    httpRequest.open('POST', 'http://localhost:5000');
		httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		var buildingNumber = encodeURIComponent(document.getElementById('buildingnumber').value);
		var PostCode = encodeURIComponent(document.getElementById('PostCode').value);
    httpRequest.send("buildingnumber="+buildingNumber+"&PostCode="+PostCode);
  }

  function alertContents() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        alert(httpRequest.responseText);
      } else {
        console.log('There was a problem with the request.');
      }
    }
  }
})();
