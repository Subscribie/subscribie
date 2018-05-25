function postCharge(token) {
  // Insert the token ID into the form so it gets submitted to the server
  var form = document.getElementById('payment-form');
  var hiddenInput = document.createElement('input');
  hiddenInput.setAttribute('type', 'hidden');
  hiddenInput.setAttribute('name', 'token');
  hiddenInput.setAttribute('value', token.id);
  form.appendChild(hiddenInput);

  //also insert the selected package as
  var selectedPackage = document.createElement('input');
  selectedPackage.setAttribute('type', 'hidden');
  selectedPackage.setAttribute('name', 'package');
  selectedPackage.setAttribute('value', document.getElementById('package').value);
  form.appendChild(selectedPackage);

  // Submit the form
  form.submit();
}

// Get stripe public key
httpRequest = new XMLHttpRequest();
httpRequest.onreadystatechange = function() {
    if (httpRequest.readyState === XMLHttpRequest.DONE && httpRequest.status === 200) {
        stripeInit(httpRequest.responseText)
    } 
}
var noCache = ((/\?/).test() ? "&" : "?") + (new Date()).getTime();
httpRequest.open('GET', '/static/js_env/STRIPE_PUBLIC_KEY.env' + noCache);
httpRequest.send();

// Create a Stripe client
function stripeInit(stripe_public_key) {
    var stripe = Stripe(stripe_public_key);

    // Create an instance of Elements
    var elements = stripe.elements();

    // Create an instance of the card Element
    var card = elements.create('card', {style: style});

    // Add an instance of the card Element into the `card-element` <div>
    card.mount('#card-element');

    // Handle real-time validation errors from the card Element.
    card.addEventListener('change', function(event) {
      var displayError = document.getElementById('card-errors');
      if (event.error) {
        displayError.textContent = event.error.message;
      } else {
        displayError.textContent = '';
      }
    });
    // Handle form submission
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function(event) {
      event.preventDefault();

      stripe.createToken(card).then(function(result) {
        if (result.error) {
          // Inform the user if there was an error
          var errorElement = document.getElementById('card-errors');
          errorElement.textContent = result.error.message;
        } else {
          //POST the token to server
          //console.log(postCharge({"token": result.token}));
          console.log("TOKEN ID: " + result.token.id);
          postCharge(result.token);
        }
      });
    });
}

// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
var style = {
  base: {
    color: '#32325d',
    lineHeight: '18px',
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '16px',
    '::placeholder': {
      color: '#aab7c4'
    }
  },
  invalid: {
    color: '#fa755a',
    iconColor: '#fa755a'
  }
};


