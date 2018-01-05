if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js', {scope: '/'})
    .then(function(reg) {
      // registration worked
      console.log('Service worker registration succeeded. Scope is ' + reg.scope);
    }).catch(function(error) {
      // registration failed
      console.log('Service worker registration failed with ' + error);
    });
}

document.addEventListener('DOMContentLoaded', function () {

  // Get all "navbar-burger" elements
  var $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  // Check if there are any navbar burgers
  if ($navbarBurgers.length > 0) {

    // Add a click event on each of them
    $navbarBurgers.forEach(function ($el) {
      $el.addEventListener('click', function () {

        // Get the target from the "data-target" attribute
        var target = $el.dataset.target;
        var $target = document.getElementById(target);

        // Toggle the class on both the "navbar-burger" and the "navbar-menu"
        $el.classList.toggle('is-active');
        $target.classList.toggle('is-active');

      });
    });
  }

});

var accordions=document.querySelectorAll(".accordions");accordions&&accordions.forEach(function(c){var a=c.querySelectorAll(".accordion");a&&a.forEach(function(a){a.querySelector(".toggle").addEventListener("click",function(b){b.preventDefault();b=b.target.parentNode.parentNode;if(!b.classList.contains("is-active")){var a=c.querySelector(".accordion.is-active");a&&a.classList.remove("is-active");b.classList.add("is-active")}})})});
