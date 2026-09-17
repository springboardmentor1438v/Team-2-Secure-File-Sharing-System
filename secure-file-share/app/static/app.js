document.addEventListener('click', function (event) {
  var button = event.target.closest('#copy');
  if (!button) return;
  navigator.clipboard.writeText(button.dataset.link).then(function () {
    button.textContent = 'Copied';
    setTimeout(function () { button.textContent = 'Copy'; }, 2000);
  });
});
