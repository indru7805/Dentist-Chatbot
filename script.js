// Send message to Flask
async function sendMessage() {
  let message = document.getElementById("message").value; // Get user's message

  let chat = document.getElementById("chatBox"); // Select chat box

  chat.innerHTML += "<p><b>You:</b> " + message + "</p>"; // Display user's message

  let response = await fetch("/chat", {
    // Send request to Flask

    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      message: message,
    }),
  });

  let data = await response.json(); // Convert response into object

  chat.innerHTML += "<p><b>Bot:</b> " + data.reply + "</p>"; // Display AI reply

  document.getElementById("message").value = ""; // Clear input box
}
