function copyToClipboard(text) {
  // Create a new textarea element and give it the text to be copied
  const elem = document.createElement('textarea');
  elem.value = text;
  // Append it to the body
  document.body.appendChild(elem);
  // Select the text
  elem.select();
  // Execute the copy command
  document.execCommand('copy');
  // Remove the textarea element from the document
  document.body.removeChild(elem);
  // Show a message that the text was copied
  showMessage('Copied to clipboard!');
}

function showMessage(message) {
  // Create a message element
  const messageElem = document.createElement('div');
  messageElem.textContent = message;
  // Style the message element
  messageElem.style.position = 'fixed';
  messageElem.style.bottom = '20px';
  messageElem.style.left = '50%';
  messageElem.style.transform = 'translateX(-50%)';
  messageElem.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
  messageElem.style.color = 'white';
  messageElem.style.padding = '10px';
  messageElem.style.borderRadius = '5px';
  messageElem.style.zIndex = '1000';
  messageElem.style.transition = 'opacity 0.5s';
  // Append the message element to the body
  document.body.appendChild(messageElem);
  // Remove the message after some time
  setTimeout(() => {
    messageElem.style.opacity = '0';
    setTimeout(() => {
      document.body.removeChild(messageElem);
    }, 500); // Wait for the fade out to finish before removing the element
  }, 2000); // Show the message for 2 seconds
}
