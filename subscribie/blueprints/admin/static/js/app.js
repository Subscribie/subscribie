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
