document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages');

    // Handle sending messages
    document.getElementById('send-button').addEventListener('click', async () => {
        const inputElement = document.getElementById('message-input');
        const message = inputElement.value;
        inputElement.value = '';

        if (message.trim() === '') return;

        // Sanitize and parse user message
        const sanitizedUserMessage = DOMPurify.sanitize(`You: ${message}`);

        // Display user message
        const userMessageDiv = document.createElement('div');
        userMessageDiv.innerHTML = sanitizedUserMessage;
        messagesContainer.appendChild(userMessageDiv);

        // Send message to server
        try {
            const response = await fetch('/proof_assistant/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // Sanitize and display bot reply
            const sanitizedBotReply = DOMPurify.sanitize(data.reply);

            const botMessageDiv = document.createElement('div');
            botMessageDiv.innerHTML = `Bot: ${sanitizedBotReply}`;
            messagesContainer.appendChild(botMessageDiv);

            // Re-render MathJax for new messages
            MathJax.typeset();
        } catch (error) {
            console.error('Error:', error);
        }

        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
});
