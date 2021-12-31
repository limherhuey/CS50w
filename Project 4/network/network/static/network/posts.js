
document.addEventListener('DOMContentLoaded', function() {

  // send new post information to views.py and prevent default submission of form
  document.querySelector('#submit-post').addEventListener('click', (event) => {
    event.preventDefault();
    create_post();
  });
});


function create_post() {

  // POST to new_post view
  fetch('/posts', {
    method: 'POST',
    body: JSON.stringify({
      body: document.querySelector('#post-body').value
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result['error']) {
      // if there is an error, print it
      console.log("Error: " + result['error']);
    } else {
      // or print result
      console.log(result['message']);

      // refresh the page
      location.reload(true);
    }
  });
}
