document.addEventListener('copy', (event) => {
  const container = document.querySelector('#content-copyright');
  const selection = document.getSelection();
  const text = selection.toString();

  if(
    text.length >= 50 && (
      container.contains(selection.anchorNode) ||
      container.contains(selection.focusNode)
    )
  ) {
    event.clipboardData.setData('text/plain', `${text}\nИсточник: ${document.location.href}`);
    event.preventDefault();
  }
});
