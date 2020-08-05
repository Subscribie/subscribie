<<<<<<< HEAD
const instant_payment = document.getElementById("instant_payment-0");
const upfront_price = document.getElementById("upfront_price");
const note_to_seller_required = document.getElementById("note_to_seller_required-0");
const message = document.getElementById("message");
const subscription = document.getElementById("subscription-0");
const price = document.getElementById("price");

subscription.addEventListener('click', () => {
  if (subscription.checked == true) {
    price.style.display = 'block'; 
  } else {
    price.style.display = 'none';
  }
});

instant_payment.addEventListener('click', () => {
  if (instant_payment.checked == true) {
      upfront_price.style.display = 'block';
  } else {
      upfront_price.style.display = 'none';
  }
});

note_to_seller_required.addEventListener('click', () => {
  if (note_to_seller_required.checked == true) {
    message.style.display = 'block';
  } else {
    message.style.display = 'none';
  }
});
=======
const check_input = document.querySelectorAll('.toggle');
const extra_fields = document.querySelectorAll('.extra_fields');

check_input.forEach((input, i) => {
  function showExtraFields() {
    if (input.checked == true) {
      extra_fields.item(i).style.display = 'block';
    } else {
      extra_fields.item(i).style.display = 'none';
    }
  }

  showExtraFields(); //show or don't show extra fields when page load

  input.addEventListener('click', () => {
    showExtraFields(); //show or don't show extra fields when checkbox checked or unchecked
  });
});
>>>>>>> upstream/master
