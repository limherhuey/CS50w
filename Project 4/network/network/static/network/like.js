
document.addEventListener('DOMContentLoaded', function() {

  // when any post's like button is clicked
  document.querySelectorAll('.like-post').forEach(function (element) {
    element.addEventListener('click', (event) => {

      // prevent form from submitting through HTML by default
      event.preventDefault();

      // get ID of post and action then pass to function
      const postID = element.dataset.postId;
      const action = element.dataset.action;
      like_post(postID, action);
    });
  });

  document.querySelectorAll('.like-post').forEach(function (element) {

    // get post ID and pass to function
    const postID = element.dataset.postId;
    liked = load_like_button(postID);
  })
})


async function load_like_button(postID) {

  // call liked view which returns whether the post is liked by current logged-in user
  let response = await fetch(`/liked/${postID}`);
  const data = await response.json();

  // load button as Like or Unlike accordingly
  let button = document.getElementById(`like-${postID}`);
  if (data["liked"]) {
    button.value = "Unlike";
    button.dataset.action = "unlike";
  } else {
    button.value = "Like";
    button.dataset.action = "like";
  }
}

function like_post(postID, action) {
  
  // call like_post view to like or unlike the post (depending on action)
  fetch(`/like/${postID}`, {
    method: 'POST',
    body: JSON.stringify({
      action: `${action}`
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result['error']) {
      // log error
      console.log("Error: " + result['error']);
    } else {
      // log result
      console.log(result["message"]);

      // update likes on page
      update_likes(postID, result["likes"]);
    }
  });
}

function update_likes(postID, likes) {

  // update like count of post and like button
  document.getElementById(`likes-${postID}`).innerHTML = likes + " Likes";
  load_like_button(postID);
}
