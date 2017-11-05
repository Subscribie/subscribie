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
