
document.addEventListener('DOMContentLoaded', function() {

  // when any edit post button is clicked
  document.querySelectorAll('#edit-post').forEach(function (element) {
    element.addEventListener('click', (event) => {

      // prevent form from submitting through HTML (default); can put it in any order
      event.preventDefault();

      // get ID of post to be edited and pass to function
      const postID = element.dataset.postId;
      edit_view(postID);
    });
  });

  // when any submit edit post button is clicked
  document.querySelectorAll('#submit-edit').forEach(function (element) {
    element.addEventListener('click', (event) => {

      // prevent form from submitting through HTML (default); can put it in any order
      event.preventDefault();

      // get ID of post to be edited and pass to function
      const postID = element.dataset.postId;
      submit_edit(postID);
    });
  });

  // initial state: edit form is hidden
  load_initial_edit();
});


function load_initial_edit() {
  document.querySelectorAll('.submit-edit').forEach(function(element) {
    element.style.display = 'none';
  });
}

function edit_view(postID) {
  // hide edit button and content, show textarea with content and a save button
  document.querySelector(`#edit-${postID}`).style.display = 'none';
  document.querySelector(`#content-${postID}`).style.display = 'none';
  document.querySelector(`#submit-edit-${postID}`).style.display = 'block';
}

function edited_view(postID, new_content) {
  // change post content to reflect edit
  document.querySelector(`#content-${postID}`).innerHTML = new_content;

  // show edit button and content, hide textarea with content and a save button
  document.querySelector(`#edit-${postID}`).style.display = 'block';
  document.querySelector(`#content-${postID}`).style.display = 'block';
  document.querySelector(`#submit-edit-${postID}`).style.display = 'none';
}

function submit_edit(postID) {
  const new_content = document.querySelector(`#edited-body-${postID}`).value;

  // POST to edit_post view
  fetch(`/edit/${postID}`, {
    method: 'POST',
    body: JSON.stringify({
      body: new_content
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result['error']) {
      // log if there is an error
      console.log("Error: " + result["error"]);
    } else {
      // or print result
      console.log(result["message"]);

      // load the post-edit view
      edited_view(postID, new_content);
    }
  });
}
