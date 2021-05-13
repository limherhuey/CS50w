

document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // send mail & prevent form from submitting through HTML (default); any order is alright
  document.querySelector('#send-email').addEventListener('click', () => {
    send_mail();
    event.preventDefault();
  });

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#content-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#content-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // get all emails within the relevant mailbox, ordered by timestamp
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {

    // add information of each email into its own div, then add the div to emails-view
    emails.forEach(email => {
      const div = document.createElement('div');
      div.classList.add("email-div");
      if (email.read) {
        // grey background for read emails
        div.classList.add("email-read");
      }
      div.innerHTML = `<span class="sender">${email.sender}</span>
        <span>${email.subject}</span>
        <span class="timestamp">${email.timestamp}</span>`;

      // view contents of an email when clicked on
      div.addEventListener('click', () => view_email(email.id, mailbox));
      document.querySelector('#emails-view').append(div);
    });
  });
}

function send_mail() {

  // send email via POST (compose function in views.py)
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value,
      next: 'sent'
    })
  })
  .then(response => response.json())
  .then(result => {
    // print result
    console.log(result);
  });

  // load the 'Sent' mailbox
  load_mailbox('sent');
}

function view_email(email_id, mailbox) {

  // show content view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#content-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // clear out contents of previous email
  document.querySelector('#content-view').innerHTML = '';

  // get information about email to display on page
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {

    // create 4 divs for sender, recipients, subject, and timestamp
    let div = []
    for (let i = 0; i < 4; i++) {
      div[i] = document.createElement('div');
    }

    // sender, subject, and timestamp
    div[0].innerHTML = `<strong>From:</strong> ${email.sender}`;    
    div[2].innerHTML = `<strong>Subject:</strong> ${email.subject}`;
    div[3].innerHTML = `<strong>Timestamp:</strong> ${email.timestamp}`;

    // add all recipients to a string for its div
    let recps = "<strong>To:</strong>";
    email.recipients.forEach((recipient, index, array) => {
      if (Object.is(array.length - 1, index)) {
        recps += ` ${recipient}`;
      } else {
        recps += ` ${recipient},`;
      }
    });
    div[1].innerHTML = recps;

    // append all 4 divs to their content view
    for (let i = 0; i < 4; i++) {
      document.querySelector('#content-view').append(div[i]);
    }

    // reply button
    const reply_button = document.createElement('button');
    reply_button.innerHTML = "Reply";
    reply_button.classList.add("btn", "btn-sm", "btn-outline-primary", "action");
    reply_button.id = "reply"
    reply_button.addEventListener('click', () => reply_email(email.sender, email.subject, email.body, email.timestamp));
    document.querySelector('#content-view').append(reply_button);

    // archive button
    if (mailbox === 'inbox') {
      const archive_button = document.createElement('button');
      archive_button.innerHTML = "Archive";
      archive_button.classList.add("btn", "btn-sm", "btn-outline-primary", "action");
      archive_button.addEventListener('click', () => {
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: true
          })
        });
        load_mailbox('inbox');
      });
      document.querySelector('#content-view').append(archive_button);
    }
    // unarchive button
    else if (mailbox === 'archive') {
      const unarchive_button = document.createElement('button');
      unarchive_button.innerHTML = "Unarchive";
      unarchive_button.classList.add("btn", "btn-sm", "btn-outline-primary", "action");
      unarchive_button.addEventListener('click', () => {
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: false
          })
        });
        load_mailbox('inbox');
      });
      document.querySelector('#content-view').append(unarchive_button);
    }

    // section line
    const hr = document.createElement('hr');
    document.querySelector('#content-view').append(hr);
      
    // convert all newline in email body to appropriate html format
    const newline = /\n/g;
    let body = email.body.replace(newline, '<br>');

    // append converted email body to html
    const cont_div = document.createElement('div');
    cont_div.innerHTML = `${body}`;
    document.querySelector('#content-view').append(cont_div);
  });

  // mark email as read
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  });
}

function reply_email(sender, subject, body, timestamp) {
  // show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#content-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // pre-fill composition form
  document.querySelector('#compose-recipients').value = `${sender}`;
  if (subject.substring(0, 4) === 'Re: ') {
    // don't add 'Re: ' again if subject already begins with it
    document.querySelector('#compose-subject').value = `${subject}`;
  } else {
    document.querySelector('#compose-subject').value = `Re: ${subject}`;
  }
  document.querySelector('#compose-body').value = `On ${timestamp} ${sender} wrote: ${body}`;
}